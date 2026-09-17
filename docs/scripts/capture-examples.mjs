/**
 * Capture light/dark PNGs from the Orbit examples gallery.
 * Usage: node docs/scripts/capture-examples.mjs
 */
import { chromium } from "playwright";
import { mkdir, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const gallery = path.join(__dirname, "../public/examples/gallery.html");
const lightDir = path.join(__dirname, "../public/examples/light");
const darkDir = path.join(__dirname, "../public/examples/dark");

const shots = ["form", "table", "primes", "login", "shell"];

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
  await mkdir(lightDir, { recursive: true });
  await mkdir(darkDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
  const url = pathToFileURL(gallery).href;

  for (const theme of ["light", "dark"]) {
    await page.goto(url);
    await page.evaluate((t) => {
      document.documentElement.setAttribute("data-theme", t);
      document.body.classList.toggle("dark", t === "dark");
    }, theme);
    const dir = theme === "light" ? lightDir : darkDir;
    for (const id of shots) {
      const el = page.locator(`#${id}`);
      await el.scrollIntoViewIfNeeded();
      await el.screenshot({ path: path.join(dir, `${id}.png`) });
      console.log(`wrote ${theme}/${id}.png`);
    }
  }
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
