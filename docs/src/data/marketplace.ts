import { createMarkdownProcessor } from '@astrojs/markdown-remark';
import { getCollection, type CollectionEntry } from 'astro:content';

import {
	githubRepoUrl,
	parseGithubRepo,
	pypiProjectUrl,
} from '../../scripts/marketplace-lib.mjs';
import { fetchGithubStars, fetchPypiInstalls } from './marketplace-stats';

/** Docs pages that live under `/plugins/` — a listing may not claim these. */
export const RESERVED_PLUGIN_SLUGS = [
	'authors',
	'categories',
	'develop',
	'feed',
	'get-listed',
	'guidelines',
	'overview',
	'paid',
	'paid-vs-free',
	'using',
];

export interface MarketplaceCategory {
	slug: string;
	label: string;
	description: string;
}

export interface MarketplaceAuthor {
	slug: string;
	name: string;
	bio: string;
	avatar?: string;
	website?: string;
	github?: string;
	sponsorUrl?: string;
}

export interface MarketplacePlugin {
	slug: string;
	name: string;
	summary: string;
	description: string;
	author: MarketplaceAuthor;
	categories: MarketplaceCategory[];
	orbitVersions: string[];
	isPaid: boolean;
	priceLabel: string;
	checkoutUrl?: string;
	package?: string;
	installCommand?: string;
	repository?: string;
	docsUrl?: string;
	homepage?: string;
	changelogUrl?: string;
	license?: string;
	keywords: string[];
	requiresPython?: string;
	thumbnail?: string;
	screenshots: { src: string; alt: string }[];
	darkMode: boolean;
	official: boolean;
	featured: boolean;
	publishedAt: Date;
	url: string;
	stars: number | null;
	installs: number | null;
	githubUrl?: string;
	pypiUrl?: string;
	githubRepo?: string;
}

function formatPrice(price: CollectionEntry<'plugins'>['data']['price']): string {
	if (price === 'free') return 'Free';
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: price.currency,
		minimumFractionDigits: Number.isInteger(price.amount) ? 0 : 2,
	}).format(price.amount);
}

async function loadCategories(): Promise<Map<string, MarketplaceCategory>> {
	const entries = await getCollection('pluginCategories');
	return new Map(
		entries.map((entry) => [
			entry.id,
			{ slug: entry.id, label: entry.data.label, description: entry.data.description },
		]),
	);
}

export async function getMarketplaceCategories(): Promise<MarketplaceCategory[]> {
	const categories = await loadCategories();
	return [...categories.values()].sort((a, b) => a.label.localeCompare(b.label));
}

async function loadAuthors(): Promise<Map<string, MarketplaceAuthor>> {
	const entries = await getCollection('pluginAuthors');
	return new Map(
		entries.map((entry) => [
			entry.data.slug,
			{
				slug: entry.data.slug,
				name: entry.data.name,
				bio: entry.data.bio,
				avatar: entry.data.avatar,
				website: entry.data.website,
				github: entry.data.github,
				sponsorUrl: entry.data.sponsor_url,
			},
		]),
	);
}

/**
 * Published listings, joined to their author and categories.
 *
 * Throws on a dangling reference so a bad submission fails the docs build
 * instead of rendering a half-empty card.
 */
export async function getMarketplacePlugins(): Promise<MarketplacePlugin[]> {
	const [categories, authors, entries] = await Promise.all([
		loadCategories(),
		loadAuthors(),
		getCollection('plugins'),
	]);

	const plugins = await Promise.all(
		entries
			.filter((entry) => entry.data.status === 'published')
			.map(async (entry) => {
				const data = entry.data;
				const author = authors.get(data.author);
				if (!author) {
					throw new Error(
						`Plugin "${data.slug}" references unknown author "${data.author}". ` +
							'Add src/data/marketplace/authors/<slug>.yaml first.',
					);
				}
				const githubRepo = data.github_repo || parseGithubRepo(data.repository ?? '');
				const [fetchedStars, fetchedInstalls] = await Promise.all([
					data.stars == null ? fetchGithubStars(githubRepo) : Promise.resolve(data.stars),
					data.installs == null ? fetchPypiInstalls(data.package) : Promise.resolve(data.installs),
				]);
				return {
					slug: data.slug,
					name: data.name,
					summary: data.summary,
					description: data.description,
					author,
					categories: data.categories.map((slug) => {
						const category = categories.get(slug);
						if (!category) {
							throw new Error(
								`Plugin "${data.slug}" uses unknown category "${slug}". ` +
									'Pick one from src/data/marketplace/categories.yaml.',
							);
						}
						return category;
					}),
					orbitVersions: data.orbit_versions,
					isPaid: data.price !== 'free',
					priceLabel: formatPrice(data.price),
					checkoutUrl: data.checkout_url,
					package: data.package,
					installCommand: data.package ? `pip install ${data.package}` : undefined,
					repository: data.repository,
					docsUrl: data.docs_url,
					homepage: data.homepage,
					changelogUrl: data.changelog_url,
					license: data.license,
					keywords: data.keywords ?? [],
					requiresPython: data.requires_python,
					thumbnail: data.thumbnail,
					screenshots: data.screenshots,
					darkMode: data.features.dark_mode,
					official: data.features.official,
					featured: data.features.featured,
					publishedAt: data.published_at,
					url: `/plugins/${data.slug}/`,
					stars: fetchedStars,
					installs: fetchedInstalls,
					githubRepo: githubRepo ?? undefined,
					githubUrl: githubRepo ? githubRepoUrl(githubRepo) : data.repository,
					pypiUrl: data.package ? pypiProjectUrl(data.package) : undefined,
				} satisfies MarketplacePlugin;
			}),
	);

	return plugins.sort((a, b) => b.publishedAt.getTime() - a.publishedAt.getTime());
}

