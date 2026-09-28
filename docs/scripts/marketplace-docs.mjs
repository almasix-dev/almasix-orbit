/**
 * Resolve marketplace listing documentation from `docs_url` at build time.
 *
 * GitHub repository and raw Markdown URLs are fetched and rendered on the
 * listing page alongside the YAML `description`. Other URLs stay link-only.
 *
 * Relative image paths in GitHub READMEs are rewritten to
 * `raw.githubusercontent.com` so they render on the marketplace host.
 */

import { parseGithubRepo } from './marketplace-lib.mjs';
import { stripVersionPrefix } from '../src/versions.mjs';

const README_NAMES = ['README.md', 'Readme.md', 'readme.md'];
const README_BRANCHES = ['main', 'master'];

function normalizeListingPath(pathname) {
	const raw = stripVersionPrefix(String(pathname ?? '/').split('?')[0].split('#')[0]);
	if (raw === '/') return '/';
	return raw.endsWith('/') ? raw : `${raw}/`;
}

/** True when `docs_url` points at this listing page (self-referential). */
export function isListingDocsUrl(docsUrl, listingPath) {
	if (!docsUrl || !listingPath) return false;
	try {
		const url = new URL(docsUrl);
		const docsPath = normalizeListingPath(url.pathname);
		const listPath = normalizeListingPath(
			listingPath.startsWith('http') ? new URL(listingPath).pathname : listingPath,
		);
		return docsPath === listPath;
	} catch {
		return false;
	}
}

