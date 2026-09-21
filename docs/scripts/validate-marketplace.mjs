/**
 * Validate the plugin marketplace registry before the docs build.
 *
 * Expects a synced checkout at docs/.marketplace (from orbit-plugins):
 *   categories.yaml, authors/*.yaml, plugins/*.yaml, public/plugins/**
 *
 *   npm run marketplace:sync
 *   npm run validate:marketplace
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parse } from 'yaml';

const defaultRoot = path.resolve(fileURLToPath(import.meta.url), '../..');

export const RESERVED_SLUGS = new Set([
	'authors',
	'categories',
	'develop',
	'feed',
	'get-listed',
	'guidelines',
	'overview',
	'paid',
	'paid-vs-free',
	'using',
]);

const SLUG = /^[a-z0-9-]+$/;
const CURRENCY = /^[A-Z]{3}$/;
const STATUSES = new Set(['published', 'draft', 'archived']);

function fail(errors, file, root, message) {
	errors.push(`${path.relative(root, file)}: ${message}`);
}

function read(errors, file, root) {
	try {
		return parse(readFileSync(file, 'utf8'));
	} catch (error) {
		fail(errors, file, root, `invalid YAML — ${error.message}`);
		return null;
	}
}

function listYaml(dir) {
	if (!existsSync(dir)) return [];
	return readdirSync(dir)
		.filter((name) => name.endsWith('.yaml'))
		.map((name) => path.join(dir, name));
}

function checkUrl(errors, file, root, field, value) {
	if (value === undefined || value === null || value === '') return;
	if (typeof value !== 'string' || !/^https:\/\//.test(value)) {
		fail(errors, file, root, `${field} must be an absolute https URL`);
	}
}

function checkLocalImage(errors, file, root, publicDir, field, value) {
	if (value === undefined || value === null || value === '') return;
	if (typeof value !== 'string') {
		fail(errors, file, root, `${field} must be a string`);
		return;
	}
	if (value.startsWith('https://')) return;
	if (!value.startsWith('/')) {
		fail(
			errors,
			file,
			root,
			`${field} must be a site-absolute path (/plugins/...) or an https URL`,
		);
		return;
	}
	if (!existsSync(path.join(publicDir, value))) {
		fail(
			errors,
			file,
			root,
			`${field} points at ${value}, which is missing from public (run marketplace:sync)`,
		);
	}
}

/**
 * Validate a synced marketplace registry.
 *
 * @param {string} [docsRoot] docs/ directory
 * @returns {string[]} error messages (empty when the registry is OK)
 */
