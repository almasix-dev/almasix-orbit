/**
 * Produce parallel docs trees: `/0.x/` from the latest `v0.*` tag, `/main/`
 * from this commit. Unprefixed `/` redirects to latest (`/0.x/`).
 *
 * Local `astro dev` / `npm run build:current` stay a single unprefixed tree.
 * Set SKIP_DOCS_0X=1 to assemble only `/main/` (still redirected from `/` when
 * a 0.x tree is missing).
 */

import { spawnSync } from 'node:child_process';
import {
	cpSync,
	existsSync,
	mkdirSync,
	readdirSync,
	readFileSync,
	rmSync,
	statSync,
	writeFileSync,
} from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { LATEST_VERSION, latestV0Tag, prefixHtmlRootUrls } from '../src/versions.mjs';

const docsRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const versionBuild = join(docsRoot, '.version-build');
const dist = join(docsRoot, 'dist');

function run(cmd, args, opts = {}) {
	const result = spawnSync(cmd, args, { stdio: 'inherit', ...opts });
	if (result.status !== 0) {
		throw new Error(`${cmd} ${args.join(' ')} failed (${result.status})`);
	}
}

function git(args, opts = {}) {
	const result = spawnSync('git', args, { encoding: 'utf8', ...opts });
	if (result.status !== 0) {
		throw new Error(`git ${args.join(' ')} failed: ${result.stderr || result.stdout}`);
	}
	return result.stdout.trim();
}

function rewriteHtmlTree(dir, slug) {
	const visit = (folder) => {
		for (const name of readdirSync(folder)) {
			const path = join(folder, name);
			if (statSync(path).isDirectory()) {
				visit(path);
				continue;
			}
			if (!name.endsWith('.html')) continue;
			const next = prefixHtmlRootUrls(readFileSync(path, 'utf8'), slug);
			writeFileSync(path, next);
		}
	};
	visit(dir);
}

function ensureVersionBase(astroConfigPath, slug) {
	let text = readFileSync(astroConfigPath, 'utf8');
	if (text.includes('DOCS_VERSION')) return;
	if (!text.includes("const base = '/';")) {
		throw new Error(`Cannot patch docs base in ${astroConfigPath}`);
	}
	text = text.replace("const base = '/';", `const base = '/${slug}/';`);
	writeFileSync(astroConfigPath, text);
}

function overlaySwitcher(extractedDocs) {
	const files = [
		'src/versions.mjs',
		'src/components/VersionSelect.astro',
		'src/components/VersionBanner.astro',
		'src/content/docs/prologue/versions.md',
	];
	for (const rel of files) {
		cpSync(join(docsRoot, rel), join(extractedDocs, rel));
	}
}

function redirectHtml(href) {
	return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0;url=${href}">
<link rel="canonical" href="https://orbit.almasix.com${href}">
<title>Orbit documentation</title>
<script>location.replace(${JSON.stringify(href)}+location.search+location.hash);</script>
</head>
<body>
<p>Redirecting to <a href="${href}">${LATEST_VERSION} documentation</a>.</p>
</body>
</html>
`;
}

function extractTagDocs(repoRoot, tag, destParent) {
	rmSync(destParent, { recursive: true, force: true });
	mkdirSync(destParent, { recursive: true });
	const archive = spawnSync('git', ['archive', tag, 'docs'], {
		cwd: repoRoot,
		maxBuffer: 512 * 1024 * 1024,
	});
	if (archive.status !== 0) {
		throw new Error(`git archive ${tag} docs failed: ${archive.stderr?.toString() || ''}`);
	}
	const tar = spawnSync('tar', ['-x'], { cwd: destParent, input: archive.stdout });
	if (tar.status !== 0) {
		throw new Error(`tar extract failed: ${tar.stderr?.toString() || ''}`);
	}
	const extractedDocs = join(destParent, 'docs');
	if (!existsSync(join(extractedDocs, 'package.json'))) {
		throw new Error(`Extracted ${tag} is missing docs/package.json`);
	}
	return extractedDocs;
}

const repoRoot = git(['rev-parse', '--show-toplevel'], { cwd: docsRoot });
spawnSync('git', ['fetch', '--tags', '--force', 'origin'], { cwd: repoRoot, stdio: 'inherit' });

rmSync(versionBuild, { recursive: true, force: true });
mkdirSync(versionBuild, { recursive: true });

const distMain = join(versionBuild, 'dist-main');
console.log('Building main docs tree → /main/');
run('npx', ['astro', 'build', '--force', '--outDir', distMain], {
	cwd: docsRoot,
	env: { ...process.env, DOCS_VERSION: 'main' },
});
rewriteHtmlTree(distMain, 'main');

let dist0x = null;
if (!process.env.SKIP_DOCS_0X) {
	const tags = git(['tag', '-l', 'v0.*'], { cwd: repoRoot })
		.split('\n')
		.map((line) => line.trim())
		.filter(Boolean);
	const tag = process.env.DOCS_0X_TAG || latestV0Tag(tags);
	if (!tag) {
		throw new Error(
			'No stable v0.x.x tag found. Fetch tags (`git fetch --tags`) or set DOCS_0X_TAG.',
		);
	}
	spawnSync('git', ['fetch', '--force', 'origin', `refs/tags/${tag}:refs/tags/${tag}`], {
		cwd: repoRoot,
		stdio: 'inherit',
	});
	console.log(`Building 0.x docs tree from ${tag} → /0.x/`);
	const extractedDocs = extractTagDocs(repoRoot, tag, join(versionBuild, 'src-0.x'));
	overlaySwitcher(extractedDocs);
	ensureVersionBase(join(extractedDocs, 'astro.config.mjs'), '0.x');
	run('npm', ['ci'], { cwd: extractedDocs });
	run('npx', ['astro', 'build', '--force', '--outDir', 'dist'], {
		cwd: extractedDocs,
		env: { ...process.env, DOCS_VERSION: '0.x' },
	});
	dist0x = join(extractedDocs, 'dist');
	rewriteHtmlTree(dist0x, '0.x');
	writeFileSync(join(versionBuild, '0.x-tag.txt'), `${tag}\n`);
}

rmSync(dist, { recursive: true, force: true });
mkdirSync(join(dist, 'main'), { recursive: true });
cpSync(distMain, join(dist, 'main'), { recursive: true });
if (dist0x) {
	mkdirSync(join(dist, '0.x'), { recursive: true });
	cpSync(dist0x, join(dist, '0.x'), { recursive: true });
}

const latestHref = dist0x ? `/${LATEST_VERSION}/` : '/main/';
writeFileSync(join(dist, 'index.html'), redirectHtml(latestHref));
writeFileSync(
	join(dist, 'robots.txt'),
	`User-agent: *\nAllow: /\nSitemap: https://orbit.almasix.com/0.x/sitemap-index.xml\nSitemap: https://orbit.almasix.com/main/sitemap-index.xml\n`,
);
for (const name of ['favicon.svg', 'apple-touch-icon.png', 'og.png']) {
	const src = join(distMain, name);
	if (existsSync(src)) cpSync(src, join(dist, name));
}

console.log(`Docs trees ready in dist/ (default ${latestHref})`);
