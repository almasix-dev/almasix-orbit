/**
 * Validate the plugin marketplace registry before the docs build.
 *
 * Checks what the Astro schema cannot: cross-file references, filename/slug
 * agreement, reserved slugs, and whether local images actually ship.
 *
 *   npm run validate:marketplace
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';

const root = path.resolve(fileURLToPath(import.meta.url), '../..');
const registry = path.join(root, 'src/data/marketplace');
const publicDir = path.join(root, 'public');

const RESERVED_SLUGS = new Set([
	'authors',
	'develop',
	'get-listed',
	'guidelines',
	'overview',
	'paid-vs-free',
]);
const SLUG = /^[a-z0-9-]+$/;
const CURRENCY = /^[A-Z]{3}$/;

const errors = [];

function fail(file, message) {
	errors.push(`${path.relative(root, file)}: ${message}`);
}

function read(file) {
	try {
		return parse(readFileSync(file, 'utf8'));
	} catch (error) {
		fail(file, `invalid YAML — ${error.message}`);
		return null;
	}
}

function listYaml(dir) {
	if (!existsSync(dir)) return [];
	return readdirSync(dir)
		.filter((name) => name.endsWith('.yaml'))
		.map((name) => path.join(dir, name));
}

function checkUrl(file, field, value) {
	if (value === undefined) return;
	if (typeof value !== 'string' || !/^https:\/\//.test(value)) {
		fail(file, `${field} must be an absolute https URL`);
	}
}

function checkLocalImage(file, field, value) {
	if (value === undefined) return;
	if (typeof value !== 'string') {
		fail(file, `${field} must be a string`);
		return;
	}
	if (value.startsWith('https://')) return;
	if (!value.startsWith('/')) {
		fail(file, `${field} must be a site-absolute path (/plugins/...) or an https URL`);
		return;
	}
	if (!existsSync(path.join(publicDir, value))) {
		fail(file, `${field} points at ${value}, which is missing from docs/public`);
	}
}

// Categories -----------------------------------------------------------------

const categoriesFile = path.join(registry, 'categories.yaml');
const categories = existsSync(categoriesFile) ? (read(categoriesFile) ?? {}) : {};
if (!existsSync(categoriesFile)) {
	fail(categoriesFile, 'missing — the registry needs a category list');
}
for (const [slug, category] of Object.entries(categories)) {
	if (!SLUG.test(slug)) fail(categoriesFile, `category key "${slug}" must be kebab-case`);
	if (!category?.label) fail(categoriesFile, `category "${slug}" is missing a label`);
	if (!category?.description) fail(categoriesFile, `category "${slug}" is missing a description`);
}

// Authors --------------------------------------------------------------------

const authors = new Set();
for (const file of listYaml(path.join(registry, 'authors'))) {
	const author = read(file);
	if (!author) continue;
	const expected = path.basename(file, '.yaml');
	if (author.slug !== expected) fail(file, `slug "${author.slug}" must match the filename`);
	if (!SLUG.test(expected)) fail(file, 'filename must be kebab-case');
	if (!author.name) fail(file, 'name is required');
	if (!author.bio) fail(file, 'bio is required');
	checkUrl(file, 'website', author.website);
	checkUrl(file, 'sponsor_url', author.sponsor_url);
	checkLocalImage(file, 'avatar', author.avatar);
	authors.add(expected);
}

// Plugins --------------------------------------------------------------------

for (const file of listYaml(path.join(registry, 'plugins'))) {
	const plugin = read(file);
	if (!plugin) continue;
	const expected = path.basename(file, '.yaml');

	if (plugin.slug !== expected) fail(file, `slug "${plugin.slug}" must match the filename`);
	if (!SLUG.test(expected)) fail(file, 'filename must be kebab-case');
	if (RESERVED_SLUGS.has(expected)) fail(file, `"${expected}" is a reserved docs URL`);

	for (const field of ['name', 'summary', 'description', 'author', 'published_at']) {
		if (!plugin[field]) fail(file, `${field} is required`);
	}
	if (typeof plugin.summary === 'string' && plugin.summary.length > 200) {
		fail(file, 'summary must be 200 characters or fewer');
	}
	if (plugin.author && !authors.has(plugin.author)) {
		fail(file, `unknown author "${plugin.author}" — add authors/${plugin.author}.yaml`);
	}

	const pluginCategories = plugin.categories ?? [];
	if (!Array.isArray(pluginCategories) || pluginCategories.length === 0) {
		fail(file, 'categories must list at least one category');
	} else {
		for (const slug of pluginCategories) {
			if (!(slug in categories)) fail(file, `unknown category "${slug}"`);
		}
	}

	const versions = plugin.orbit_versions ?? [];
	if (!Array.isArray(versions) || versions.length === 0) {
		fail(file, 'orbit_versions must list at least one supported Orbit version');
	}

	const price = plugin.price;
	if (price === undefined) {
		fail(file, 'price is required — use `free` or an amount/currency pair');
	} else if (price !== 'free') {
		if (typeof price?.amount !== 'number' || price.amount <= 0) {
			fail(file, 'price.amount must be a positive number');
		}
		if (!CURRENCY.test(price?.currency ?? '')) {
			fail(file, 'price.currency must be an ISO 4217 code such as USD');
		}
		if (!plugin.checkout_url) fail(file, 'paid plugins must provide a checkout_url');
	} else if (!plugin.package && !plugin.repository) {
		fail(file, 'free plugins must provide a package (PyPI name) or a public repository');
	}

	if (plugin.status && !['published', 'draft'].includes(plugin.status)) {
		fail(file, 'status must be `published` or `draft`');
	}

	checkUrl(file, 'checkout_url', plugin.checkout_url);
	checkUrl(file, 'repository', plugin.repository);
	checkUrl(file, 'docs_url', plugin.docs_url);
	checkLocalImage(file, 'thumbnail', plugin.thumbnail);

	for (const [index, shot] of (plugin.screenshots ?? []).entries()) {
		if (!shot?.alt) fail(file, `screenshots[${index}] needs alt text`);
		checkLocalImage(file, `screenshots[${index}].src`, shot?.src);
	}
}

if (errors.length > 0) {
	console.error(`Marketplace registry has ${errors.length} problem(s):\n`);
	for (const error of errors) console.error(`  - ${error}`);
	console.error('\nSee docs/src/content/docs/plugins/get-listed.md for the listing format.');
	process.exit(1);
}

console.log('Marketplace registry OK.');
