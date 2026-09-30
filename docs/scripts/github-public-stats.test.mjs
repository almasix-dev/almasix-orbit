import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
	clearPublicRepoStatsCache,
	fetchPublicRepoStats,
	formatCount,
	getGitHubStats,
	githubStatsThemeAlias,
} from './github-public-stats.mjs';
import { fillGithubStatsHtml, htmlHasMissingGithubStats } from './github-stats-html.mjs';

function jsonResponse(body, status = 200) {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' },
	});
}

const chip = `<div class="header"><div class="gh-chip astro-abc" role="group" aria-label="GitHub repository"><a class="gh-chip__part astro-abc" href="https://github.com/acme/kit" title="GitHub stars"><span class="astro-abc">—</span></a><a class="gh-chip__part astro-abc" href="https://github.com/acme/kit/forks" title="GitHub forks"><span class="astro-abc">—</span></a></div></div>`;

const card = `<ul><li class="market-card" data-plugin data-search="kit https://github.com/acme/kit theme" data-stars data-installs><div><ul class="market-stats"><li title="PyPI downloads in the last 30 days"><strong>—</strong><span class="market-stats-label">Installs</span></li><li title="GitHub stars"><strong>—</strong><span class="market-stats-label">Stars</span></li></ul><a class="market-card-link" href="https://github.com/acme/kit" title="GitHub repository">GitHub</a></div></li></ul>`;

test('formatCount matches the header chip', () => {
	assert.equal(formatCount(0), '0');
	assert.equal(formatCount(12), '12');
	assert.equal(formatCount(1500), '1.5k');
});

test('a rejected build token retries anonymously, then shields', async () => {
	clearPublicRepoStatsCache();
	const previous = process.env.GITHUB_TOKEN;
	process.env.GITHUB_TOKEN = 'fine-grained-without-access';
	const calls = [];
	try {
		const stats = await fetchPublicRepoStats('acme/kit', async (url, init) => {
			calls.push({ url, auth: init?.headers?.Authorization ?? '' });
			if (url.includes('api.github.com') && init?.headers?.Authorization) {
				return jsonResponse({ message: 'Not Found' }, 404);
			}
			if (url.endsWith('/repos/acme/kit')) {
				return jsonResponse({ stargazers_count: 4, forks_count: 2 });
			}
			if (url.endsWith('/releases/latest')) return jsonResponse({ message: 'Not Found' }, 404);
			if (url.includes('/github/v/release/')) return jsonResponse({ message: 'v1.2.3', value: 'v1.2.3' });
			return jsonResponse({ message: 'nope' }, 500);
		});
		assert.equal(stats.stars, 4);
		assert.equal(stats.forks, 2);
		assert.equal(stats.release, 'v1.2.3');
		assert.equal(stats.source, 'github');
		assert.ok(calls.some((call) => call.url.includes('api.github.com') && call.auth === ''));
	} finally {
		if (previous == null) delete process.env.GITHUB_TOKEN;
		else process.env.GITHUB_TOKEN = previous;
		clearPublicRepoStatsCache();
	}
});

test('shields fills stars when the GitHub API is rate-limited', async () => {
	clearPublicRepoStatsCache();
	const previousToken = process.env.GITHUB_TOKEN;
	const previousGh = process.env.GH_TOKEN;
	delete process.env.GITHUB_TOKEN;
	delete process.env.GH_TOKEN;
	try {
		const stats = await fetchPublicRepoStats('acme/kit', async (url) => {
			if (url.includes('api.github.com')) return jsonResponse({ message: 'rate limit' }, 403);
			if (url.includes('/github/stars/')) return jsonResponse({ value: '8', message: '8' });
			if (url.includes('/github/forks/')) return jsonResponse({ value: '1', message: '1' });
			if (url.includes('/github/v/release/')) return jsonResponse({ message: 'unavailable' });
			return jsonResponse({}, 404);
		});
		assert.equal(stats.stars, 8);
		assert.equal(stats.forks, 1);
		assert.equal(stats.release, null);
		assert.equal(stats.source, 'shields');
		assert.equal((await getGitHubStats('acme/kit')).stars, 8);
	} finally {
		if (previousToken == null) delete process.env.GITHUB_TOKEN;
		else process.env.GITHUB_TOKEN = previousToken;
		if (previousGh == null) delete process.env.GH_TOKEN;
		else process.env.GH_TOKEN = previousGh;
		clearPublicRepoStatsCache();
	}
});

