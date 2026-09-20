/**
 * Capture marketplace UI shots (light + dark) from the running docs site.
 *
 * Full-page screenshots so the sidebar, filters, listing aside, and
 * description are not cropped. Serve the built site first:
 *
 *   cd docs && npm run build && npx astro preview --port 4321
 *   node scripts/capture-marketplace.mjs
 */
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const examplesRoot = path.join(__dirname, '../public/examples');
const docsUrl = (process.env.DOCS_URL ?? 'http://localhost:4321').replace(/\/$/, '');

const shots = [
	{ id: 'plugins/browse', url: '/plugins/' },
	{ id: 'plugins/paid', url: '/plugins/paid/' },
	{ id: 'plugins/listing', url: '/plugins/orbit-branding/' },
	{ id: 'plugins/author', url: '/plugins/authors/almasix/' },
];

async function setTheme(page, theme) {
	await page.evaluate((t) => {
		document.documentElement.dataset.theme = t;
		document.documentElement.style.colorScheme = t;
		try {
			localStorage.setItem('starlight-theme', t);
		} catch {
			/* private mode */
		}
	}, theme);
	await page.waitForTimeout(250);
}

async function main() {
	const browser = await chromium.launch({
		executablePath: process.env.ORBIT_CHROMIUM || '/usr/bin/chromium',
	});
	const page = await browser.newPage({
		viewport: { width: 1440, height: 900 },
		deviceScaleFactor: 2,
	});

	for (const theme of ['light', 'dark']) {
		for (const shot of shots) {
			await page.goto(`${docsUrl}${shot.url}`, { waitUntil: 'networkidle', timeout: 60000 });
			await setTheme(page, theme);
			await page.goto(`${docsUrl}${shot.url}`, { waitUntil: 'networkidle', timeout: 60000 });
			await setTheme(page, theme);
			await page.waitForTimeout(400);
			const outDir = path.join(examplesRoot, theme, path.dirname(shot.id));
			await mkdir(outDir, { recursive: true });
			const outPath = path.join(examplesRoot, theme, `${shot.id}.png`);
			await page.screenshot({
				path: outPath,
				animations: 'disabled',
				fullPage: true,
			});
			console.log(`wrote ${theme}/${shot.id}.png`);
		}
	}

	await browser.close();
}

main().catch((err) => {
	console.error(err);
	process.exit(1);
});
