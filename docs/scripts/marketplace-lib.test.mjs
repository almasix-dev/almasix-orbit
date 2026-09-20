import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
	authorStarsTotal,
	formatStat,
	githubRepoUrl,
	isMarketplacePath,
	isNavCurrent,
	normalizePath,
	parseGithubRepo,
	pypiProjectUrl,
} from './marketplace-lib.mjs';

test('marketplace paths include catalog, listings, and plugin development', () => {
	assert.equal(isMarketplacePath('/plugins'), true);
	assert.equal(isMarketplacePath('/plugins/'), true);
	assert.equal(isMarketplacePath('/plugins/orbit-branding/'), true);
	assert.equal(isMarketplacePath('/plugins/paid/?x=1'), true);
	assert.equal(isMarketplacePath('/panels/plugins/'), true);
	assert.equal(isMarketplacePath('/panels/plugins'), true);
	assert.equal(isMarketplacePath('/'), false);
	assert.equal(isMarketplacePath('/forms/overview/'), false);
	assert.equal(isMarketplacePath('/panels/configuration/'), false);
});

test('nav current is exact for catalog roots and nested for indexes', () => {
	assert.equal(isNavCurrent('/plugins/', '/plugins/'), true);
	assert.equal(isNavCurrent('/plugins/', '/plugins/orbit-branding/'), true);
	assert.equal(isNavCurrent('/plugins/', '/plugins/using/'), false);
	assert.equal(isNavCurrent('/plugins/paid/', '/plugins/paid/'), true);
	assert.equal(isNavCurrent('/plugins/paid/', '/plugins/'), false);
	assert.equal(isNavCurrent('/plugins/authors/', '/plugins/authors/almasix/'), true);
	assert.equal(isNavCurrent('/panels/plugins/', '/panels/plugins/'), true);
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
