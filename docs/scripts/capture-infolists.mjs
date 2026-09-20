/**
 * Capture infolist gallery shots (light + dark).
 * Usage: node docs/scripts/capture-infolists.mjs
 */
import { chromium } from "playwright";
import { mkdir, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const gallery = path.join(__dirname, "../public/examples/gallery.html");
const examplesRoot = path.join(__dirname, "../public/examples");

const IDS = [
  "infolists/overview",
  "infolists/overview/labels",
  "infolists/overview/helper-hint",
  "infolists/overview/hidden-label",
  "infolists/overview/inline-label",
  "infolists/overview/placeholder",
  "infolists/overview/default",
  "infolists/overview/copyable",
  "infolists/overview/format-state",
  "infolists/overview/tooltip",
  "infolists/overview/slots",
  "infolists/overview/affix",
  "infolists/overview/extra-attributes",
  "infolists/overview/columns",
  "infolists/overview/sections",
  "infolists/text-entry/basic",
  "infolists/text-entry/badge",
  "infolists/text-entry/color",
  "infolists/text-entry/icon",
  "infolists/text-entry/url",
  "infolists/text-entry/size-weight",
  "infolists/text-entry/font-family",
  "infolists/text-entry/line-clamp",
  "infolists/text-entry/list",
  "infolists/text-entry/bulleted",
  "infolists/text-entry/separator",
  "infolists/text-entry/date",
  "infolists/text-entry/since",
  "infolists/text-entry/money",
  "infolists/text-entry/numeric",
  "infolists/text-entry/markdown",
  "infolists/text-entry/html",
  "infolists/text-entry/prose",
  "infolists/text-entry/limit",
  "infolists/icon-entry/basic",
  "infolists/icon-entry/boolean",
  "infolists/icon-entry/colors",
  "infolists/image-entry/basic",
  "infolists/image-entry/circular",
  "infolists/image-entry/stacked",
  "infolists/color-entry/basic",
  "infolists/color-entry/copyable",
  "infolists/code-entry/basic",
  "infolists/code-entry/grammar",
  "infolists/key-value-entry/basic",
  "infolists/key-value-entry/labels",
  "infolists/repeatable-entry/basic",
  "infolists/repeatable-entry/columns",
  "infolists/view-entry/basic",
  "infolists/view-entry/callable",
];

async function exists(p) {
  try {
    await access(p);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  if (!(await exists(gallery))) {
    console.error("Missing gallery.html — run: python docs/scripts/build-gallery.py");
    process.exit(1);
  }
  const browser = await chromium.launch({
    executablePath: process.env.ORBIT_CHROMIUM || "/usr/bin/chromium",
  });
  const page = await browser.newPage({
    viewport: { width: 1680, height: 1050 },
    deviceScaleFactor: 2,
  });
  await page.goto(pathToFileURL(gallery).href, { waitUntil: "domcontentloaded" });
  for (const theme of ["light", "dark"]) {
    await page.evaluate((t) => {
      document.documentElement.setAttribute("data-theme", t);
      document.body.classList.toggle("dark", t === "dark");
      document
        .querySelectorAll(".or-action-modal-host, .or-modal-backdrop, .or-modal")
        .forEach((el) => el.remove());
    }, theme);
    await page.waitForTimeout(100);
    for (const id of IDS) {
      const loc = page.locator(`[data-shot="${id}"]`);
      if ((await loc.count()) === 0) {
        console.warn("missing shot", id);
        continue;
      }
      const outDir = path.join(examplesRoot, theme, path.dirname(id));
      await mkdir(outDir, { recursive: true });
      const outPath = path.join(examplesRoot, theme, `${id}.png`);
      await loc.scrollIntoViewIfNeeded();
      await loc.screenshot({ path: outPath, animations: "disabled" });
      console.log(`wrote ${theme}/${id}.png`);
    }
  }
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
