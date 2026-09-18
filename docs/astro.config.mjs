// @ts-check
import { readFileSync } from 'node:fs';

import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

const base = '/';

/** Section roots linked from the landing page → first real doc page. */
const sectionRedirects = Object.fromEntries(
	[
		['forms', 'forms/overview'],
		['tables', 'tables/overview'],
		['tables/columns', 'tables/columns/overview'],
		['tables/filters', 'tables/filters/overview'],
		['schemas', 'schemas/overview'],
		['resources', 'resources/overview'],
		['actions', 'actions/overview'],
		['infolists', 'infolists/overview'],
		['notifications', 'notifications/overview'],
		['widgets', 'widgets/overview'],
		['query-builder', 'query-builder/overview'],
		['support', 'support/overview'],
		['navigation', 'navigation/overview'],
		['users', 'users/overview'],
		['testing', 'testing/overview'],
		['panels', 'panels/configuration'],
		['getting-started', 'getting-started/installation'],
		['components', 'components/form'],
		['prologue', 'prologue/versions'],
	].flatMap(([from, to]) => [
		[`/${from}`, `/${to}`],
		[`/${from}/`, `/${to}/`],
	]),
);

// https://astro.build/config
export default defineConfig({
	site: 'https://orbit.almasix.com',
	base,
	devToolbar: { enabled: false },
	redirects: sectionRedirects,
	integrations: [
		starlight({
			title: 'Orbit',
			description:
				'Server-driven admin UI for Almasix — panels, resources, forms, tables, and more on Conduit + Alpine.',
			logo: {
				light: './src/assets/almasix-banner-light.svg',
				dark: './src/assets/almasix-banner-dark.svg',
				alt: 'Almasix',
				replacesTitle: true,
			},
			favicon: '/favicon.svg',
			social: [
				{
					icon: 'github',
					label: 'GitHub',
					href: 'https://github.com/almasix-dev/almasix-orbit',
				},
			],
			editLink: {
				baseUrl: 'https://github.com/almasix-dev/almasix-orbit/edit/main/docs/',
			},
			customCss: ['./src/styles/custom.css', './src/styles/landing.css'],
			components: {
				Header: './src/components/Header.astro',
				Hero: './src/components/Hero.astro',
				PageFrame: './src/components/PageFrame.astro',
				SiteTitle: './src/components/SiteTitle.astro',
				ThemeSelect: './src/components/ThemeSelect.astro',
			},
			expressiveCode: {
				// Vitesse pair tracks the Starlight UI theme — soft, high-legibility
				// on both light and dark pages (better than a single dark-only theme).
				themes: ['vitesse-dark', 'vitesse-light'],
				useStarlightDarkModeSwitch: true,
				useStarlightUiThemeColors: false,
				// Must stay true on Astro 7: inlining can break code-frame CSS.
				emitExternalStylesheet: true,
				styleOverrides: {
					borderRadius: '0.85rem',
					borderWidth: '1px',
					codeFontFamily: "'JetBrains Mono', ui-monospace, monospace",
					codeFontSize: '0.9rem',
					frames: {
						shadowColor: 'rgba(0, 0, 0, 0.22)',
					},
				},
			},
			head: [
				{
					tag: 'link',
					attrs: { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
				},
				{
					tag: 'link',
					attrs: {
						rel: 'preconnect',
						href: 'https://fonts.gstatic.com',
						crossorigin: true,
					},
				},
				{
					tag: 'script',
					content: readFileSync('./src/scripts/sidebar-accordion.js', 'utf8'),
				},
				{
					tag: 'script',
					content: readFileSync('./src/scripts/hero-slides.js', 'utf8'),
				},
				{
					tag: 'script',
					content: readFileSync('./src/scripts/example-lightbox.js', 'utf8'),
				},
				{
					tag: 'meta',
					attrs: { property: 'og:image', content: 'https://orbit.almasix.com/og.png' },
				},
				{
					tag: 'meta',
					attrs: { property: 'og:image:width', content: '1200' },
				},
				{
					tag: 'meta',
					attrs: { property: 'og:image:height', content: '630' },
				},
				{
					tag: 'meta',
					attrs: { property: 'og:image:alt', content: 'Almasix Orbit — Almasix' },
				},
				{
					tag: 'meta',
					attrs: { name: 'twitter:image', content: 'https://orbit.almasix.com/og.png' },
				},
				{
					tag: 'meta',
					attrs: { name: 'theme-color', content: '#F1511B' },
				},
				{
					tag: 'script',
					attrs: { type: 'application/ld+json' },
					content:
						'{"@context": "https://schema.org", "@graph": [{"@type": "WebSite", "@id": "https://orbit.almasix.com/#website", "url": "https://orbit.almasix.com/", "name": "Almasix Orbit", "description": "Server-driven admin UI for Almasix \\u2014 panels, resources, forms, and tables on Conduit + Alpine.", "publisher": {"@id": "https://almasix.com/#organization"}, "inLanguage": "en"}, {"@type": "SoftwareApplication", "@id": "https://orbit.almasix.com/#software", "name": "Almasix Orbit", "applicationCategory": "DeveloperApplication", "url": "https://orbit.almasix.com/", "isPartOf": {"@id": "https://almasix.com/#software"}, "publisher": {"@id": "https://almasix.com/#organization"}}]}',
				},
			],
			sidebar: [
				{ label: 'Home', slug: 'index' },
				{
					label: 'Prologue',
					collapsed: false,
					items: [
						{ label: 'Documentation versions', slug: 'prologue/versions' },
						{ label: 'Release notes', slug: 'prologue/release-notes' },
					],
				},
				{
					label: 'Getting started',
					collapsed: true,
					items: [
						{ label: 'Installation', slug: 'getting-started/installation' },
						{ label: 'Quick start', slug: 'getting-started/quick-start' },
					],
				},
				{
					label: 'Resources',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'resources/overview' },
						{ label: 'Listing records', slug: 'resources/listing-records' },
						{ label: 'Creating records', slug: 'resources/creating-records' },
						{ label: 'Editing records', slug: 'resources/editing-records' },
						{ label: 'Viewing records', slug: 'resources/viewing-records' },
						{ label: 'Managing relationships', slug: 'resources/managing-relationships' },
						{ label: 'Global search', slug: 'resources/global-search' },
						{ label: 'Resource pages', slug: 'resources/pages' },
					],
				},
				{
					label: 'Tables',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'tables/overview' },
						{
							label: 'Columns',
							collapsed: true,
							items: [
								{ label: 'Overview', slug: 'tables/columns/overview' },
								{ label: 'Text column', slug: 'tables/columns/text' },
								{ label: 'Icon column', slug: 'tables/columns/icon' },
								{ label: 'Image column', slug: 'tables/columns/image' },
								{ label: 'Color column', slug: 'tables/columns/color' },
								{ label: 'Select column', slug: 'tables/columns/select' },
								{ label: 'Toggle column', slug: 'tables/columns/toggle' },
								{ label: 'Text input column', slug: 'tables/columns/text-input' },
								{ label: 'Checkbox column', slug: 'tables/columns/checkbox' },
								{ label: 'Badge column', slug: 'tables/columns/badge' },
								{ label: 'Boolean column', slug: 'tables/columns/boolean' },
								{ label: 'Tags column', slug: 'tables/columns/tags' },
								{ label: 'View column', slug: 'tables/columns/view' },
								{ label: 'Column group', slug: 'tables/columns/column-group' },
							],
						},
						{
							label: 'Filters',
							collapsed: true,
							items: [
								{ label: 'Overview', slug: 'tables/filters/overview' },
							],
						},
						{ label: 'Actions', slug: 'tables/actions' },
						{ label: 'Layout', slug: 'tables/layout' },
						{ label: 'Summaries', slug: 'tables/summaries' },
						{ label: 'Grouping rows', slug: 'tables/grouping' },
					],
				},
				{
					label: 'Schemas',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'schemas/overview' },
						{ label: 'Layouts', slug: 'schemas/layouts' },
						{ label: 'Grid', slug: 'schemas/grid' },
						{ label: 'Flex', slug: 'schemas/flex' },
						{ label: 'Group', slug: 'schemas/group' },
						{ label: 'Split', slug: 'schemas/split' },
						{ label: 'Fieldset', slug: 'schemas/fieldset' },
						{ label: 'Sections', slug: 'schemas/sections' },
						{ label: 'Tabs', slug: 'schemas/tabs' },
						{ label: 'Wizards', slug: 'schemas/wizards' },
						{ label: 'Callouts', slug: 'schemas/callouts' },
						{ label: 'Empty states', slug: 'schemas/empty-states' },
						{ label: 'Prime components', slug: 'schemas/primes' },
					],
				},
				{
					label: 'Forms',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'forms/overview' },
						{ label: 'Text input', slug: 'forms/text-input' },
						{ label: 'Select', slug: 'forms/select' },
						{ label: 'Checkbox', slug: 'forms/checkbox' },
						{ label: 'Toggle', slug: 'forms/toggle' },
						{ label: 'Checkbox list', slug: 'forms/checkbox-list' },
						{ label: 'Radio', slug: 'forms/radio' },
						{ label: 'Date-time picker', slug: 'forms/date-time-picker' },
						{ label: 'Date picker', slug: 'forms/date-picker' },
						{ label: 'Time picker', slug: 'forms/time-picker' },
						{ label: 'File upload', slug: 'forms/file-upload' },
						{ label: 'Rich editor', slug: 'forms/rich-editor' },
						{ label: 'Markdown editor', slug: 'forms/markdown-editor' },
						{ label: 'Repeater', slug: 'forms/repeater' },
						{ label: 'Builder', slug: 'forms/builder' },
						{ label: 'Tags input', slug: 'forms/tags-input' },
						{ label: 'Textarea', slug: 'forms/textarea' },
						{ label: 'Key-value', slug: 'forms/key-value' },
						{ label: 'Color picker', slug: 'forms/color-picker' },
						{ label: 'Money input', slug: 'forms/money-input' },
						{ label: 'Toggle buttons', slug: 'forms/toggle-buttons' },
						{ label: 'Slider', slug: 'forms/slider' },
						{ label: 'Code editor', slug: 'forms/code-editor' },
						{ label: 'Hidden', slug: 'forms/hidden' },
						{ label: 'Multi-select', slug: 'forms/multi-select' },
						{ label: 'Morph-to select', slug: 'forms/morph-to-select' },
						{ label: 'Table select', slug: 'forms/table-select' },
						{ label: 'Modal table select', slug: 'forms/modal-table-select' },
						{ label: 'Relationship repeater', slug: 'forms/relationship-repeater' },
						{ label: 'One-time code input', slug: 'forms/one-time-code-input' },
						{ label: 'Placeholder', slug: 'forms/placeholder' },
						{ label: 'View field', slug: 'forms/view-field' },
						{ label: 'Validation', slug: 'forms/validation' },
						{ label: 'Custom fields', slug: 'forms/custom-fields' },
						{ label: 'Closures', slug: 'forms/closures' },
					],
				},
				{
					label: 'Infolists',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'infolists/overview' },
					],
				},
				{
					label: 'Actions',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'actions/overview' },
						{ label: 'Modals', slug: 'actions/modals' },
						{ label: 'Grouping actions', slug: 'actions/grouping-actions' },
						{ label: 'Create action', slug: 'actions/create' },
						{ label: 'Edit action', slug: 'actions/edit' },
						{ label: 'View action', slug: 'actions/view' },
						{ label: 'Delete action', slug: 'actions/delete' },
						{ label: 'Replicate action', slug: 'actions/replicate' },
						{ label: 'Force-delete action', slug: 'actions/force-delete' },
						{ label: 'Restore action', slug: 'actions/restore' },
						{ label: 'Import action', slug: 'actions/import' },
						{ label: 'Export action', slug: 'actions/export' },
					],
				},
				{
					label: 'Notifications',
					collapsed: true,
					items: [{ label: 'Overview', slug: 'notifications/overview' }],
				},
				{
					label: 'Widgets',
					collapsed: true,
					items: [{ label: 'Overview', slug: 'widgets/overview' }],
				},
				{
					label: 'Panel configuration',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'panels/configuration' },
						{ label: 'Actions in the panel', slug: 'panels/actions' },
					],
				},
				{
					label: 'Navigation',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'navigation/overview' },
						{ label: 'Custom pages', slug: 'navigation/custom-pages' },
						{ label: 'User menu', slug: 'navigation/user-menu' },
						{ label: 'Clusters', slug: 'navigation/clusters' },
					],
				},
				{
					label: 'Users',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'users/overview' },
						{ label: 'Multi-factor authentication', slug: 'users/multi-factor-authentication' },
						{ label: 'Multi-tenancy', slug: 'users/tenancy' },
					],
				},
				{
					label: 'Support',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'support/overview' },
						{ label: 'Closures & evaluate', slug: 'support/closures' },
					],
				},
				{
					label: 'Query builder',
					collapsed: true,
					items: [{ label: 'Overview', slug: 'query-builder/overview' }],
				},
				{
					label: 'Components',
					collapsed: true,
					items: [
						{ label: 'Rendering a form', slug: 'components/form' },
						{ label: 'Rendering a table', slug: 'components/table' },
					],
				},
				{
					label: 'Testing',
					collapsed: true,
					items: [{ label: 'Overview', slug: 'testing/overview' }],
				},
				{
					label: 'Digging deeper',
					collapsed: true,
					items: [
						{ label: 'Configuration & assets', slug: 'configuration' },
						{ label: 'Packages', slug: 'packages' },
						{ label: 'Features', slug: 'features' },
					],
				},
			],

		}),
	],
});
