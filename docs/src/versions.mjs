/**
 * Documentation version switcher — majors + main only.
 *
 * Majors (`0.x`, later `1.x`, …) are the published lines. **Latest** is always
 * the newest major — never `main`. `main` is the unreleased tip and is opt-in.
 *
 * Production builds emit parallel trees at `/0.x/` (latest 0.x git tag) and
 * `/main/` (this commit). Unprefixed `/` redirects to latest. `astro dev`
 * stays unprefixed and is the `main` tree.
 */

/** @typedef {{ slug: string, label: string, kind: 'unreleased' | 'major' }} DocsVersion */

/** @type {DocsVersion[]} — latest major first; `main` last (never default). */
export const DOCS_VERSIONS = [
	{ slug: '0.x', label: '0.x', kind: 'major' },
	{ slug: 'main', label: 'main', kind: 'unreleased' },
];

/** Newest published major — the default docs line. Never `main`. */
export const LATEST_VERSION = '0.x';

/** Unprefixed local `astro dev` is the unreleased tree. */
export const DEV_VERSION = 'main';

export const DOCS_VERSION_QUERY = 'docsVersion';

const SKIP_PREFIX_HEADS = new Set(['api', ...DOCS_VERSIONS.map((version) => version.slug)]);

/** @param {string} slug */
export function isKnownVersion(slug) {
	return DOCS_VERSIONS.some((version) => version.slug === slug);
}

/**
 * Drop a leading `/0.x/` or `/main/` segment.
 * @param {string} pathname
 */
export function stripVersionPrefix(pathname) {
	const raw = String(pathname ?? '').split('?')[0] || '/';
	const leading = raw.startsWith('/') ? raw : `/${raw}`;
	const parts = leading.split('/');
	const head = parts[1];
	if (!head || !isKnownVersion(head)) return leading || '/';
	const rest = parts.slice(2).join('/');
	return rest ? `/${rest}` : '/';
}

/**
 * @param {string} pathname
 * @returns {{ version: string | null, inner: string }}
 */
export function splitVersionPath(pathname) {
	const raw = String(pathname ?? '').split('?')[0] || '/';
	const leading = raw.startsWith('/') ? raw : `/${raw}`;
	const parts = leading.split('/');
	const head = parts[1];
	if (head && isKnownVersion(head)) {
		const rest = parts.slice(2).join('/');
		return { version: head, inner: rest ? `/${rest}` : '/' };
	}
	return { version: null, inner: leading || '/' };
}

/**
 * @param {URL | string} url
 * @param {string} [unlabeled] when the path has no version prefix (local `astro dev`)
 */
export function versionFromUrl(url, unlabeled = DEV_VERSION) {
	const parsed = typeof url === 'string' ? new URL(url, 'https://example.invalid') : url;
	const { version } = splitVersionPath(parsed.pathname);
	if (version) return version;
	const fromQuery = parsed.searchParams.get(DOCS_VERSION_QUERY);
	if (fromQuery && isKnownVersion(fromQuery)) return fromQuery;
	return unlabeled;
}

/**
 * Tree identity from Astro `BASE_URL` (`/`, `/main/`, `/0.x/`).
 * @param {string} [base]
 */
export function versionFromBase(base) {
	const head = String(base ?? '/')
		.split('/')
		.filter(Boolean)[0];
	return head && isKnownVersion(head) ? head : DEV_VERSION;
}

/**
 * Prefix a site-absolute path with the active docs tree (`/main/plugins/`).
 * @param {string} pathname
 * @param {string} [baseUrl]
 */
export function withDocsBase(pathname, baseUrl = '/') {
	const base = String(baseUrl || '/').replace(/\/?$/, '/');
	const path = pathname.startsWith('/') ? pathname : `/${pathname}`;
	if (base === '/') return path;
	const prefix = base.replace(/\/$/, '');
	if (path === prefix || path.startsWith(`${prefix}/`)) return path;
	const head = path.split('/').filter(Boolean)[0];
	if (head && SKIP_PREFIX_HEADS.has(head)) return path;
	return `${prefix}${path}`;
}

/**
 * @param {string} _base  unused (kept so existing call sites still compile)
 * @param {string} slug
 * @param {string} [pathname]
 * @param {string} [search]
 */
export function hrefForVersion(_base, slug, pathname = '/', search = '') {
	const target = isKnownVersion(slug) ? slug : LATEST_VERSION;
	const inner = stripVersionPrefix(pathname);
	const innerPath = inner === '/' ? '/' : inner.startsWith('/') ? inner : `/${inner}`;
	const path = `/${target}${innerPath === '/' ? '/' : innerPath}`;
	const params = new URLSearchParams(search.startsWith('?') ? search.slice(1) : search);
	params.delete(DOCS_VERSION_QUERY);
	const query = params.toString();
	return query ? `${path}?${query}` : path;
}

/**
 * Stable `v0.MIN.PATCH` tags only (no pre-releases).
 * @param {string[]} tags
 */
export function latestV0Tag(tags) {
	const versions = (tags ?? [])
		.map((tag) => String(tag).trim())
		.filter((tag) => /^v0\.\d+\.\d+$/.test(tag))
		.sort((a, b) => {
			const pa = a.slice(1).split('.').map(Number);
			const pb = b.slice(1).split('.').map(Number);
			for (let i = 0; i < 3; i += 1) {
				if (pa[i] !== pb[i]) return pa[i] - pb[i];
			}
			return 0;
		});
	return versions.at(-1) ?? null;
}

/**
 * Prefix root-absolute URLs in built HTML with `/{version}` unless already versioned or `/api`.
 * @param {string} html
 * @param {string} versionSlug
 * @param {string} [origin]
 */
export function prefixHtmlRootUrls(html, versionSlug, origin = 'https://orbit.almasix.com') {
	const prefix = `/${versionSlug}`;
	const rewritePath = (path) => {
		if (!path.startsWith('/') || path.startsWith('//')) return path;
		const head = path.split('/').filter(Boolean)[0];
		if (head && SKIP_PREFIX_HEADS.has(head)) return path;
		if (path === prefix || path.startsWith(`${prefix}/`)) return path;
		return `${prefix}${path}`;
	};
	const originEscaped = origin.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
	return html
		.replace(/(href|src|action)=("|')(\/[^"']*)\2/g, (match, attr, quote, path) => {
			void match;
			return `${attr}=${quote}${rewritePath(path)}${quote}`;
		})
		.replace(
			new RegExp(`(content|href)=("|')${originEscaped}(/[^"']*)\\2`, 'g'),
			(match, attr, quote, path) => {
				void match;
				return `${attr}=${quote}${origin}${rewritePath(path)}${quote}`;
			},
		);
}
