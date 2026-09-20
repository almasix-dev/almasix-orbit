/**
 * Shared marketplace helpers — used by the Astro catalog and Node tests.
 */

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
		label: 'Guides',
		items: [
			{ label: 'Using a plugin', href: '/plugins/using/' },
			{ label: 'Building a plugin', href: '/panels/plugins/' },
			{ label: 'Listing a plugin', href: '/plugins/get-listed/' },
			{ label: 'Listing guidelines', href: '/plugins/guidelines/' },
			{ label: 'Paid vs free', href: '/plugins/paid-vs-free/' },
			{ label: 'How listings work', href: '/plugins/overview/' },
		],
	},
];

/** Trailing slash, no query string — matches Starlight's static URLs. */
export function normalizePath(pathname) {
	const raw = (pathname ?? '/').split('?')[0] || '/';
	if (raw === '/') return '/';
	return raw.endsWith('/') ? raw : `${raw}/`;
}

export function isMarketplacePath(pathname) {
	const path = (pathname ?? '/').split('?')[0].replace(/\/+$/, '') || '/';
	return path === '/plugins' || path.startsWith('/plugins/') || path === '/panels/plugins';
}

export function isHomePath(pathname) {
	const path = (pathname ?? '/').split('?')[0].replace(/\/+$/, '') || '/';
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
		return (
			parts[0] === 'plugins' &&
			parts.length === 2 &&
			!['authors', 'categories', 'paid', 'using', 'get-listed', 'guidelines', 'overview', 'paid-vs-free'].includes(
				parts[1],
			)
		);
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
