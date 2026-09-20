/**
 * Capture Actions gallery shots (light + dark).
 * Usage: node docs/scripts/capture-actions.mjs
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
    console.error("Missing gallery.html — run: .venv/bin/python docs/scripts/build-gallery.py");
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
        .querySelectorAll(".or-action-modal-host, .or-modal-backdrop")
        .forEach((el) => {
          if (!el.closest('[data-shot^="actions/"]')) el.remove();
        });
    }, theme);
    await page.waitForTimeout(150);

    const shots = page.locator('[data-shot^="actions/"]');
    const count = await shots.count();
    if (!count) {
      throw new Error("No actions/[data-shot] frames found — rebuild gallery");
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
