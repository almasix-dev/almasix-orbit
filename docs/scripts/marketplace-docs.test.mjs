import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
	fetchGithubReadme,
	fetchListingDocsMarkdown,
	githubRepoFromDocsUrl,
	isListingDocsUrl,
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
