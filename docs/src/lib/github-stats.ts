/** Build-time GitHub repo stats for the docs header chip. */

export type GitHubStats = {
	stars: number | null;
	forks: number | null;
	release: string | null;
	repoUrl: string;
	releasesUrl: string;
};

const REPO = 'almasix-dev/almasix-orbit';
const REPO_URL = `https://github.com/${REPO}`;
const RELEASES_URL = `${REPO_URL}/releases`;

let cached: GitHubStats | null = null;

async function fetchJson(url: string): Promise<unknown | null> {
	try {
		const res = await fetch(url, {
			headers: {
				Accept: 'application/vnd.github+json',
				'User-Agent': 'almasix-orbit-docs',
			},
		});
		if (!res.ok) return null;
		return await res.json();
	} catch {
		return null;
	}
}

export async function getGitHubStats(): Promise<GitHubStats> {
	if (cached) return cached;

	const fallback: GitHubStats = {
		stars: null,
		forks: null,
		release: null,
		repoUrl: REPO_URL,
		releasesUrl: RELEASES_URL,
	};

	const [repo, release] = await Promise.all([
		fetchJson(`https://api.github.com/repos/${REPO}`),
		fetchJson(`https://api.github.com/repos/${REPO}/releases/latest`),
	]);

	const stats: GitHubStats = { ...fallback };

	if (repo && typeof repo === 'object') {
		const r = repo as Record<string, unknown>;
		if (typeof r.stargazers_count === 'number') stats.stars = r.stargazers_count;
		if (typeof r.forks_count === 'number') stats.forks = r.forks_count;
	}

	if (release && typeof release === 'object') {
		const rel = release as Record<string, unknown>;
		if (typeof rel.tag_name === 'string' && rel.tag_name) {
			stats.release = rel.tag_name;
		}
	}

	cached = stats;
	return stats;
}

export function formatCount(n: number): string {
	if (n >= 1000) {
		const k = n / 1000;
		return `${k >= 10 ? Math.round(k) : k.toFixed(1).replace(/\.0$/, '')}k`;
	}
	return String(n);
}
