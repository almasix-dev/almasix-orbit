"""Tests for content max-width resolution and shell injection."""

from __future__ import annotations

from types import SimpleNamespace

from almasix.orbit.panels.content_width import resolve_content_max_width
from almasix.orbit.panels.panel import Panel
from almasix.orbit.tables.columns import TextColumn
from almasix.orbit.tables.filters import SelectFilter
from almasix.orbit.tables.table import Table


def test_resolve_content_max_width_tokens() -> None:
    assert resolve_content_max_width(None).css_value == "96rem"
    assert resolve_content_max_width("screen-lg").css_value == "64rem"
    assert resolve_content_max_width("7xl").css_value == "80rem"
    assert resolve_content_max_width("full").css_value == "100%"
    assert resolve_content_max_width("1200px").css_value == "1200px"
    assert resolve_content_max_width("max-w-screen-2xl").css_value == "96rem"
    assert resolve_content_max_width(None).token == "screen-2xl"


def test_panel_injects_content_max_css_var() -> None:
    panel = Panel.make("admin").content_max_width("screen-lg")
    html = panel.render_shell("<div class='or-page'>x</div>")
    assert "--or-content-max: 64rem" in html
    assert panel.to_dict()["content_max_width"] == "screen-lg"


def test_table_list_card_structure() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .filters([SelectFilter.make("status").options({"a": "A", "b": "B"})])
        .records([SimpleNamespace(title="Hello")])
    )
    html = table.render()
    assert "or-list-card" in html
    assert "or-list-toolbar" in html
    assert "or-list-table-scroll" in html
    assert "or-list-row" in html


def test_panel_nav_fluent_aliases_and_theme_system() -> None:
    panel = (
        Panel.make("admin")
        .apps_navigation()
        .sidebar_navigation()
        .top_navigation()
        .apps_navigation()
    )
    assert panel._navigation_layout == "apps"
    html = panel.render_shell("<div class='or-page'>ok</div>")
    assert "cycleTheme" in html
    assert "or-theme-icon-system" in html
    assert "data-theme-preference" in html


def test_sidebar_css_has_no_body_divider() -> None:
    from pathlib import Path

    css = Path("packages/panels/src/almasix/orbit/resources/css/orbit.css").read_text(
        encoding="utf-8"
    )
    start = css.find("\n.or-sidebar {")
    assert start >= 0
    chunk = css[start : start + 200]
    assert "border-right" not in chunk


def test_table_bulk_hidden_until_selection() -> None:
    from almasix.orbit.actions.action import DeleteBulkAction

    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .bulk_actions([DeleteBulkAction.make()])
        .records([SimpleNamespace(id=1, title="Hello")])
    )
    html = table.render()
    assert 'x-data="orbitTableSelection"' in html
    assert 'x-show="selectionCount > 0"' in html
    assert "or-row-check" in html
    assert "or-td-select" in html
    assert "data-tooltip=" not in html  # nav-only; sanity
    assert "data-total=" in html
    assert "selectAllResults()" in html
    assert "or-ta-selection-indicator" in html
    assert "Deselect all" in html
    assert "Bulk actions" in html
