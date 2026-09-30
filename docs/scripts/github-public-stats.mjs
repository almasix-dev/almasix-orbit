/**
 * Public GitHub stars, forks, and latest release.
 *
 * Docs builds on shared datacenter IPs often 401/403/404 the GitHub API when a
 * build token is missing, expired, or not allowed to see the repo (GitHub
 * hides public repos from fine-grained tokens as 404). A bad token used to
 * bake em dashes into the header chip and marketplace cards. Try the API,
 * retry without the token, then read shields.io which caches the same numbers.
 */

import { fileURLToPath } from 'node:url';

const REPO_RE = /^[\w.-]+\/[\w.-]+$/;
const cache = new Map();

export function clearPublicRepoStatsCache() {
	cache.clear();
}

function readToken() {
	const raw = process.env?.GITHUB_TOKEN || process.env?.GH_TOKEN;
	if (typeof raw !== 'string') return '';
	const token = raw.trim();
	if (!token || token === 'undefined' || token === 'null') return '';
	return token;
}

function githubHeaders(token) {
	const headers = {
		Accept: 'application/vnd.github+json',
		'User-Agent': 'almasix-orbit-docs',
		'X-GitHub-Api-Version': '2022-11-28',
	};
	if (token) headers.Authorization = `Bearer ${token}`;
	return headers;
}

async function fetchJson(url, headers, doFetch) {
	try {
		const response = await doFetch(url, { headers });
		if (!response.ok) return { ok: false, status: response.status, data: null };
		return { ok: true, status: response.status, data: await response.json() };
	} catch {
		return { ok: false, status: 0, data: null };
	}
}

function parseShieldNumber(payload) {
	if (!payload || typeof payload !== 'object') return null;
	const raw = payload.value ?? payload.message;
	if (typeof raw === 'number' && Number.isFinite(raw)) return raw;
	if (typeof raw !== 'string') return null;
	const text = raw.trim().replace(/,/g, '');
	if (text.toLowerCase() === 'unavailable') return null;
	if (/^\d+$/.test(text)) return Number(text);
	const kilos = text.match(/^(\d+(?:\.\d+)?)k$/i);
	if (kilos) return Math.round(Number(kilos[1]) * 1000);
	const millions = text.match(/^(\d+(?:\.\d+)?)m$/i);
	if (millions) return Math.round(Number(millions[1]) * 1_000_000);
	return null;
}

function parseReleaseName(value) {
	if (typeof value !== 'string') return null;
	const text = value.trim();
	if (!text || /^unavailable$/i.test(text) || text === '—' || text === '-') return null;
	if (!/^v?[\w.+-]+$/.test(text)) return null;
	return text;
}

async function shieldsNumber(repo, kind, doFetch) {
	const result = await fetchJson(
		`https://img.shields.io/github/${kind}/${repo}.json`,
		{ Accept: 'application/json', 'User-Agent': 'almasix-orbit-docs' },
		doFetch,
	);
	return result.ok ? parseShieldNumber(result.data) : null;
}

async function shieldsRelease(repo, doFetch) {
	const result = await fetchJson(
		`https://img.shields.io/github/v/release/${repo}.json`,
		{ Accept: 'application/json', 'User-Agent': 'almasix-orbit-docs' },
		doFetch,
	);
	if (!result.ok || !result.data || typeof result.data !== 'object') return null;
	return parseReleaseName(result.data.message ?? result.data.value);
}

const emptyStats = () => ({ stars: null, forks: null, release: null, source: 'unavailable' });

/**
 * @param {string} repo `owner/name`
 * @param {typeof fetch} [doFetch]
 */
