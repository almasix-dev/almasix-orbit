/**
 * Capture Widgets + Dashboard gallery shots (light + dark).
 * Usage: node docs/scripts/capture-widgets.mjs
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

async function waitForCharts(page) {
  await page.waitForFunction(
    () => {
      const alpineReady = typeof window.Alpine !== "undefined";
      const chartLib =
        typeof window.Chart !== "undefined" || typeof window.ApexCharts !== "undefined";
      return alpineReady && chartLib;
    },
    { timeout: 15000 },
  );
  // Allow orbitChart / orbitSparkline to paint canvases.
  await page.waitForTimeout(600);
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
  await waitForCharts(page);

  for (const theme of ["light", "dark"]) {
    await page.evaluate((t) => {
      document.documentElement.setAttribute("data-theme", t);
      document.body.classList.toggle("dark", t === "dark");
    }, theme);
    await page.waitForTimeout(200);
    // Re-paint charts after theme toggle when libraries support it.
    await page.evaluate(() => {
      document.querySelectorAll('[x-data="orbitChart"], [x-data="orbitSparkline"]').forEach((el) => {
        el.dispatchEvent(new CustomEvent("orbit:theme-changed", { bubbles: true }));
      });
    });
    await page.waitForTimeout(400);

    const prefixes = ["widgets/", "panels/dashboard"];
    for (const prefix of prefixes) {
      const shots = page.locator(`[data-shot^="${prefix}"]`);
      const count = await shots.count();
      if (!count && prefix === "widgets/") {
        throw new Error("No widgets/[data-shot] frames found — rebuild gallery");
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
  }
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
