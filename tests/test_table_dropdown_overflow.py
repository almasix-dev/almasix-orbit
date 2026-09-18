"""Playwright: row action menus must float above table scroll overflow."""

from __future__ import annotations

from pathlib import Path

import pytest

CSS = Path("packages/panels/src/almasix/orbit/resources/css/orbit.css")
JS = Path("packages/panels/src/almasix/orbit/resources/js/orbit.js")


def _launch_chromium(playwright):  # type: ignore[no-untyped-def]
    from pathlib import Path as P

    for candidate in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
        if P(candidate).is_file():
            return playwright.chromium.launch(
                headless=True,
                executable_path=candidate,
                args=["--no-sandbox", "--disable-gpu"],
            )
    return playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])


@pytest.mark.skipif(not CSS.is_file() or not JS.is_file(), reason="orbit assets missing")
def test_row_action_menu_escapes_table_scroll_overflow() -> None:
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    css = CSS.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.3/dist/cdn.min.js"></script>
<script>{js}</script>
<style>{css}
body {{ margin: 0; background: var(--or-cream, #f8fafc); }}
[x-cloak] {{ display: none !important; }}
</style></head>
<body>
  <div class="or-list-card" style="width: 32rem; margin: 2rem;">
    <div class="or-list-table-scroll" id="scroll" style="max-height: 7rem;">
      <table class="or-table">
        <thead><tr>
          <th class="or-th">Name</th>
          <th class="or-th or-th-actions">Actions</th>
        </tr></thead>
        <tbody>
          <tr>
            <td class="or-td">Ada Lovelace</td>
            <td class="or-td or-td-actions">
              <div class="or-row-actions">
                <div class="or-action-group or-dropdown" data-dropdown="true"
                  x-data="orbitDropdown" @click.outside="closeMenu()">
                  <button type="button" class="or-btn or-btn-gray or-btn-icon or-icon-btn"
                    id="trigger" aria-label="Actions" aria-haspopup="menu"
                    @click="toggleMenu($event)" :aria-expanded="menuOpen.toString()">⋮</button>
                  <div class="or-dropdown-menu or-dropdown-menu-end" id="menu" role="menu"
                    x-show="menuOpen" x-cloak>
                    <button type="button" class="or-btn or-btn-gray" id="view">View</button>
                    <button type="button" class="or-btn or-btn-danger" id="delete">Delete</button>
                    <button type="button" class="or-btn or-btn-gray" id="extra">More</button>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="or-table-pagination" id="footer" style="padding: 0.75rem 1rem; border-top: 1px solid #e5e7eb;">
      Showing 1 to 1 of 1 results
    </div>
  </div>
</body></html>"""

    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page(viewport={"width": 900, "height": 600})
        page.set_content(html, wait_until="load")
        page.wait_for_function("() => window.Alpine && window.Alpine.version")
        page.click("#trigger")
        page.wait_for_selector("#menu:not([style*='display: none'])", state="visible")
        metrics = page.evaluate(
            """() => {
              const menu = document.getElementById('menu');
              const scroll = document.getElementById('scroll');
              const footer = document.getElementById('footer');
              const deleteBtn = document.getElementById('delete');
              const menuRect = menu.getBoundingClientRect();
              const scrollRect = scroll.getBoundingClientRect();
              const footerRect = footer.getBoundingClientRect();
              const deleteRect = deleteBtn.getBoundingClientRect();
              const style = getComputedStyle(menu);
              return {
                position: style.position,
                fixedClass: menu.classList.contains('or-dropdown-menu-fixed'),
                inBody: menu.parentElement === document.body,
                menuBottom: menuRect.bottom,
                scrollBottom: scrollRect.bottom,
                footerTop: footerRect.top,
                deleteVisibleHeight: deleteRect.height,
                deleteTop: deleteRect.top,
                scrollScrollHeight: scroll.scrollHeight,
                scrollClientHeight: scroll.clientHeight,
                escapesScroll: menuRect.bottom > scrollRect.bottom + 4,
                deleteNotClipped: deleteRect.bottom <= window.innerHeight
                  && deleteRect.height > 8
                  && deleteRect.top < footerRect.bottom,
              };
            }"""
        )
        browser.close()

    assert metrics["fixedClass"] is True, metrics
    assert metrics["position"] == "fixed", metrics
    assert metrics["inBody"] is True, metrics
    assert metrics["escapesScroll"] is True, metrics
    assert metrics["deleteVisibleHeight"] > 8, metrics
    # Opening the menu must not force the table body to scroll its own content.
    assert metrics["scrollScrollHeight"] <= metrics["scrollClientHeight"] + 2, metrics
