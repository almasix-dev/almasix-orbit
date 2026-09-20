import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
	DEV_VERSION,
	DOCS_VERSION_QUERY,
	LATEST_VERSION,
	hrefForVersion,
	latestV0Tag,
	prefixHtmlRootUrls,
	splitVersionPath,
	stripVersionPrefix,
	versionFromBase,
	versionFromUrl,
	withDocsBase,
} from '../src/versions.mjs';

test('stripVersionPrefix and splitVersionPath', () => {
	assert.equal(stripVersionPrefix('/getting-started/installation/'), '/getting-started/installation/');
	assert.equal(stripVersionPrefix('/0.x/getting-started/installation/'), '/getting-started/installation/');
	assert.equal(stripVersionPrefix('/main/plugins/'), '/plugins/');
	assert.equal(stripVersionPrefix('/main'), '/');
	assert.equal(stripVersionPrefix('/0.x/'), '/');
	assert.deepEqual(splitVersionPath('/main/plugins/orbit-branding/'), {
		version: 'main',
		inner: '/plugins/orbit-branding/',
	});
	assert.deepEqual(splitVersionPath('/forms/overview/'), { version: null, inner: '/forms/overview/' });
});

test('versionFromUrl prefers path prefix over query and unlabeled dev', () => {
	assert.equal(versionFromUrl('https://orbit.almasix.com/0.x/forms/'), '0.x');
	assert.equal(versionFromUrl('https://orbit.almasix.com/main/forms/'), 'main');
	assert.equal(
		versionFromUrl(`https://orbit.almasix.com/forms/?${DOCS_VERSION_QUERY}=0.x`),
		'0.x',
	);
	assert.equal(versionFromUrl('https://orbit.almasix.com/forms/'), DEV_VERSION);
	assert.equal(versionFromUrl('https://orbit.almasix.com/'), DEV_VERSION);
	assert.equal(versionFromBase('/'), DEV_VERSION);
	assert.equal(versionFromBase('/main/'), 'main');
	assert.equal(versionFromBase('/0.x/'), '0.x');
});

test('hrefForVersion swaps real tree prefixes', () => {
	assert.equal(
		hrefForVersion('/', '0.x', '/main/getting-started/installation/'),
		'/0.x/getting-started/installation/',
	);
	assert.equal(hrefForVersion('/', 'main', '/0.x/plugins/'), '/main/plugins/');
	assert.equal(hrefForVersion('/', '0.x', '/'), '/0.x/');
	assert.equal(
		hrefForVersion('/', 'main', '/0.x/forms/', `?${DOCS_VERSION_QUERY}=0.x&q=1`),
		'/main/forms/?q=1',
	);
	assert.equal(LATEST_VERSION, '0.x');
});

test('withDocsBase prefixes tree base and skips /api', () => {
	assert.equal(withDocsBase('/plugins/', '/'), '/plugins/');
	assert.equal(withDocsBase('/plugins/', '/main/'), '/main/plugins/');
	assert.equal(withDocsBase('/main/plugins/', '/main/'), '/main/plugins/');
	assert.equal(withDocsBase('/api/github/star', '/main/'), '/api/github/star');
});

test('latestV0Tag picks the highest stable 0.x tag', () => {
	assert.equal(latestV0Tag(['v0.1.0', 'v0.3.1', 'v0.2.1', 'v0.3.1-rc.1', 'nightly']), 'v0.3.1');
	assert.equal(latestV0Tag([]), null);
});

test('prefixHtmlRootUrls rewrites site-root hrefs once', () => {
	const html = prefixHtmlRootUrls(
		'<a href="/getting-started/">x</a><link href="/0.x/_astro/a.css"><img src="/_astro/b.png"><a href="/api/github/star">s</a><meta content="https://orbit.almasix.com/forms/">',
		'0.x',
	);
	assert.match(html, /href="\/0\.x\/getting-started\/"/);
	assert.match(html, /href="\/0\.x\/_astro\/a\.css"/);
	assert.match(html, /src="\/0\.x\/_astro\/b\.png"/);
	assert.match(html, /href="\/api\/github\/star"/);
	assert.match(html, /content="https:\/\/orbit\.almasix\.com\/0\.x\/forms\/"/);
});
