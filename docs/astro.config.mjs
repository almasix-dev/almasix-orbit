// @ts-check
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
				'Orbit brings Filament’s power to Almasix — panels, resources, forms, and tables.',
			customCss: ['./src/styles/custom.css'],
			sidebar: [
				{ label: 'Home', slug: 'index' },
				{
					label: 'Getting started',
					collapsed: false,
					items: [{ label: 'Install', slug: 'getting-started' }],
				},
				{
					label: 'Packages',
					collapsed: false,
					items: [{ label: 'Overview', slug: 'index' }],
				},
				{
					label: 'Parity',
					collapsed: false,
					items: [{ label: 'Filament 5.x matrix', slug: 'parity' }],
				},
			],
		}),
	],
});
