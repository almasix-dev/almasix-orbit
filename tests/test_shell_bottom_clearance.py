"""Playwright: shell bottom clearance after page content."""

from __future__ import annotations

from pathlib import Path

import pytest

CSS = Path("packages/panels/src/almasix/orbit/resources/css/orbit.css")


def _launch_chromium(playwright):  # type: ignore[no-untyped-def]
    """Prefer system Chromium when Playwright's browser cache is incomplete."""
    from pathlib import Path as P

    for candidate in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
        if P(candidate).is_file():
            return playwright.chromium.launch(
                headless=True,
                executable_path=candidate,
                args=["--no-sandbox", "--disable-gpu"],
            )
    return playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])


@pytest.mark.skipif(not CSS.is_file(), reason="orbit.css missing")
def test_main_scroll_has_bottom_clearance_after_content() -> None:
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    css = CSS.read_text(encoding="utf-8")
    # Tall page so .or-main must scroll; #last is the final content marker.
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<style>{css}</style></head>
<body class="or-body">
  <div class="or-app" style="height:420px">
    <aside class="or-sidebar" style="width:12rem"></aside>
    <div class="or-main">
      <header class="or-topbar"><span>Top</span></header>
      <nav class="or-breadcrumbs"><ol class="or-breadcrumbs-list"><li>Home</li></ol></nav>
      <main class="or-content">
        <div class="or-page">
          <div id="tall" style="height:900px;background:var(--or-line)"></div>
          <div id="last" class="or-list-card" style="padding:1rem">LAST</div>
        </div>
      </main>
    </div>
  </div>
</body></html>"""

    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page(viewport={"width": 1100, "height": 420})
        page.set_content(html, wait_until="load")
        page.evaluate("document.querySelector('.or-main').scrollTop = 999999")
        metrics = page.evaluate(
            """() => {
              const main = document.querySelector('.or-main');
              const last = document.querySelector('#last');
              const mainRect = main.getBoundingClientRect();
              const lastRect = last.getBoundingClientRect();
              const style = getComputedStyle(main, '::after');
              return {
                clearance: mainRect.bottom - lastRect.bottom,
                scrollTop: main.scrollTop,
                canScroll: main.scrollHeight > main.clientHeight + 8,
                afterHeight: style.height,
              };
            }"""
        )
        browser.close()

    assert metrics["canScroll"] is True
    # At least ~4rem visible gap between last content and the scrollport bottom.
    assert metrics["clearance"] >= 60, metrics
    assert metrics["afterHeight"] not in ("0px", "auto"), metrics
