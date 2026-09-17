#!/usr/bin/env python3
"""Capture gallery sections with system Chromium via Playwright."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "public" / "examples" / "gallery.html"
SHOTS = ["form", "table", "primes", "login", "shell"]


def main() -> None:
    if not GALLERY.exists():
        raise SystemExit("Missing gallery.html — run build-gallery.py first")
    url = GALLERY.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/chromium", headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 800})
        for theme in ("light", "dark"):
            out = ROOT / "public" / "examples" / theme
            out.mkdir(parents=True, exist_ok=True)
            page.goto(url)
            page.evaluate(
                """(t) => {
                  document.documentElement.setAttribute('data-theme', t);
                  document.body.classList.toggle('dark', t === 'dark');
                }""",
                theme,
            )
            for sid in SHOTS:
                loc = page.locator(f"#{sid}")
                loc.scroll_into_view_if_needed()
                path = out / f"{sid}.png"
                loc.screenshot(path=str(path))
                print(f"wrote {path}")
        browser.close()


if __name__ == "__main__":
    main()