export async function fetchPublicRepoStats(repo, doFetch = fetch) {
	if (!repo || !REPO_RE.test(repo)) return emptyStats();
	if (cache.has(repo)) return cache.get(repo);

	const token = readToken();
	let repoResult = await fetchJson(
		`https://api.github.com/repos/${repo}`,
		githubHeaders(token),
		doFetch,
	);
	if (!repoResult.ok && token && [401, 403, 404].includes(repoResult.status)) {
		repoResult = await fetchJson(
			`https://api.github.com/repos/${repo}`,
			githubHeaders(''),
			doFetch,
		);
	}

	let releaseResult = await fetchJson(
		`https://api.github.com/repos/${repo}/releases/latest`,
		githubHeaders(token),
		doFetch,
	);
	if (!releaseResult.ok && token && [401, 403, 404].includes(releaseResult.status)) {
		releaseResult = await fetchJson(
			`https://api.github.com/repos/${repo}/releases/latest`,
			githubHeaders(''),
			doFetch,
		);
	}

	const body = repoResult.ok && repoResult.data && typeof repoResult.data === 'object' ? repoResult.data : null;
	let stars = typeof body?.stargazers_count === 'number' ? body.stargazers_count : null;
	let forks = typeof body?.forks_count === 'number' ? body.forks_count : null;
	let release = null;
	if (releaseResult.ok && releaseResult.data && typeof releaseResult.data === 'object') {
		release = parseReleaseName(releaseResult.data.tag_name);
	}

	let source = body ? 'github' : 'unavailable';
	if (stars == null || forks == null || !release) {
		const [shieldStars, shieldForks, shieldTag] = await Promise.all([
			stars == null ? shieldsNumber(repo, 'stars', doFetch) : null,
			forks == null ? shieldsNumber(repo, 'forks', doFetch) : null,
			!release ? shieldsRelease(repo, doFetch) : null,
		]);
		if (stars == null && shieldStars != null) {
			stars = shieldStars;
			source = 'shields';
		}
		if (forks == null && shieldForks != null) {
			forks = shieldForks;
			source = 'shields';
		}
		if (!release && shieldTag) {
			release = shieldTag;
			if (source === 'unavailable') source = 'shields';
		}
	}

	const stats = { stars, forks, release, source };
	cache.set(repo, stats);
	if (source !== 'github') {
		console.log(
			`GitHub stats ${repo}: stars=${stars ?? '—'} forks=${forks ?? '—'} release=${release ?? '—'} (${source})`,
		);
	}
	return stats;
}

/** Same shape the docs header chip expects from the Starlight theme. */
export function formatCount(n) {
	if (n >= 1000) {
		const k = n / 1000;
		return `${k >= 10 ? Math.round(k) : k.toFixed(1).replace(/\.0$/, '')}k`;
	}
	return String(n);
}

export async function getGitHubStats(repo) {
	const fallback = {
		stars: null,
		forks: null,
		release: null,
		repoUrl: repo ? `https://github.com/${repo}` : 'https://github.com/almasix-dev',
		releasesUrl: repo ? `https://github.com/${repo}/releases` : 'https://github.com/almasix-dev',
	};
	if (!repo || !REPO_RE.test(repo)) return fallback;
	const stats = await fetchPublicRepoStats(repo);
	return {
		...fallback,
		stars: stats.stars,
		forks: stats.forks,
		release: stats.release,
	};
}

/** Route the theme header's stats import at the resilient fetcher above. */
export function githubStatsThemeAlias(themeModuleUrl) {
	const target = fileURLToPath(themeModuleUrl);
	return {
		name: 'orbit-github-stats',
		enforce: 'pre',
		resolveId(source, importer) {
			if (!source || !importer) return null;
			const fromTheme =
				importer.includes('/@almasix/starlight-theme/') ||
				importer.includes('\\@almasix\\starlight-theme\\');
			if (!fromTheme) return null;
			const normalized = source.replaceAll('\\', '/');
			if (
				normalized === '../lib/github-stats' ||
				normalized.endsWith('/lib/github-stats') ||
				normalized.endsWith('/github-stats.ts')
			) {
				return target;
			}
			return null;
		},
	};
}
