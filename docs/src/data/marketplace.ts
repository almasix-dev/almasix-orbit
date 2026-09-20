import { createMarkdownProcessor } from '@astrojs/markdown-remark';
import { getCollection, type CollectionEntry } from 'astro:content';

/** Docs pages that live under `/plugins/` — a listing may not claim these. */
export const RESERVED_PLUGIN_SLUGS = [
	'authors',
	'develop',
	'get-listed',
	'guidelines',
	'overview',
	'paid-vs-free',
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
	thumbnail?: string;
	screenshots: { src: string; alt: string }[];
	darkMode: boolean;
	official: boolean;
	featured: boolean;
	publishedAt: Date;
	url: string;
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

	const plugins = entries
		.filter((entry) => entry.data.status === 'published')
		.map((entry) => {
			const data = entry.data;
			const author = authors.get(data.author);
			if (!author) {
				throw new Error(
					`Plugin "${data.slug}" references unknown author "${data.author}". ` +
						'Add src/data/marketplace/authors/<slug>.yaml first.',
				);
			}
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
				thumbnail: data.thumbnail,
				screenshots: data.screenshots,
				darkMode: data.features.dark_mode,
				official: data.features.official,
				featured: data.features.featured,
				publishedAt: data.published_at,
				url: `/plugins/${data.slug}/`,
			} satisfies MarketplacePlugin;
		});

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
