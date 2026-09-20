/**
 * Shared marketplace helpers — used by the Astro catalog and Node tests.
 */

import { stripVersionPrefix } from '../src/versions.mjs';

/** Catalog indexes (not a plugin listing slug). */
export const MARKETPLACE_INDEX_SEGMENTS = ['authors', 'categories', 'develop', 'feed', 'paid'];

/** Plugin guides that live under `/plugins/` but use the docs sidebar. */
export const PLUGIN_DOC_SEGMENTS = ['get-listed', 'guidelines', 'overview', 'paid-vs-free', 'using'];

export const MARKETPLACE_NAV = [
	{
		label: 'Browse',
		items: [
			{ label: 'All plugins', href: '/plugins/' },
			{ label: 'Paid plugins', href: '/plugins/paid/' },
			{ label: 'Authors', href: '/plugins/authors/' },
			{ label: 'Categories', href: '/plugins/categories/' },
		],
	},
	{
		label: 'Catalog API',
		items: [{ label: 'JSON feed', href: '/plugins/develop/' }],
	},
];

/** Trailing slash, no query string — matches Starlight's static URLs. */
export function normalizePath(pathname) {
	const raw = stripVersionPrefix((pathname ?? '/').split('?')[0] || '/');
	if (raw === '/') return '/';
	return raw.endsWith('/') ? raw : `${raw}/`;
}

/** First `/plugins/…` segment, without a trailing file extension. */
export function pluginPathSegment(pathname) {
	const path = stripVersionPrefix((pathname ?? '/').split('?')[0]).replace(/\/+$/, '') || '/';
	if (path === '/plugins') return '';
	if (!path.startsWith('/plugins/')) return null;
	return path.slice('/plugins/'.length).split('/')[0].replace(/\.[a-z0-9]+$/i, '');
}

export function isMarketplacePath(pathname) {
	const segment = pluginPathSegment(pathname);
	if (segment === null) return false;
	if (segment === '') return true;
	return !PLUGIN_DOC_SEGMENTS.includes(segment);
}

export function isPluginDocPath(pathname) {
	const segment = pluginPathSegment(pathname);
	return Boolean(segment) && PLUGIN_DOC_SEGMENTS.includes(segment);
}

export function isHomePath(pathname) {
	const path = stripVersionPrefix((pathname ?? '/').split('?')[0]).replace(/\/+$/, '') || '/';
	return path === '/' || path === '/index' || path === '/index.html';
}

/** Documentation pages (not the splash home, not the plugin catalog). */
export function isDocsPath(pathname) {
	return !isHomePath(pathname) && !isMarketplacePath(pathname);
}

/**
 * Highlight a sidebar link. Catalog roots stay exact; nested indexes
 * (`/plugins/authors/almasix/`) keep their parent current. Listing pages
 * (`/plugins/orbit-branding/`) keep "All plugins" current.
 */
export function isNavCurrent(href, pathname) {
	const current = normalizePath(pathname);
	const target = normalizePath(href);
	if (target === '/plugins/paid/') {
		return current === target;
	}
	if (target === '/plugins/') {
		if (current === '/plugins/') return true;
		const parts = current.replace(/^\/+|\/+$/g, '').split('/');
		const listing = parts[0] === 'plugins' && parts.length === 2 ? parts[1].replace(/\.[a-z0-9]+$/i, '') : '';
		return Boolean(listing) && !MARKETPLACE_INDEX_SEGMENTS.includes(listing) && !PLUGIN_DOC_SEGMENTS.includes(listing);
	}
	return current === target || current.startsWith(target);
}

/** `owner/repo` from a GitHub HTTPS URL, or null. */
export function parseGithubRepo(url) {
	if (!url || typeof url !== 'string') return null;
	const match = url.match(/^https:\/\/github\.com\/([\w.-]+)\/([\w.-]+?)(?:\.git)?(?:\/|#|\?|$)/i);
	return match ? `${match[1]}/${match[2]}` : null;
}

export function githubRepoUrl(repo) {
	return `https://github.com/${repo}`;
}

export function pypiProjectUrl(pkg) {
	return `https://pypi.org/project/${encodeURIComponent(pkg)}/`;
}

export function formatStat(value) {
	if (value == null || Number.isNaN(value)) return '—';
	if (value >= 1_000_000) {
		const m = value / 1_000_000;
		return `${m >= 10 ? Math.round(m) : m.toFixed(1).replace(/\.0$/, '')}M`;
	}
	if (value >= 1000) {
		const k = value / 1000;
		return `${k >= 10 ? Math.round(k) : k.toFixed(1).replace(/\.0$/, '')}k`;
	}
	return String(value);
}

export function authorStarsTotal(plugins) {
	return plugins.reduce((sum, plugin) => sum + (Number(plugin.stars) || 0), 0);
}