/** Authors with at least one published listing, alphabetical. */
export async function getMarketplaceAuthors(): Promise<
	{ author: MarketplaceAuthor; plugins: MarketplacePlugin[] }[]
> {
	const plugins = await getMarketplacePlugins();
	const grouped = new Map<string, { author: MarketplaceAuthor; plugins: MarketplacePlugin[] }>();
	for (const plugin of plugins) {
		const group = grouped.get(plugin.author.slug) ?? { author: plugin.author, plugins: [] };
		group.plugins.push(plugin);
		grouped.set(plugin.author.slug, group);
	}
	return [...grouped.values()].sort((a, b) => a.author.name.localeCompare(b.author.name));
}

let processor: Awaited<ReturnType<typeof createMarkdownProcessor>> | undefined;

/** Render a listing's markdown `description` to HTML. */
export async function renderListingMarkdown(markdown: string): Promise<string> {
	processor ??= await createMarkdownProcessor({ gfm: true, smartypants: true });
	const { code } = await processor.render(markdown);
	return code;
}

/** Versions offered in the browse filter, newest first. */
export function collectOrbitVersions(plugins: MarketplacePlugin[]): string[] {
	const versions = new Set<string>();
	for (const plugin of plugins) {
		for (const version of plugin.orbitVersions) versions.add(version);
	}
	return [...versions].sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));
}

export function getRelatedPlugins(
	plugin: MarketplacePlugin,
	all: MarketplacePlugin[],
	limit = 3,
): MarketplacePlugin[] {
	const categorySlugs = new Set(plugin.categories.map((category) => category.slug));
	return all
		.filter((candidate) => candidate.slug !== plugin.slug)
		.map((candidate) => ({
			candidate,
			overlap: candidate.categories.filter((category) => categorySlugs.has(category.slug)).length,
		}))
		.filter((row) => row.overlap > 0)
		.sort((a, b) => b.overlap - a.overlap || b.candidate.publishedAt.getTime() - a.candidate.publishedAt.getTime())
		.slice(0, limit)
		.map((row) => row.candidate);
}

/** GitHub profile URL from a handle or an already-absolute URL. */
export function authorGithubHref(github: string): string {
	if (/^https?:\/\//i.test(github)) return github;
	return `https://github.com/${github.replace(/^@/, '')}`;
}

export function pluginToFeedItem(plugin: MarketplacePlugin) {
	return {
		slug: plugin.slug,
		name: plugin.name,
		summary: plugin.summary,
		url: plugin.url,
		author: {
			slug: plugin.author.slug,
			name: plugin.author.name,
		},
		categories: plugin.categories.map((category) => category.slug),
		orbit_versions: plugin.orbitVersions,
		price: plugin.isPaid ? plugin.priceLabel : 'free',
		package: plugin.package ?? null,
		repository: plugin.repository ?? null,
		docs_url: plugin.docsUrl ?? null,
		license: plugin.license ?? null,
		keywords: plugin.keywords,
		official: plugin.official,
		featured: plugin.featured,
		stars: plugin.stars,
		installs: plugin.installs,
		github_url: plugin.githubUrl ?? null,
		pypi_url: plugin.pypiUrl ?? null,
		published_at: plugin.publishedAt.toISOString().slice(0, 10),
	};
}
