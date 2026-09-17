/**
 * Capture gallery shots → docs/public/examples/{light|dark}/{section}/{name}.png
 * Usage: node docs/scripts/capture-examples.mjs
 */
import { chromium } from "playwright";
import { mkdir, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const gallery = path.join(__dirname, "../public/examples/gallery.html");
const examplesRoot = path.join(__dirname, "../public/examples");

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
    viewport: { width: 1280, height: 900 },
    deviceScaleFactor: 2,
  });
  const url = pathToFileURL(gallery).href;

  for (const theme of ["light", "dark"]) {
    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.evaluate((t) => {
      document.documentElement.setAttribute("data-theme", t);
      document.body.classList.toggle("dark", t === "dark");
      document
        .querySelectorAll(".or-action-modal-host, .or-modal-backdrop, .or-modal")
        .forEach((el) => el.remove());
    }, theme);
    await page.waitForTimeout(100);

    const shots = page.locator("[data-shot]");
    const count = await shots.count();
    if (!count) {
      throw new Error("No [data-shot] frames found in gallery");
    }
    for (let i = 0; i < count; i++) {
      const loc = shots.nth(i);
      const shotId = (await loc.getAttribute("data-shot")) || `shot-${i}`;
      const outDir = path.join(examplesRoot, theme, path.dirname(shotId));
      await mkdir(outDir, { recursive: true });
      const outPath = path.join(examplesRoot, theme, `${shotId}.png`);
      await loc.scrollIntoViewIfNeeded();
      await loc.screenshot({ path: outPath, animations: "disabled" });
      console.log(`wrote ${theme}/${shotId}.png`);
    }
  }
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
