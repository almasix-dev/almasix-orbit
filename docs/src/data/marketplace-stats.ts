/** Live GitHub / PyPI stats for marketplace cards. Failures become `null`. */

import { fetchPublicRepoStats } from '../../scripts/github-public-stats.mjs';

const starCache = new Map<string, number | null>();
const installCache = new Map<string, number | null>();

export async function fetchGithubStars(repo: string | null | undefined): Promise<number | null> {
	if (!repo) return null;
	if (starCache.has(repo)) return starCache.get(repo) ?? null;
	try {
		const stats = await fetchPublicRepoStats(repo);
		const stars = typeof stats.stars === 'number' ? stats.stars : null;
		starCache.set(repo, stars);
		return stars;
	} catch {
		starCache.set(repo, null);
		return null;
	}
}

/** Last-month downloads from pypistats (best public proxy for “installs”). */
export async function fetchPypiInstalls(pkg: string | null | undefined): Promise<number | null> {
	if (!pkg) return null;
	if (installCache.has(pkg)) return installCache.get(pkg) ?? null;
	try {
		const response = await fetch(
			`https://pypistats.org/api/packages/${encodeURIComponent(pkg)}/recent`,
		);
		if (!response.ok) {
			installCache.set(pkg, null);
			return null;
		}
		const data = (await response.json()) as { data?: { last_month?: unknown } };
		const month = data.data?.last_month;
		const installs = typeof month === 'number' ? month : null;
		installCache.set(pkg, installs);
		return installs;
	} catch {
		installCache.set(pkg, null);
		return null;
	}
}