export function validateMarketplace(docsRoot = defaultRoot) {
	const errors = [];
	const registry = path.join(docsRoot, '.marketplace');
	const publicDir = path.join(docsRoot, 'public');
	const failFile = (file, message) => fail(errors, file, docsRoot, message);

	if (!existsSync(registry)) {
		failFile(
			registry,
			'missing — run `npm run marketplace:sync` (fetches almasix-dev/orbit-plugins)',
		);
		return errors;
	}

	const categoriesFile = path.join(registry, 'categories.yaml');
	const categories = existsSync(categoriesFile) ? (read(errors, categoriesFile, docsRoot) ?? {}) : {};
	if (!existsSync(categoriesFile)) {
		failFile(categoriesFile, 'missing — the registry needs a category list');
	} else if (categories === null || typeof categories !== 'object' || Array.isArray(categories)) {
		failFile(categoriesFile, 'must be a mapping of slug → { label, description }');
	} else {
		for (const [slug, category] of Object.entries(categories)) {
			if (!SLUG.test(slug)) failFile(categoriesFile, `category key "${slug}" must be kebab-case`);
			if (!category?.label) failFile(categoriesFile, `category "${slug}" is missing a label`);
			if (!category?.description) {
				failFile(categoriesFile, `category "${slug}" is missing a description`);
			}
		}
	}

	const authors = new Set();
	const authorsDir = path.join(registry, 'authors');
	if (!existsSync(authorsDir)) {
		failFile(authorsDir, 'missing — add at least one author profile in orbit-plugins');
	}
	for (const file of listYaml(authorsDir)) {
		const author = read(errors, file, docsRoot);
		if (!author) continue;
		const expected = path.basename(file, '.yaml');
		if (author.slug !== expected) failFile(file, `slug "${author.slug}" must match the filename`);
		if (!SLUG.test(expected)) failFile(file, 'filename must be kebab-case');
		if (!author.name) failFile(file, 'name is required');
		if (!author.bio) failFile(file, 'bio is required');
		checkUrl(errors, file, docsRoot, 'website', author.website);
		checkUrl(errors, file, docsRoot, 'sponsor_url', author.sponsor_url);
		checkLocalImage(errors, file, docsRoot, publicDir, 'avatar', author.avatar);
		authors.add(expected);
	}

	const pluginsDir = path.join(registry, 'plugins');
	if (!existsSync(pluginsDir)) {
		failFile(pluginsDir, 'missing — add plugin YAML files in orbit-plugins');
	}
	for (const file of listYaml(pluginsDir)) {
		const plugin = read(errors, file, docsRoot);
		if (!plugin) continue;
		const expected = path.basename(file, '.yaml');

		if (plugin.slug !== expected) failFile(file, `slug "${plugin.slug}" must match the filename`);
		if (!SLUG.test(expected)) failFile(file, 'filename must be kebab-case');
		if (RESERVED_SLUGS.has(expected)) failFile(file, `"${expected}" is a reserved docs URL`);

		for (const field of ['name', 'summary', 'description', 'author', 'published_at']) {
			if (!plugin[field]) failFile(file, `${field} is required`);
		}
		if (typeof plugin.summary === 'string' && plugin.summary.length > 200) {
			failFile(file, 'summary must be 200 characters or fewer');
		}
		if (plugin.author && !authors.has(plugin.author)) {
			failFile(file, `unknown author "${plugin.author}" — add authors/${plugin.author}.yaml`);
		}

		const pluginCategories = plugin.categories ?? [];
		if (!Array.isArray(pluginCategories) || pluginCategories.length === 0) {
			failFile(file, 'categories must list at least one category');
		} else {
			for (const slug of pluginCategories) {
				if (!(slug in categories)) failFile(file, `unknown category "${slug}"`);
			}
		}

		const versions = plugin.orbit_versions ?? [];
		if (!Array.isArray(versions) || versions.length === 0) {
			failFile(file, 'orbit_versions must list at least one supported Orbit version');
		}

		const price = plugin.price;
		if (price === undefined) {
			failFile(file, 'price is required — use `free` or an amount/currency pair');
		} else if (price !== 'free') {
			if (typeof price?.amount !== 'number' || price.amount <= 0) {
				failFile(file, 'price.amount must be a positive number');
			}
			if (!CURRENCY.test(price?.currency ?? '')) {
				failFile(file, 'price.currency must be an ISO 4217 code such as USD');
			}
			if (!plugin.checkout_url) failFile(file, 'paid plugins must provide a checkout_url');
		} else if (!plugin.package && !plugin.repository) {
			failFile(file, 'free plugins must provide a package (PyPI name) or a public repository');
		}

		if (plugin.status && !STATUSES.has(plugin.status)) {
			failFile(file, 'status must be `published`, `draft`, or `archived`');
		}
		if (plugin.features?.official === true && plugin.author !== 'almasix') {
			failFile(file, 'features.official is reserved for listings whose author is `almasix`');
		}

		if (plugin.keywords !== undefined && !Array.isArray(plugin.keywords)) {
			failFile(file, 'keywords must be a list of strings');
		}
		if (plugin.github_repo !== undefined && !/^[\w.-]+\/[\w.-]+$/.test(plugin.github_repo)) {
			failFile(file, 'github_repo must be owner/repo');
		}
		for (const field of ['stars', 'installs']) {
			if (plugin[field] !== undefined && (typeof plugin[field] !== 'number' || plugin[field] < 0)) {
				failFile(file, `${field} must be a non-negative number`);
			}
		}

		checkUrl(errors, file, docsRoot, 'checkout_url', plugin.checkout_url);
		checkUrl(errors, file, docsRoot, 'repository', plugin.repository);
		checkUrl(errors, file, docsRoot, 'docs_url', plugin.docs_url);
		checkUrl(errors, file, docsRoot, 'homepage', plugin.homepage);
		checkUrl(errors, file, docsRoot, 'changelog_url', plugin.changelog_url);
		checkLocalImage(errors, file, docsRoot, publicDir, 'thumbnail', plugin.thumbnail);

		for (const [index, shot] of (plugin.screenshots ?? []).entries()) {
			if (!shot?.alt) failFile(file, `screenshots[${index}] needs alt text`);
			checkLocalImage(errors, file, docsRoot, publicDir, `screenshots[${index}].src`, shot?.src);
		}
	}

	return errors;
}

function runCli() {
	const errors = validateMarketplace();
	if (errors.length > 0) {
		console.error(`Marketplace registry has ${errors.length} problem(s):\n`);
		for (const error of errors) console.error(`  - ${error}`);
		console.error(
			'\nSync from https://github.com/almasix-dev/orbit-plugins then see /plugins/get-listed/.',
		);
		process.exit(1);
	}
	console.log('Marketplace registry OK.');
}

const invokedDirectly =
	Boolean(process.argv[1]) && import.meta.url === pathToFileURL(process.argv[1]).href;
if (invokedDirectly) {
	runCli();
}
