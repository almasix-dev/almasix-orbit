import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { test } from 'node:test';

import { RESERVED_SLUGS, validateMarketplace } from './validate-marketplace.mjs';

function write(root, relative, contents) {
	const file = path.join(root, relative);
	mkdirSync(path.dirname(file), { recursive: true });
	writeFileSync(file, contents);
}

function fixture(overrides = {}) {
	const root = mkdtempSync(path.join(tmpdir(), 'orbit-market-'));
	write(
		root,
		'.marketplace/categories.yaml',
		'theme:\n  label: Theme\n  description: Panel themes.\n',
	);
	write(
		root,
		'.marketplace/authors/almasix.yaml',
		'name: Almasix\nslug: almasix\nbio: The Orbit team.\n',
	);
	write(
		root,
		'.marketplace/plugins/orbit-branding.yaml',
		[
			'name: Orbit Branding',
			'slug: orbit-branding',
			'summary: Sample panel branding plugin from the Orbit examples.',
			'description: Registers a favicon and a render hook.',
			'author: almasix',
			'categories: [theme]',
			'orbit_versions: ["0.3"]',
			'price: free',
			'repository: https://github.com/almasix-dev/almasix-orbit',
			'features:',
			'  official: true',
			'status: published',
			'published_at: 2026-09-20',
			'',
		].join('\n'),
	);
	for (const [relative, contents] of Object.entries(overrides)) {
		if (contents === null) continue;
		write(root, relative, contents);
	}
	return root;
}

