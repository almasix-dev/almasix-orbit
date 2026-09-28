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


def test_resource_pages_inherit_panel_width_and_full_stays_inside_it() -> None:
    """Unset pages use the panel cap. ``full`` fills that cap, not the viewport."""
    from almasix.orbit.forms import Form, TextInput
    from almasix.orbit.panels.conduit.hosts import CreateRecordHost
    from almasix.orbit.panels.pages import resource_pages as rp
    from almasix.orbit.panels.resource import Resource

    class PlainResource(Resource):
        slug = "plain"
        records_mutable = True

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("name")])

    class FullResource(Resource):
        slug = "fulls"
        records_mutable = True
        content_max_width = "full"

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("name")])

    class MaxWFullResource(Resource):
        slug = "maxw"
        content_max_width = "max-w-full"

    for operation in ("list", "create", "edit", "view"):
        assert rp._resource_width_style(PlainResource, operation=operation) == ""

    panel = Panel.make("admin").content_max_width("screen-2xl").path("/")
    create = CreateRecordHost.bind(panel=panel, resource=PlainResource)()
    create.mount()
    fragment = create.render()
    assert "max-width:" not in fragment
    assert "--or-content-max: 96rem" in panel.render_shell(fragment)

    full_style = rp._resource_width_style(FullResource, operation="create")
    assert "var(--or-content-max, 96rem)" in full_style
    assert "100%" not in full_style
    assert "var(--or-content-max, 96rem)" in rp._resource_width_style(
        MaxWFullResource, operation="list"
    )

    full_page = CreateRecordHost.bind(panel=panel, resource=FullResource)()
    full_page.mount()
    page = full_page.render()
    assert "max-width: var(--or-content-max, 96rem)" in page
    assert "max-width: 100%" not in page
    narrow = Panel.make("narrow").content_max_width("screen-lg").path("/n")
    wrapped = narrow.render_shell(page)
    assert "--or-content-max: 64rem" in wrapped
    assert "max-width: 100%" not in wrapped


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
