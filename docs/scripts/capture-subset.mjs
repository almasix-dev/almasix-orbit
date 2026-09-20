import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const gallery = path.join(__dirname, "../public/examples/gallery.html");
const examplesRoot = path.join(__dirname, "../public/examples");
const IDS = process.argv.slice(2);

const browser = await chromium.launch({ executablePath: process.env.ORBIT_CHROMIUM || "/usr/bin/chromium" });
const page = await browser.newPage({ viewport: { width: 1680, height: 1050 }, deviceScaleFactor: 2 });
for (const theme of ["light", "dark"]) {
  await page.goto(pathToFileURL(gallery).href, { waitUntil: "domcontentloaded" });
  await page.evaluate((t) => {
    document.documentElement.setAttribute("data-theme", t);
    document.body.classList.toggle("dark", t === "dark");
    document.querySelectorAll(".or-action-modal-host, .or-modal-backdrop, .or-modal").forEach((el) => {
      if (el.closest('[data-shot="forms/modal-table-select/picker"]')) return;
      el.remove();
    });
  }, theme);
  await page.waitForTimeout(400);
  for (const id of IDS) {
    const loc = page.locator(`[data-shot="${id}"]`);
    if ((await loc.count()) === 0) { console.warn("missing", id); continue; }
    await mkdir(path.join(examplesRoot, theme, path.dirname(id)), { recursive: true });
    await loc.scrollIntoViewIfNeeded();
    await loc.screenshot({ path: path.join(examplesRoot, theme, `${id}.png`), animations: "disabled" });
    console.log("wrote", theme, id);
  }
}
await browser.close();