test('valid registry is silent', () => {
	const root = fixture();
	try {
		assert.deepEqual(validateMarketplace(root), []);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('reserved slugs include marketplace routes', () => {
	assert.ok(RESERVED_SLUGS.has('using'));
	assert.ok(RESERVED_SLUGS.has('categories'));
	assert.ok(RESERVED_SLUGS.has('feed'));
	assert.ok(RESERVED_SLUGS.has('paid'));
	assert.ok(RESERVED_SLUGS.has('develop'));
});

test('unknown author, category, reserved slug, and paid checkout', () => {
	const root = fixture({
		'.marketplace/plugins/overview.yaml': [
			'name: Reserved',
			'slug: overview',
			'summary: x',
			'description: y',
			'author: missing-author',
			'categories: [not-a-category]',
			'orbit_versions: ["0.3"]',
			'price:',
			'  amount: 10',
			'  currency: USD',
			'status: published',
			'published_at: 2026-01-01',
			'',
		].join('\n'),
	});
	try {
		const errors = validateMarketplace(root).join('\n');
		assert.match(errors, /reserved docs URL/);
		assert.match(errors, /unknown author/);
		assert.match(errors, /unknown category/);
		assert.match(errors, /checkout_url/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('free plugins need a package or repository', () => {
	const root = fixture({
		'.marketplace/plugins/no-dist.yaml': [
			'name: No Dist',
			'slug: no-dist',
			'summary: Missing distribution.',
			'description: Body',
			'author: almasix',
			'categories: [theme]',
			'orbit_versions: ["0.3"]',
			'price: free',
			'published_at: 2026-01-01',
			'',
		].join('\n'),
	});
	try {
		assert.match(validateMarketplace(root).join('\n'), /package \(PyPI name\) or a public repository/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('official is reserved for the almasix author', () => {
	const root = fixture({
		'.marketplace/authors/acme.yaml': 'name: Acme\nslug: acme\nbio: A vendor.\n',
		'.marketplace/plugins/acme-kit.yaml': [
			'name: Acme Kit',
			'slug: acme-kit',
			'summary: Not official.',
			'description: Body',
			'author: acme',
			'categories: [theme]',
			'orbit_versions: ["0.3"]',
			'price: free',
			'repository: https://github.com/acme/kit',
			'features:',
			'  official: true',
			'published_at: 2026-01-01',
			'',
		].join('\n'),
	});
	try {
		assert.match(validateMarketplace(root).join('\n'), /features.official is reserved/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('missing local images and relative paths fail', () => {
	const root = fixture({
		'.marketplace/plugins/orbit-branding.yaml': [
			'name: Orbit Branding',
			'slug: orbit-branding',
			'summary: Sample panel branding plugin from the Orbit examples.',
			'description: Registers a favicon and a render hook.',
			'author: almasix',
			'categories: [theme]',
			'orbit_versions: ["0.3"]',
			'price: free',
			'repository: https://github.com/almasix-dev/almasix-orbit',
			'thumbnail: /plugins/orbit-branding/thumbnail.png',
			'screenshots:',
			'  - src: relative.png',
			'    alt: A shot',
			'published_at: 2026-09-20',
			'',
		].join('\n'),
	});
	try {
		const errors = validateMarketplace(root).join('\n');
		assert.match(errors, /missing from public/);
		assert.match(errors, /site-absolute path/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('invalid status, http URLs, and missing category file', () => {
	const root = fixture();
	write(
		root,
		'.marketplace/plugins/orbit-branding.yaml',
		[
			'name: Orbit Branding',
			'slug: orbit-branding',
			'summary: Sample.',
			'description: Body',
			'author: almasix',
			'categories: [theme]',
			'orbit_versions: ["0.3"]',
			'price: free',
			'repository: http://github.com/almasix-dev/almasix-orbit',
			'status: shipping',
			'published_at: 2026-09-20',
			'',
		].join('\n'),
	);
	try {
		const errors = validateMarketplace(root).join('\n');
		assert.match(errors, /status must be/);
		assert.match(errors, /absolute https URL/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('missing marketplace checkout is reported', () => {
	const root = mkdtempSync(path.join(tmpdir(), 'orbit-market-empty-'));
	try {
		const errors = validateMarketplace(root).join('\n');
		assert.match(errors, /marketplace:sync/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('invalid YAML, slug mismatch, and missing directories', () => {
	const root = fixture({
		'.marketplace/authors/broken.yaml': 'name: [unterminated',
		'.marketplace/authors/wrong-name.yaml': 'name: Wrong\nslug: other-slug\nbio: Bio.\n',
		'.marketplace/plugins/orbit-branding.yaml': [
			'name: Orbit Branding',
			'slug: not-the-filename',
			'summary: Sample.',
			'description: Body',
			'author: almasix',
			'categories: [theme]',
			'orbit_versions: ["0.3"]',
			'price: free',
			'repository: https://github.com/almasix-dev/almasix-orbit',
			'keywords: branding',
			'screenshots:',
			'  - src: https://example.com/shot.png',
			'published_at: 2026-09-20',
			'',
		].join('\n'),
	});
	try {
		const errors = validateMarketplace(root).join('\n');
		assert.match(errors, /invalid YAML/);
		assert.match(errors, /must match the filename/);
		assert.match(errors, /keywords must be a list/);
		assert.match(errors, /needs alt text/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('paid price shape and category labels', () => {
	const root = fixture({
		'.marketplace/categories.yaml': 'theme:\n  description: No label.\n',
		'.marketplace/plugins/orbit-branding.yaml': [
			'name: Orbit Branding',
			'slug: orbit-branding',
			'summary: Sample.',
			'description: Body',
			'author: almasix',
			'categories: [theme]',
			'orbit_versions: []',
			'price:',
			'  amount: 0',
			'  currency: usd',
			'checkout_url: https://store.example.com/buy',
			'published_at: 2026-09-20',
			'',
		].join('\n'),
	});
	try {
		const errors = validateMarketplace(root).join('\n');
		assert.match(errors, /missing a label/);
		assert.match(errors, /orbit_versions must list at least one/);
		assert.match(errors, /price.amount must be a positive number/);
		assert.match(errors, /ISO 4217/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('github_repo and stats must be well-shaped', () => {
	const root = fixture({
		'.marketplace/plugins/orbit-branding.yaml': [
			'name: Orbit Branding',
			'slug: orbit-branding',
			'summary: Sample.',
			'description: Body',
			'author: almasix',
			'categories: [theme]',
			'orbit_versions: ["0.3"]',
			'price: free',
			'repository: https://github.com/almasix-dev/almasix-orbit',
			'github_repo: not a repo',
			'stars: -1',
			'installs: nope',
			'published_at: 2026-09-20',
			'',
		].join('\n'),
	});
	try {
		const errors = validateMarketplace(root).join('\n');
		assert.match(errors, /github_repo must be owner\/repo/);
		assert.match(errors, /stars must be a non-negative number/);
		assert.match(errors, /installs must be a non-negative number/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('missing authors directory is reported', () => {
	const root = mkdtempSync(path.join(tmpdir(), 'orbit-market-no-authors-'));
	write(
		root,
		'.marketplace/categories.yaml',
		'theme:\n  label: Theme\n  description: Panel themes.\n',
	);
	try {
		const errors = validateMarketplace(root).join('\n');
		assert.match(errors, /at least one author profile/);
		assert.match(errors, /add plugin YAML files/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});
