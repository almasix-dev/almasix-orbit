import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
	branchFromGithubContentUrl,
	fetchGithubReadme,
	fetchListingDocsMarkdown,
	githubRawUrl,
	githubRepoFromDocsUrl,
	isListingDocsUrl,
	rewriteGithubReadmeMedia,
} from './marketplace-docs.mjs';

test('isListingDocsUrl detects self-referential marketplace links', () => {
	assert.equal(
		isListingDocsUrl('https://orbit.almasix.com/plugins/orbit-permission/', '/plugins/orbit-permission/'),
		true,
	);
	assert.equal(
		isListingDocsUrl('https://orbit.almasix.com/main/plugins/orbit-permission/', '/plugins/orbit-permission/'),
		true,
	);
	assert.equal(
		isListingDocsUrl('https://github.com/almasix-dev/almasix-orbit-permission', '/plugins/orbit-permission/'),
		false,
	);
});

test('githubRepoFromDocsUrl parses repo, blob, and tree URLs', () => {
	assert.equal(
		githubRepoFromDocsUrl('https://github.com/almasix-dev/almasix-orbit-permission'),
		'almasix-dev/almasix-orbit-permission',
	);
	assert.equal(
		githubRepoFromDocsUrl('https://github.com/acme/kit/blob/main/README.md'),
		'acme/kit',
	);
	assert.equal(
		githubRepoFromDocsUrl('https://github.com/acme/kit/tree/develop/docs'),
		'acme/kit',
	);
});

test('fetchGithubReadme uses the GitHub API download_url', async () => {
	const markdown = '# Hello from README';
	const calls = [];
	const doFetch = async (url) => {
		calls.push(String(url));
		if (String(url).endsWith('/readme')) {
			return new Response(JSON.stringify({ download_url: 'https://cdn.example/readme.md' }), {
				status: 200,
				headers: { 'Content-Type': 'application/json' },
			});
		}
		if (String(url) === 'https://cdn.example/readme.md') {
			return new Response(markdown, { status: 200 });
		}
		return new Response('missing', { status: 404 });
	};
	const result = await fetchGithubReadme('acme/kit', doFetch);
	assert.equal(result, markdown);
	assert.match(calls[0], /api\.github\.com\/repos\/acme\/kit\/readme/);
});

test('fetchListingDocsMarkdown skips self-referential docs_url', async () => {
	const result = await fetchListingDocsMarkdown(
		'https://orbit.almasix.com/plugins/orbit-permission/',
		'/plugins/orbit-permission/',
		async () => {
			throw new Error('should not fetch');
		},
	);
	assert.equal(result, null);
});

test('fetchListingDocsMarkdown resolves GitHub docs_url to README markdown', async () => {
	const result = await fetchListingDocsMarkdown(
		'https://github.com/almasix-dev/almasix-orbit-permission',
		'/plugins/orbit-permission/',
		async (url) => {
			if (String(url).endsWith('/readme')) {
				return new Response(JSON.stringify({ download_url: 'https://cdn.example/readme.md' }), {
					status: 200,
					headers: { 'Content-Type': 'application/json' },
				});
			}
			return new Response('# Plugin docs', { status: 200 });
		},
	);
	assert.equal(result, '# Plugin docs');
});

test('rewriteGithubReadmeMedia rewrites relative markdown and HTML images', () => {
	assert.equal(githubRawUrl('acme/kit', 'main', 'docs/a.png'), 'https://raw.githubusercontent.com/acme/kit/main/docs/a.png');
	assert.equal(branchFromGithubContentUrl('https://raw.githubusercontent.com/acme/kit/develop/README.md'), 'develop');

	const md = rewriteGithubReadmeMedia(
		[
			'![Light](docs/images/general-settings.png)',
			'<img src="docs/images/general-settings-form.png" alt="form" width="48%" />',
			'<img src="./docs/images/dark.png" alt="dark" />',
			'![Abs](https://example.com/a.png)',
			'![Blob](https://github.com/acme/kit/blob/main/docs/shot.png)',
		].join('\n'),
		'acme/kit',
		'main',
	);
	assert.match(md, /!\[Light\]\(https:\/\/raw\.githubusercontent\.com\/acme\/kit\/main\/docs\/images\/general-settings\.png\)/);
	assert.match(md, /src="https:\/\/raw\.githubusercontent\.com\/acme\/kit\/main\/docs\/images\/general-settings-form\.png"/);
	assert.match(md, /src="https:\/\/raw\.githubusercontent\.com\/acme\/kit\/main\/docs\/images\/dark\.png"/);
	assert.match(md, /!\[Abs\]\(https:\/\/example\.com\/a\.png\)/);
	assert.match(md, /!\[Blob\]\(https:\/\/raw\.githubusercontent\.com\/acme\/kit\/main\/docs\/shot\.png\)/);
});

test('fetchGithubReadme rewrites media using download_url branch', async () => {
	const result = await fetchGithubReadme('acme/kit', async (url) => {
		if (String(url).endsWith('/readme')) {
			return new Response(
				JSON.stringify({
					download_url: 'https://raw.githubusercontent.com/acme/kit/main/README.md',
					html_url: 'https://github.com/acme/kit/blob/main/README.md',
				}),
				{ status: 200, headers: { 'Content-Type': 'application/json' } },
			);
		}
		return new Response('![Shot](docs/images/shot.png)', { status: 200 });
	});
	assert.equal(
		result,
		'![Shot](https://raw.githubusercontent.com/acme/kit/main/docs/images/shot.png)',
	);
});
