/**
 * Fill baked-in GitHub em dashes after a docs build.
 *
 * The header chip and marketplace star counts are rendered while the site is
 * built. When that request fails, the HTML keeps "—". This pass writes the
 * live counts into both the current tree and the archived 0.x tree.
 */

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { formatStat, parseGithubRepo } from './marketplace-lib.mjs';
import { fetchPublicRepoStats, formatCount } from './github-public-stats.mjs';

const clientSource = readFileSync(
	join(dirname(fileURLToPath(import.meta.url)), 'github-stats-client.js'),
	'utf8',
);

const DASH = '(?:—|-|–)';

function githubRepoFromText(text) {
	if (!text) return null;
	const match = String(text).match(/https:\/\/github\.com\/[\w.-]+\/[\w.-]+/i);
	return match ? parseGithubRepo(match[0]) : null;
}

function chipRepo(html) {
	const match = html.match(
		/<a\b[^>]*href="(https:\/\/github\.com\/[^"]+)"[^>]*\btitle="GitHub stars"|<a\b[^>]*\btitle="GitHub stars"[^>]*href="(https:\/\/github\.com\/[^"]+)"/,
	);
	return githubRepoFromText(match?.[1] || match?.[2] || '');
}

function chipCountsMissing(html) {
	return (
		new RegExp(`title="GitHub stars"[\\s\\S]{0,800}?>\\s*${DASH}\\s*</span>`).test(html) ||
		new RegExp(`title="GitHub forks"[\\s\\S]{0,800}?>\\s*${DASH}\\s*</span>`).test(html)
	);
}

function emptyDataAttr(tag, name) {
	if (new RegExp(`\\b${name}="\\d`).test(tag)) return false;
	if (new RegExp(`\\b${name}='\\d`).test(tag)) return false;
	return new RegExp(`\\b${name}(?:=(["'])\\1)?(?=[\\s>/])`).test(tag);
}

function setDataAttr(tag, name, value) {
	if (!emptyDataAttr(tag, name)) return tag;
	if (tag.includes(`${name}=""`)) return tag.replace(`${name}=""`, `${name}="${value}"`);
	if (tag.includes(`${name}=''`)) return tag.replace(`${name}=''`, `${name}="${value}"`);
	return tag.replace(new RegExp(`\\b${name}(?=[\\s>/])`), `${name}="${value}"`);
}

function strippedText(fragment) {
	return fragment.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
}

function isDashText(text) {
	return text === '—' || text === '-' || text === '–';
}

/** True when a titled element's own text is still a placeholder dash. */
function titledElementHasDash(html, title, tag) {
	const pattern = new RegExp(`<${tag}\\b[^>]*\\btitle="${title}"[^>]*>([\\s\\S]*?)</${tag}>`, 'g');
	for (const match of html.matchAll(pattern)) {
		const text = strippedText(match[1]);
		if (isDashText(text)) return true;
		if (tag === 'li' && /^(?:—|-|–)(?:\s|$)/.test(text)) return true;
	}
	return false;
}

function countElementHasDash(html, attr, tag) {
	const pattern = new RegExp(`<${tag}\\b[^>]*\\b${attr}\\b[^>]*>([\\s\\S]*?)</${tag}>`, 'g');
	for (const match of html.matchAll(pattern)) {
		if (isDashText(strippedText(match[1]))) return true;
	}
	return false;
}

export function htmlHasMissingGithubStats(html) {
	if (titledElementHasDash(html, 'GitHub stars', 'a')) return true;
	if (titledElementHasDash(html, 'GitHub forks', 'a')) return true;
	if (titledElementHasDash(html, 'GitHub stars', 'li')) return true;
	if (countElementHasDash(html, 'data-star-count', 'span')) return true;
	if (countElementHasDash(html, 'data-star-count-page', 'strong')) return true;
	return false;
}

function reposNeedingStats(html) {
	const repos = new Set();
	const header = chipRepo(html);
	if (header && (chipCountsMissing(html) || !html.includes('gh-chip__release'))) repos.add(header);

	const cards = [...html.matchAll(/<li\b[^>]*\bdata-plugin\b[^>]*>/g)];
	for (let index = 0; index < cards.length; index += 1) {
		const open = cards[index][0];
		const start = cards[index].index + open.length;
		const end = index + 1 < cards.length ? cards[index + 1].index : html.length;
		const block = html.slice(start, end);
		const missing =
			emptyDataAttr(open, 'data-stars') &&
			new RegExp(`title="GitHub stars"[\\s\\S]{0,800}?>\\s*${DASH}\\s*</strong>`).test(block);
		if (!missing) continue;
		const search = open.match(/\bdata-search="([^"]*)"/);
		const fromSearch = githubRepoFromText(search?.[1] ?? '');
		const link = block.match(/href="(https:\/\/github\.com\/[^"]+)"[^>]*title="GitHub repository"/);
		const repo = fromSearch || githubRepoFromText(link?.[1] ?? '');
		if (repo) repos.add(repo);
	}

	for (const match of html.matchAll(/<button\b[^>]*\bdata-star-repo="([^"]+)"[^>]*>[\s\S]*?<\/button>/g)) {
		if (new RegExp(`data-star-count[^>]*>\\s*${DASH}\\s*</span>`).test(match[0])) repos.add(match[1]);
	}
	return repos;
}

function replaceDash(html, pattern, value) {
	if (value == null) return html;
	return html.replace(pattern, `$1${value}$2`);
}

