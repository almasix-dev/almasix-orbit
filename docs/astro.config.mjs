// @ts-check
import { readFileSync } from 'node:fs';

import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

const base = '/';

// https://astro.build/config
export default defineConfig({
	site: 'https://orbit.almasix.com',
	base,
	devToolbar: { enabled: false },
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
				themes: ['one-dark-pro'],
				useStarlightDarkModeSwitch: false,
				useStarlightUiThemeColors: false,
				// Must stay true on Astro 7: inlining can break code-frame CSS.
				emitExternalStylesheet: true,
				styleOverrides: {
					borderRadius: '0.85rem',
					borderWidth: '1px',
					codeFontFamily: "'JetBrains Mono', ui-monospace, monospace",
					codeFontSize: '0.9rem',
					codeBackground: '#282c34',
					codeForeground: '#abb2bf',
					frames: {
						shadowColor: 'rgba(0, 0, 0, 0.4)',
						editorBackground: '#282c34',
						terminalBackground: '#282c34',
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
					label: 'Panels',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'panels' },
						{ label: 'Resources', slug: 'resources' },
						{ label: 'Pages', slug: 'pages' },
						{ label: 'Relation managers', slug: 'relation-managers' },
						{ label: 'Navigation', slug: 'panels/navigation' },
						{ label: 'Actions in the panel', slug: 'panels/actions' },
					],
				},
				{
					label: 'Support',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'support' },
						{ label: 'Closures & evaluate', slug: 'support/closures' },
					],
				},
				{
					label: 'Schemas',
					collapsed: true,
					items: [
						{ label: 'Schemas & layouts', slug: 'schemas' },
					],
				},
				{
					label: 'Forms',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'forms' },
						{ label: 'Standalone use', slug: 'forms/standalone' },
						{ label: 'Closures', slug: 'forms/closures' },
						{
							label: 'Field types',
							collapsed: true,
							items: [
						{ label: 'Builder', slug: 'forms/fields/builder' },
						{ label: 'CheckboxList', slug: 'forms/fields/checkbox-list' },
						{ label: 'Checkbox', slug: 'forms/fields/checkbox' },
						{ label: 'CodeEditor', slug: 'forms/fields/code-editor' },
						{ label: 'ColorPicker', slug: 'forms/fields/color-picker' },
						{ label: 'DatePicker', slug: 'forms/fields/date-picker' },
						{ label: 'DateTimePicker', slug: 'forms/fields/date-time-picker' },
						{ label: 'FileUpload', slug: 'forms/fields/file-upload' },
						{ label: 'Hidden', slug: 'forms/fields/hidden' },
						{ label: 'KeyValue', slug: 'forms/fields/key-value' },
						{ label: 'MarkdownEditor', slug: 'forms/fields/markdown-editor' },
						{ label: 'ModalTableSelect', slug: 'forms/fields/modal-table-select' },
						{ label: 'MorphToSelect', slug: 'forms/fields/morph-to-select' },
						{ label: 'MultiSelect', slug: 'forms/fields/multi-select' },
						{ label: 'OneTimeCodeInput', slug: 'forms/fields/one-time-code-input' },
						{ label: 'Placeholder', slug: 'forms/fields/placeholder' },
						{ label: 'Radio', slug: 'forms/fields/radio' },
						{ label: 'RelationshipRepeater', slug: 'forms/fields/relationship-repeater' },
						{ label: 'Repeater', slug: 'forms/fields/repeater' },
						{ label: 'RichEditor', slug: 'forms/fields/rich-editor' },
						{ label: 'Select', slug: 'forms/fields/select' },
						{ label: 'Slider', slug: 'forms/fields/slider' },
						{ label: 'TableSelect', slug: 'forms/fields/table-select' },
						{ label: 'TagsInput', slug: 'forms/fields/tags-input' },
						{ label: 'TextInput', slug: 'forms/fields/text-input' },
						{ label: 'Textarea', slug: 'forms/fields/textarea' },
						{ label: 'TimePicker', slug: 'forms/fields/time-picker' },
						{ label: 'ToggleButtons', slug: 'forms/fields/toggle-buttons' },
						{ label: 'Toggle', slug: 'forms/fields/toggle' },
						{ label: 'ViewField', slug: 'forms/fields/view-field' },
							],
						},
					],
				},
				{
					label: 'Tables',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'tables' },
						{ label: 'Standalone use', slug: 'tables/standalone' },
						{ label: 'Filters', slug: 'tables/filters' },
						{
							label: 'Column types',
							collapsed: true,
							items: [
						{ label: 'BadgeColumn', slug: 'tables/columns/badge-column' },
						{ label: 'BooleanColumn', slug: 'tables/columns/boolean-column' },
						{ label: 'CheckboxColumn', slug: 'tables/columns/checkbox-column' },
						{ label: 'ColorColumn', slug: 'tables/columns/color-column' },
						{ label: 'ColumnGroup', slug: 'tables/columns/column-group' },
						{ label: 'IconColumn', slug: 'tables/columns/icon-column' },
						{ label: 'ImageColumn', slug: 'tables/columns/image-column' },
						{ label: 'SelectColumn', slug: 'tables/columns/select-column' },
						{ label: 'TagsColumn', slug: 'tables/columns/tags-column' },
						{ label: 'TextColumn', slug: 'tables/columns/text-column' },
						{ label: 'TextInputColumn', slug: 'tables/columns/text-input-column' },
						{ label: 'ToggleColumn', slug: 'tables/columns/toggle-column' },
						{ label: 'ViewColumn', slug: 'tables/columns/view-column' },
							],
						},
					],
				},
				{
					label: 'Actions',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'actions' },
					],
				},
				{
					label: 'Infolists',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'infolists' },
					],
				},
				{
					label: 'Notifications',
					collapsed: true,
					items: [{ label: 'Overview', slug: 'notifications' }],
				},
				{
					label: 'Widgets',
					collapsed: true,
					items: [{ label: 'Overview', slug: 'widgets' }],
				},
				{
					label: 'Query builder',
					collapsed: true,
					items: [{ label: 'Overview', slug: 'query-builder' }],
				},
				{
					label: 'Digging deeper',
					collapsed: true,
					items: [
						{ label: 'Configuration & assets', slug: 'configuration' },
						{ label: 'Testing', slug: 'testing' },
						{ label: 'Packages', slug: 'packages' },
						{ label: 'Features', slug: 'features' },
					],
				},
			],
		}),
	],
});