test('fill replaces header and marketplace dashes and keeps real install counts', async () => {
	const html = `${chip}<button type="button" data-star-slug="kit" data-star-repo="acme/kit" data-star-base><span data-star-count>—</span></button><strong data-star-count-page="kit">—</strong>${card}<ul class="market-stats"><li><strong>0</strong><span class="market-stats-label">Stars</span></li></ul></body>`;
	const filled = await fillGithubStatsHtml(html, async () => ({
		stars: 4,
		forks: 0,
		release: 'v9.0.0',
		source: 'test',
	}));
	assert.match(filled, /title="GitHub stars"[\s\S]*?<span class="astro-abc">4<\/span>/);
	assert.match(filled, /title="GitHub forks"[\s\S]*?<span class="astro-abc">0<\/span>/);
	assert.match(filled, /class="gh-chip__part astro-abc gh-chip__release" href="https:\/\/github.com\/acme\/kit\/releases">v9\.0\.0/);
	assert.match(filled, /data-stars="4"/);
	assert.match(filled, /data-star-base="4"/);
	assert.match(filled, /data-star-count>4</);
	assert.match(filled, /data-star-count-page="kit">4</);
	assert.match(filled, /title="PyPI downloads[\s\S]*?<strong>—<\/strong>/);
	assert.match(filled, /<strong>4<\/strong><span class="market-stats-label">Stars<\/span>/);
	assert.equal(htmlHasMissingGithubStats(filled), false);
	assert.match(filled, /data-orbit-github-stats/);
});

test('a card baked at 0 stars still loads a live count', async () => {
	const html =
		'<body><li class="market-card" data-plugin data-star-repo="acme/kit" data-stars="0"><li title="GitHub stars"><strong>0</strong></li></li></body>';
	const filled = await fillGithubStatsHtml(html, async () => {
		throw new Error('baked numbers are refreshed in the browser');
	});
	assert.match(filled, /data-orbit-github-stats/);
	assert.match(filled, /data-stars="0"/);
});

test('a failed lookup leaves a browser backfill script and does not clobber known counts', async () => {
	const known = chip
		.replaceAll('—', '3')
		.replace(
			'aria-label="GitHub repository">',
			'aria-label="GitHub repository"><a class="gh-chip__part astro-abc gh-chip__release" href="https://github.com/acme/kit/releases">v1</a>',
		);
	const unchanged = await fillGithubStatsHtml(known, async () => {
		throw new Error('should not fetch when counts are present');
	});
	assert.equal(unchanged, known);

	const dashed = `<body>${chip}</body>`;
	const fallback = await fillGithubStatsHtml(dashed, async () => ({
		stars: null,
		forks: null,
		release: null,
		source: 'unavailable',
	}));
	assert.match(fallback, /data-orbit-github-stats/);
	assert.match(fallback, /api\.github\.com\/repos\//);
	assert.equal(htmlHasMissingGithubStats(fallback), true);
});

test('theme alias resolves only the starlight-theme github-stats import', () => {
	const plugin = githubStatsThemeAlias(new URL('./github-public-stats.mjs', import.meta.url));
	const hit = plugin.resolveId(
		'../lib/github-stats',
		'/workspace/docs/node_modules/@almasix/starlight-theme/components/Header.astro',
	);
	assert.match(hit, /github-public-stats\.mjs$/);
	assert.equal(
		plugin.resolveId('../lib/github-stats', '/workspace/docs/src/components/Header.astro'),
		null,
	);
});