function applyStats(html, statsByRepo) {
	let next = html;
	const header = chipRepo(next);
	const headerStats = header ? statsByRepo.get(header) : null;
	if (headerStats) {
		next = replaceDash(
			next,
			new RegExp(
				`(<a\\b[^>]*\\btitle="GitHub stars"[^>]*>[\\s\\S]*?<span\\b[^>]*>)\\s*${DASH}\\s*(</span>)`,
			),
			headerStats.stars == null ? null : formatCount(headerStats.stars),
		);
		next = replaceDash(
			next,
			new RegExp(
				`(<a\\b[^>]*\\btitle="GitHub forks"[^>]*>[\\s\\S]*?<span\\b[^>]*>)\\s*${DASH}\\s*(</span>)`,
			),
			headerStats.forks == null ? null : formatCount(headerStats.forks),
		);
		if (headerStats.release && !next.includes('gh-chip__release')) {
			const open = next.match(/<div class="gh-chip\b[^"]*"[^>]*aria-label="GitHub repository">/);
			if (open) {
				const scope = next.match(/class="gh-chip__part ([^"\s]+)"/);
				const scopeClass = scope ? ` ${scope[1]}` : '';
				const href = `https://github.com/${header}/releases`;
				const link = `<a class="gh-chip__part${scopeClass} gh-chip__release" href="${href}">${headerStats.release}</a>`;
				const at = open.index + open[0].length;
				next = next.slice(0, at) + link + next.slice(at);
			}
		}
	}

	const cards = [...next.matchAll(/<li\b[^>]*\bdata-plugin\b[^>]*>/g)];
	let cursor = 0;
	let rebuilt = '';
	for (let index = 0; index < cards.length; index += 1) {
		const open = cards[index][0];
		const start = cards[index].index;
		const openEnd = start + open.length;
		const end = index + 1 < cards.length ? cards[index + 1].index : next.length;
		const block = next.slice(openEnd, end);
		const search = open.match(/\bdata-search="([^"]*)"/);
		const link = block.match(/href="(https:\/\/github\.com\/[^"]+)"[^>]*title="GitHub repository"/);
		const repo = githubRepoFromText(search?.[1] ?? '') || githubRepoFromText(link?.[1] ?? '');
		const stats = repo ? statsByRepo.get(repo) : null;
		let nextOpen = open;
		let nextBlock = block;
		if (stats?.stars != null) {
			const label = formatStat(stats.stars);
			nextOpen = setDataAttr(open, 'data-stars', String(stats.stars));
			nextBlock = replaceDash(
				block,
				new RegExp(
					`(<li\\b[^>]*\\btitle="GitHub stars"[^>]*>[\\s\\S]*?<strong\\b[^>]*>)\\s*${DASH}\\s*(</strong>)`,
				),
				label,
			);
		}
		rebuilt += next.slice(cursor, start) + nextOpen + nextBlock;
		cursor = end;
	}
	if (cards.length) {
		next = rebuilt + next.slice(cursor);
	}

	next = next.replace(
		/<button\b[^>]*\bdata-star-repo="([^"]+)"[^>]*>[\s\S]*?<\/button>/g,
		(button, repo) => {
			const stats = statsByRepo.get(repo);
			if (stats?.stars == null) return button;
			const label = formatStat(stats.stars);
			let updated = setDataAttr(button, 'data-star-base', String(stats.stars));
			updated = replaceDash(
				updated,
				new RegExp(`(<span\\b[^>]*\\bdata-star-count[^>]*>)\\s*${DASH}\\s*(</span>)`),
				label,
			);
			return updated;
		},
	);

	const pageRepos = [...next.matchAll(/\bdata-star-repo="([^"]+)"/g)].map((match) => match[1]);
	const uniquePageRepos = [...new Set(pageRepos)];
	if (uniquePageRepos.length === 1) {
		const stars = statsByRepo.get(uniquePageRepos[0])?.stars;
		if (stars != null) {
			next = replaceDash(
				next,
				new RegExp(
					`(<strong\\b[^>]*\\bdata-star-count-page="[^"]*"[^>]*>)\\s*${DASH}\\s*(</strong>)`,
					'g',
				),
				formatStat(stars),
			);
		}
	}

	const summed = [...next.matchAll(/\bdata-stars="(\d+)"/g)].reduce(
		(total, match) => total + Number(match[1]),
		0,
	);
	if (summed > 0) {
		next = next.replace(
			new RegExp(
				`(<li(?![^>]*\\btitle=)[^>]*>[\\s\\S]*?<strong>)(?:0|${DASH})(</strong>\\s*<span class="market-stats-label">Stars</span>)`,
			),
			`$1${formatStat(summed)}$2`,
		);
	}
	return next;
}

export async function fillGithubStatsHtml(html, loadStats = fetchPublicRepoStats) {
	const repos = reposNeedingStats(html);
	if (!repos.size) return html;
	const statsByRepo = new Map();
	await Promise.all(
		[...repos].map(async (repo) => {
			try {
				statsByRepo.set(repo, await loadStats(repo));
			} catch {
				statsByRepo.set(repo, { stars: null, forks: null, release: null, source: 'unavailable' });
			}
		}),
	);
	const filled = applyStats(html, statsByRepo);
	if (!htmlHasMissingGithubStats(filled) || filled.includes('data-orbit-github-stats')) return filled;
	const script = `<script data-orbit-github-stats>${clientSource}</script>`;
	if (filled.includes('</body>')) return filled.replace('</body>', `${script}</body>`);
	return `${filled}${script}`;
}