/** `owner/repo` from a GitHub repo, blob, or tree URL. */
export function githubRepoFromDocsUrl(docsUrl) {
	if (!docsUrl || typeof docsUrl !== 'string') return null;
	const withoutHash = docsUrl.split('#')[0];
	const direct = parseGithubRepo(withoutHash);
	if (direct) return direct;
	const blob = withoutHash.match(/^https:\/\/github\.com\/([\w.-]+)\/([\w.-]+)\/blob\//i);
	if (blob) return `${blob[1]}/${blob[2]}`;
	const tree = withoutHash.match(/^https:\/\/github\.com\/([\w.-]+)\/([\w.-]+)\/tree\//i);
	if (tree) return `${tree[1]}/${tree[2]}`;
	return null;
}

function githubHeaders() {
	return {
		Accept: 'application/vnd.github+json',
		'User-Agent': 'almasix-orbit-docs',
		'X-GitHub-Api-Version': '2022-11-28',
	};
}

/** Branch name from a raw.githubusercontent.com or github.com/blob URL. */
export function branchFromGithubContentUrl(url) {
	if (!url || typeof url !== 'string') return null;
	const raw = url.match(
		/^https:\/\/raw\.githubusercontent\.com\/[\w.-]+\/[\w.-]+\/([^/]+)\//i,
	);
	if (raw) return decodeURIComponent(raw[1]);
	const blob = url.match(/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/blob\/([^/]+)\//i);
	if (blob) return decodeURIComponent(blob[1]);
	return null;
}

function isAbsoluteOrSpecialUrl(href) {
	return /^(?:[a-z][a-z0-9+.-]*:|\/\/|#|data:)/i.test(href);
}

/** Turn a repo-relative path into a raw.githubusercontent.com URL. */
export function githubRawUrl(repo, branch, path) {
	const cleaned = String(path ?? '')
		.trim()
		.replace(/^\.\//, '')
		.replace(/^\//, '');
	if (!repo || !branch || !cleaned || isAbsoluteOrSpecialUrl(cleaned)) return null;
	return `https://raw.githubusercontent.com/${repo}/${branch}/${cleaned}`;
}

/**
 * Rewrite relative Markdown/HTML image URLs so they load from GitHub raw content
 * when the README is embedded on orbit.almasix.com.
 */
export function rewriteGithubReadmeMedia(markdown, repo, branch = 'main') {
	if (!markdown || !repo) return markdown ?? '';
	const ref = branch || 'main';

	const rewriteHref = (href) => {
		const trimmed = String(href ?? '').trim();
		if (!trimmed || isAbsoluteOrSpecialUrl(trimmed)) {
			// github.com/owner/repo/blob/branch/path → raw for images
			const blobImg = trimmed.match(
				/^https:\/\/github\.com\/([\w.-]+\/[\w.-]+)\/blob\/([^/]+)\/(.+\.(?:png|jpe?g|gif|webp|svg|avif|bmp|ico))(?:\?.*)?$/i,
			);
			if (blobImg) {
				return `https://raw.githubusercontent.com/${blobImg[1]}/${blobImg[2]}/${blobImg[3]}`;
			}
			return trimmed;
		}
		return githubRawUrl(repo, ref, trimmed) ?? trimmed;
	};

	let out = String(markdown);
	// ![alt](path) and ![alt](path "title")
	out = out.replace(/!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g, (full, alt, href) => {
		const next = rewriteHref(href);
		return next === href ? full : `![${alt}](${next})`;
	});
	// <img src="path"> / <img src='path'>
	out = out.replace(
		/(<img\b[^>]*?\bsrc\s*=\s*)(["'])([^"']+)\2/gi,
		(full, prefix, quote, href) => {
			const next = rewriteHref(href);
			return next === href ? full : `${prefix}${quote}${next}${quote}`;
		},
	);
	return out;
}

/** Fetch the default-branch README for a GitHub repository. */
export async function fetchGithubReadme(repo, doFetch = fetch) {
	if (!repo) return null;
	try {
		const meta = await doFetch(`https://api.github.com/repos/${repo}/readme`, {
			headers: githubHeaders(),
		});
		if (meta.ok) {
			const data = await meta.json();
			if (typeof data.download_url === 'string') {
				const body = await doFetch(data.download_url);
				if (body.ok) {
					const text = await body.text();
					const branch =
						branchFromGithubContentUrl(data.download_url) ||
						branchFromGithubContentUrl(data.html_url) ||
						'main';
					return rewriteGithubReadmeMedia(text, repo, branch);
				}
			}
		}
	} catch {
		// fall through to raw.githubusercontent.com
	}
	for (const branch of README_BRANCHES) {
		for (const name of README_NAMES) {
			const url = `https://raw.githubusercontent.com/${repo}/${branch}/${name}`;
			try {
				const response = await doFetch(url);
				if (response.ok) {
					const text = await response.text();
					return rewriteGithubReadmeMedia(text, repo, branch);
				}
			} catch {
				// try next branch / filename
			}
		}
	}
	return null;
}

async function fetchRawMarkdownUrl(url, doFetch) {
	try {
		const response = await doFetch(url);
		if (!response.ok) return null;
		const type = response.headers.get('content-type') ?? '';
		if (!type.includes('text/markdown') && !type.includes('text/plain') && !url.endsWith('.md')) {
			return null;
		}
		const text = await response.text();
		const repoMatch = url.match(
			/^https:\/\/raw\.githubusercontent\.com\/([\w.-]+\/[\w.-]+)\/([^/]+)\//i,
		);
		if (repoMatch) {
			return rewriteGithubReadmeMedia(text, repoMatch[1], decodeURIComponent(repoMatch[2]));
		}
		return text;
	} catch {
		return null;
	}
}

/**
 * Markdown body for a listing's `docs_url`, or null when the URL is
 * self-referential, unsupported, or unreachable.
 */
export async function fetchListingDocsMarkdown(docsUrl, listingPath, doFetch = fetch) {
	if (!docsUrl || isListingDocsUrl(docsUrl, listingPath)) return null;

	const repo = githubRepoFromDocsUrl(docsUrl);
	if (repo) return fetchGithubReadme(repo, doFetch);

	const withoutHash = docsUrl.split('#')[0];
	if (/^https:\/\/raw\.githubusercontent\.com\/.+\.md$/i.test(withoutHash)) {
		return fetchRawMarkdownUrl(withoutHash, doFetch);
	}

	return null;
}
