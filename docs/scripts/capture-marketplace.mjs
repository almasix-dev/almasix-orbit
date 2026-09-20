/**
 * Capture marketplace UI shots (light + dark) from the running docs site.
 * Usage: node scripts/capture-marketplace.mjs
 *        DOCS_URL=http://127.0.0.1:4321 node scripts/capture-marketplace.mjs
 */
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const examplesRoot = path.join(__dirname, '../public/examples');
const docsUrl = (process.env.DOCS_URL ?? 'http://localhost:4321').replace(/\/$/, '');

const shots = [
	{ id: 'plugins/browse', url: '/plugins/', selector: '.market' },
	{ id: 'plugins/listing', url: '/plugins/orbit-branding/', selector: '.market' },
	{ id: 'plugins/author', url: '/plugins/authors/almasix/', selector: '.market' },
	{ id: 'plugins/using', url: '/plugins/using/', selector: 'main' },
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
	await page.waitForTimeout(200);
}

async function main() {
	const browser = await chromium.launch({
		executablePath: process.env.ORBIT_CHROMIUM || '/usr/bin/chromium',
	});
	const page = await browser.newPage({
		viewport: { width: 1280, height: 900 },
		deviceScaleFactor: 2,
	});

	for (const theme of ['light', 'dark']) {
		for (const shot of shots) {
			await page.goto(`${docsUrl}${shot.url}`, { waitUntil: 'networkidle' });
			await setTheme(page, theme);
			await page.goto(`${docsUrl}${shot.url}`, { waitUntil: 'networkidle' });
			await setTheme(page, theme);
			const loc = page.locator(shot.selector).first();
			await loc.waitFor({ state: 'visible' });
			const outDir = path.join(examplesRoot, theme, path.dirname(shot.id));
			await mkdir(outDir, { recursive: true });
			const outPath = path.join(examplesRoot, theme, `${shot.id}.png`);
			await loc.screenshot({ path: outPath, animations: 'disabled' });
			console.log(`wrote ${theme}/${shot.id}.png`);
		}
	}

	await browser.close();
}

main().catch((err) => {
	console.error(err);
	process.exit(1);
});
