"""Playwright: open ActionGroup menu must paint above later group triggers."""

from __future__ import annotations

from pathlib import Path

import pytest

CSS = Path("packages/panels/src/almasix/orbit/resources/css/orbit.css")


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


@pytest.mark.skipif(not CSS.is_file(), reason="orbit.css missing")
def test_open_action_group_menu_above_later_row_trigger() -> None:
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    css = CSS.read_text(encoding="utf-8")
    # Two stacked row ActionGroups: open the first; the second ⋮ must not win paint.
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<style>{css}
body {{ margin: 0; background: var(--or-cream, #f8fafc); }}
.or-dropdown-menu[hidden] {{ display: none !important; }}
</style></head>
<body>
  <div class="or-list-card" style="width: 28rem; margin: 2rem">
    <div class="or-list-table-scroll">
      <table class="or-table">
        <tbody>
          <tr>
            <td class="or-td">Row 1</td>
            <td class="or-td or-td-actions">
              <div class="or-row-actions">
                <div class="or-action-group or-dropdown" id="group-1">
                  <button type="button" class="or-btn or-btn-gray or-btn-icon or-icon-btn"
                    id="trigger-1" aria-label="Actions" aria-expanded="true"
                    aria-haspopup="menu">⋮</button>
                  <div class="or-dropdown-menu" id="menu-1" role="menu">
                    <button type="button" class="or-btn or-btn-gray" id="menu-item">Edit</button>
                    <button type="button" class="or-btn or-btn-danger">Delete</button>
                  </div>
                </div>
              </div>
            </td>
          </tr>
          <tr>
            <td class="or-td">Row 2</td>
            <td class="or-td or-td-actions">
              <div class="or-row-actions">
                <div class="or-action-group or-dropdown" id="group-2">
                  <button type="button" class="or-btn or-btn-gray or-btn-icon or-icon-btn"
                    id="trigger-2" aria-label="Actions" aria-expanded="false"
                    aria-haspopup="menu">⋮</button>
                  <div class="or-dropdown-menu" id="menu-2" role="menu" hidden>
                    <button type="button" class="or-btn">View</button>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</body></html>"""

    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page(viewport={"width": 800, "height": 500})
        page.set_content(html, wait_until="load")
        metrics = page.evaluate(
            """() => {
              const menu = document.getElementById('menu-1');
              const trigger2 = document.getElementById('trigger-2');
              const item = document.getElementById('menu-item');
              const menuRect = menu.getBoundingClientRect();
              const t2 = trigger2.getBoundingClientRect();
              // Probe a point inside the open menu that vertically aligns with row-2 trigger
              // when the menu overlaps that row (typical short menus still cover the next ⋮).
              const x = Math.min(
                menuRect.left + menuRect.width / 2,
                Math.max(menuRect.left + 8, t2.left + t2.width / 2)
              );
              const y = Math.min(
                menuRect.bottom - 8,
                Math.max(menuRect.top + 8, t2.top + t2.height / 2)
              );
              const hit = document.elementFromPoint(x, y);
              const group1 = document.getElementById('group-1');
              const z = getComputedStyle(group1).zIndex;
              return {
                x, y,
                hitId: hit && (hit.id || hit.closest('[id]')?.id || hit.className),
                hitTag: hit && hit.tagName,
                overlapsTrigger2:
                  menuRect.bottom > t2.top &&
                  menuRect.top < t2.bottom &&
                  menuRect.right > t2.left &&
                  menuRect.left < t2.right,
                group1Z: z,
                menuVisible: menuRect.height > 0 && getComputedStyle(menu).display !== 'none',
                itemInMenu: !!(item && menu.contains(item)),
              };
            }"""
        )
        browser.close()

    assert metrics["menuVisible"] is True, metrics
    assert metrics["group1Z"] not in ("auto", "0", ""), metrics
    # If geometry overlaps the later trigger, the hit target must be menu chrome — not ⋮ #2.
    if metrics["overlapsTrigger2"]:
        assert metrics["hitId"] != "trigger-2", metrics
        assert "trigger-2" not in str(metrics["hitId"]), metrics
