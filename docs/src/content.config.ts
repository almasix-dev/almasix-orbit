import { defineCollection, z } from 'astro:content';
import { file, glob } from 'astro/loaders';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

const marketplaceBase = './.marketplace';

/** `free`, or a price shown on the listing with an external checkout. */
const price = z.union([
	z.literal('free'),
	z.object({
		amount: z.number().positive(),
		currency: z.string().regex(/^[A-Z]{3}$/, 'Use an ISO 4217 code such as USD or EUR'),
	}),
]);

const screenshot = z.object({
	src: z.string(),
	alt: z.string(),
});

const pluginCategories = defineCollection({
	loader: file(`${marketplaceBase}/categories.yaml`),
	schema: z.object({
		label: z.string(),
		description: z.string(),
	}),
});

const pluginAuthors = defineCollection({
	loader: glob({ pattern: '**/*.yaml', base: `${marketplaceBase}/authors` }),
	schema: z.object({
		name: z.string(),
		slug: z.string().regex(/^[a-z0-9-]+$/),
		bio: z.string(),
		avatar: z.string().optional(),
		website: z.string().url().optional(),
		github: z.string().optional(),
		sponsor_url: z.string().url().optional(),
	}),
});

const plugins = defineCollection({
	loader: glob({ pattern: '**/*.yaml', base: `${marketplaceBase}/plugins` }),
	schema: z
		.object({
			name: z.string(),
			slug: z.string().regex(/^[a-z0-9-]+$/),
			summary: z.string().max(200),
			description: z.string(),
			author: z.string().regex(/^[a-z0-9-]+$/),
			categories: z.array(z.string()).min(1),
			orbit_versions: z.array(z.string()).min(1),
			price,
			checkout_url: z.string().url().optional(),
			package: z.string().optional(),
			repository: z.string().url().optional(),
			docs_url: z.string().url().optional(),
			homepage: z.string().url().optional(),
			changelog_url: z.string().url().optional(),
			license: z.string().optional(),
			keywords: z.array(z.string()).default([]),
			requires_python: z.string().optional(),
			github_repo: z
				.string()
				.regex(/^[\w.-]+\/[\w.-]+$/, 'Use GitHub owner/repo, e.g. acme/orbit-kit')
				.optional(),
			stars: z.number().int().nonnegative().optional(),
			installs: z.number().int().nonnegative().optional(),
			thumbnail: z.string().optional(),
			screenshots: z.array(screenshot).default([]),
			features: z
				.object({
					dark_mode: z.boolean().default(false),
					official: z.boolean().default(false),
					featured: z.boolean().default(false),
				})
				.default({}),
			status: z.enum(['published', 'draft', 'archived']).default('published'),
			published_at: z.coerce.date(),
		})
		.superRefine((plugin, ctx) => {
			if (plugin.price !== 'free' && !plugin.checkout_url) {
				ctx.addIssue({
					code: z.ZodIssueCode.custom,
					path: ['checkout_url'],
					message: 'Paid plugins must provide a `checkout_url` buyers can complete a purchase on.',
				});
			}
			if (plugin.price === 'free' && !plugin.package && !plugin.repository) {
				ctx.addIssue({
					code: z.ZodIssueCode.custom,
					path: ['package'],
					message: 'Free plugins must provide a `package` (PyPI name) or a public `repository`.',
				});
			}
			if (plugin.features.official && plugin.author !== 'almasix') {
				ctx.addIssue({
					code: z.ZodIssueCode.custom,
					path: ['features', 'official'],
					message: '`features.official` is reserved for listings whose author is `almasix`.',
				});
			}
		}),
});

const articles = defineCollection({
	loader: glob({ pattern: '**/*.yaml', base: `${marketplaceBase}/articles` }),
	schema: z
		.object({
			name: z.string(),
			slug: z.string().regex(/^[a-z0-9-]+$/),
			summary: z.string().max(200),
			body: z.string(),
			author: z.string().regex(/^[a-z0-9-]+$/),
			tags: z.array(z.string()).default([]),
			related_plugins: z.array(z.string().regex(/^[a-z0-9-]+$/)).default([]),
			thumbnail: z.string().optional(),
			images: z.array(screenshot).default([]),
			canonical_url: z.string().url().optional(),
			features: z
				.object({
					official: z.boolean().default(false),
					featured: z.boolean().default(false),
				})
				.default({}),
			status: z.enum(['published', 'draft', 'archived']).default('published'),
			published_at: z.coerce.date(),
		})
		.superRefine((article, ctx) => {
			if (article.features.official && article.author !== 'almasix') {
				ctx.addIssue({
					code: z.ZodIssueCode.custom,
					path: ['features', 'official'],
					message: '`features.official` is reserved for listings whose author is `almasix`.',
				});
			}
		}),
});

export const collections = {
	docs: defineCollection({ loader: docsLoader(), schema: docsSchema() }),
	pluginCategories,
	pluginAuthors,
	plugins,
	articles,
};
