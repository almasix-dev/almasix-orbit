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
					label: 'The panel',
					collapsed: true,
					items: [
						{ label: 'Panels', slug: 'panels' },
						{ label: 'Resources', slug: 'resources' },
						{ label: 'Pages', slug: 'pages' },
						{ label: 'Relation managers', slug: 'relation-managers' },
					],
				},
				{
					label: 'Building UI',
					collapsed: true,
					items: [
						{ label: 'Forms', slug: 'forms' },
						{ label: 'Tables', slug: 'tables' },
						{ label: 'Actions', slug: 'actions' },
						{ label: 'Infolists', slug: 'infolists' },
						{ label: 'Schemas & layouts', slug: 'schemas' },
					],
				},
				{
					label: 'Extras',
					collapsed: true,
					items: [
						{ label: 'Notifications', slug: 'notifications' },
						{ label: 'Widgets', slug: 'widgets' },
						{ label: 'Query builder', slug: 'query-builder' },
						{ label: 'Support toolkit', slug: 'support' },
					],
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
