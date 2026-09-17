#!/usr/bin/env python3
"""Capture gallery shots → docs/public/examples/{light|dark}/{section}/{name}.png."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "public" / "examples" / "gallery.html"


def main() -> None:
    if not GALLERY.exists():
        raise SystemExit("Missing gallery.html — run build-gallery.py first")

    url = GALLERY.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/chromium", headless=True)
        page = browser.new_page(
            viewport={"width": 1280, "height": 900},
            device_scale_factor=2,  # crisp docs PNGs
        )
        for theme in ("light", "dark"):
            page.goto(url, wait_until="domcontentloaded")
            page.evaluate(
                """(t) => {
                  document.documentElement.setAttribute('data-theme', t);
                  document.body.classList.toggle('dark', t === 'dark');
                  // Belt-and-suspenders: never leave confirm chrome in the frame.
                  document.querySelectorAll(
                    '.or-action-modal-host, .or-modal-backdrop, .or-modal'
                  ).forEach((el) => el.remove());
                }""",
                theme,
            )
            page.wait_for_timeout(100)
            shots = page.locator("[data-shot]")
            count = shots.count()
            if count == 0:
                raise SystemExit("No [data-shot] frames found in gallery")
            for i in range(count):
                loc = shots.nth(i)
                shot_id = loc.get_attribute("data-shot") or f"shot-{i}"
                out = ROOT / "public" / "examples" / theme / Path(shot_id)
                out.parent.mkdir(parents=True, exist_ok=True)
                path = out.with_suffix(".png")
                loc.scroll_into_view_if_needed()
                loc.screenshot(path=str(path), animations="disabled")
                print(f"wrote {path.relative_to(ROOT)}")
        browser.close()


if __name__ == "__main__":
    main()
