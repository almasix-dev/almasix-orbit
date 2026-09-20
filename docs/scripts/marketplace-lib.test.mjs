import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
	authorStarsTotal,
	formatStat,
	githubRepoUrl,
	isDocsPath,
	isHomePath,
	isMarketplacePath,
	isNavCurrent,
	isPluginDocPath,
	normalizePath,
	parseGithubRepo,
	pluginPathSegment,
	pypiProjectUrl,
} from './marketplace-lib.mjs';

test('marketplace paths are the catalog, not plugin guides or panel docs', () => {
	assert.equal(isMarketplacePath('/plugins'), true);
	assert.equal(isMarketplacePath('/plugins/'), true);
	assert.equal(isMarketplacePath('/plugins/orbit-branding/'), true);
	assert.equal(isMarketplacePath('/plugins/paid/?x=1'), true);
	assert.equal(isMarketplacePath('/plugins/authors/almasix/'), true);
	assert.equal(isMarketplacePath('/plugins/develop/'), true);
	assert.equal(isMarketplacePath('/plugins/feed.json'), true);
	assert.equal(isMarketplacePath('/plugins/using/'), false);
	assert.equal(isMarketplacePath('/plugins/overview/'), false);
	assert.equal(isMarketplacePath('/plugins/get-listed/'), false);
	assert.equal(isMarketplacePath('/panels/plugins/'), false);
	assert.equal(isMarketplacePath('/main/plugins'), true);
	assert.equal(isMarketplacePath('/main/plugins/orbit-branding/'), true);
	assert.equal(isMarketplacePath('/0.x/plugins/using/'), false);
	assert.equal(isMarketplacePath('/0.x/forms/overview/'), false);
	assert.equal(isMarketplacePath('/forms/overview/'), false);
	assert.equal(isMarketplacePath('/panels/configuration/'), false);
});

test('docs vs home vs marketplace for the top-bar menus', () => {
	assert.equal(isHomePath('/'), true);
	assert.equal(isHomePath('/main/'), true);
	assert.equal(isHomePath('/0.x/'), true);
	assert.equal(isHomePath('/index.html'), true);
	assert.equal(isHomePath('/getting-started/installation/'), false);
	assert.equal(isDocsPath('/'), false);
	assert.equal(isDocsPath('/main/getting-started/installation/'), true);
	assert.equal(isDocsPath('/0.x/plugins/overview/'), true);
	assert.equal(isDocsPath('/main/plugins/'), false);
	assert.equal(isDocsPath('/forms/overview/'), true);
	assert.equal(isDocsPath('/plugins/overview/'), true);
	assert.equal(isDocsPath('/panels/plugins/'), true);
	assert.equal(isDocsPath('/plugins/'), false);
	assert.equal(isDocsPath('/plugins/develop/'), false);
	assert.equal(isPluginDocPath('/plugins/using/'), true);
	assert.equal(isPluginDocPath('/plugins/orbit-branding/'), false);
	assert.equal(pluginPathSegment('/plugins/feed.json'), 'feed');
});

test('nav current is exact for catalog roots and nested for indexes', () => {
	assert.equal(isNavCurrent('/plugins/', '/plugins/'), true);
	assert.equal(isNavCurrent('/plugins/', '/plugins/orbit-branding/'), true);
	assert.equal(isNavCurrent('/plugins/', '/plugins/using/'), false);
	assert.equal(isNavCurrent('/plugins/', '/plugins/develop/'), false);
	assert.equal(isNavCurrent('/plugins/paid/', '/plugins/paid/'), true);
	assert.equal(isNavCurrent('/plugins/paid/', '/plugins/'), false);
	assert.equal(isNavCurrent('/plugins/authors/', '/plugins/authors/almasix/'), true);
	assert.equal(isNavCurrent('/plugins/develop/', '/plugins/develop/'), true);
});

test('parseGithubRepo reads owner/repo and ignores extra path', () => {
	assert.equal(parseGithubRepo('https://github.com/acme/orbit-kit'), 'acme/orbit-kit');
	assert.equal(parseGithubRepo('https://github.com/acme/orbit-kit.git'), 'acme/orbit-kit');
	assert.equal(parseGithubRepo('https://github.com/acme/orbit-kit/tree/main'), 'acme/orbit-kit');
	assert.equal(parseGithubRepo('https://gitlab.com/acme/orbit-kit'), null);
	assert.equal(parseGithubRepo(''), null);
});

test('package and GitHub URLs', () => {
	assert.equal(githubRepoUrl('acme/kit'), 'https://github.com/acme/kit');
	assert.equal(pypiProjectUrl('acme-orbit-kit'), 'https://pypi.org/project/acme-orbit-kit/');
	assert.equal(normalizePath('/plugins'), '/plugins/');
});

test('formatStat and author star totals', () => {
	assert.equal(formatStat(null), '—');
	assert.equal(formatStat(12), '12');
	assert.equal(formatStat(1200), '1.2k');
	assert.equal(formatStat(15000), '15k');
	assert.equal(formatStat(2_500_000), '2.5M');
	assert.equal(authorStarsTotal([{ stars: 3 }, { stars: 7 }, {}]), 10);
});
