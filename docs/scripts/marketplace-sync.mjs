/**
 * Fetch almasix-dev/orbit-plugins into docs/.marketplace and copy images into
 * docs/public/plugins and docs/public/articles so the catalog can build without
 * shipping listing YAML in this repository.
 *
 *   npm run marketplace:sync
 *
 * Production / CI: fails if the fetch fails.
 * Offline local: MARKETPLACE_SYNC_OPTIONAL=1 skips when the network is down
 * (requires an existing .marketplace checkout).
 */
import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const docsRoot = path.resolve(fileURLToPath(import.meta.url), '../..');
const dest = path.join(docsRoot, '.marketplace');
const publicPlugins = path.join(docsRoot, 'public', 'plugins');
const publicArticles = path.join(docsRoot, 'public', 'articles');

const REPO = process.env.ORBIT_PLUGINS_REPO || 'https://github.com/almasix-dev/orbit-plugins.git';
const REF = process.env.ORBIT_PLUGINS_REF || 'main';
const optional = process.env.MARKETPLACE_SYNC_OPTIONAL === '1';

function fail(message) {
	console.error(message);
	process.exit(1);
}

function cloneRegistry() {
	const tmp = path.join(docsRoot, '.marketplace-tmp');
	rmSync(tmp, { recursive: true, force: true });
	mkdirSync(path.dirname(tmp), { recursive: true });
	const result = spawnSync(
		'git',
		['clone', '--depth', '1', '--branch', REF, REPO, tmp],
		{ encoding: 'utf8' },
	);
	if (result.status !== 0) {
		rmSync(tmp, { recursive: true, force: true });
		const detail = (result.stderr || result.stdout || '').trim();
		throw new Error(`git clone failed (${result.status}): ${detail}`);
	}
	rmSync(path.join(tmp, '.git'), { recursive: true, force: true });
	rmSync(dest, { recursive: true, force: true });
	cpSync(tmp, dest, { recursive: true });
	rmSync(tmp, { recursive: true, force: true });
}

function copyTree(sourceRelative, target) {
	const source = path.join(dest, 'public', sourceRelative);
	rmSync(target, { recursive: true, force: true });
	if (!existsSync(source)) {
		mkdirSync(target, { recursive: true });
		return;
	}
	mkdirSync(path.dirname(target), { recursive: true });
	cpSync(source, target, { recursive: true });
}

function copyImages() {
	const pluginsSource = path.join(dest, 'public', 'plugins');
	if (!existsSync(pluginsSource)) {
		throw new Error(`registry is missing public/plugins at ${pluginsSource}`);
	}
	copyTree('plugins', publicPlugins);
	copyTree('articles', publicArticles);
}

try {
	cloneRegistry();
	copyImages();
	console.log(`Marketplace registry synced from ${REPO} @ ${REF} → .marketplace/`);
} catch (error) {
	if (optional && existsSync(path.join(dest, 'categories.yaml'))) {
		console.warn(`marketplace:sync failed (${error.message}); using existing .marketplace/`);
		try {
			copyImages();
		} catch (copyError) {
			console.warn(`marketplace:sync image copy skipped: ${copyError.message}`);
		}
		process.exit(0);
	}
	fail(`marketplace:sync failed: ${error.message}`);
}
