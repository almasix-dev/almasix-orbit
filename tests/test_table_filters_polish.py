"""Filter indicators, SelectFilter defaults, and index polish coverage."""

from __future__ import annotations

from almasix.orbit.panels.conduit.hosts import ListRecordsHost
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.tables import SelectFilter, Table, TernaryFilter, TextColumn


class _Post(Resource):
    model = type("Post", (), {})
    navigation_label = "Posts"
    slug = "posts"
    records = [
        {"id": 1, "title": "Alpha", "status": "draft", "featured": True},
        {"id": 2, "title": "Beta", "status": "published", "featured": False},
        {"id": 3, "title": "Gamma", "status": "published", "featured": True},
    ]

    @classmethod
    def get_records(cls):
        return list(cls.records)

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status"),
            ]
        ).filters(
            [
                SelectFilter.make("status").options(
                    {"draft": "Draft", "published": "Published"}
                )
            ]
        ).empty_state_heading("Nothing here").empty_state_description("Create your first post.")


def test_select_filter_default_apply_and_indicators() -> None:
    panel = Panel.make("admin").path("admin").resources([_Post]).login(False)
    host_cls = ListRecordsHost.bind(panel=panel, resource=_Post)
    host = host_cls(table_filters={"status": "published"})
    host.mount()
    html = host.render()
    assert "Beta" in html and "Gamma" in html
    assert "Alpha" not in html
    assert "or-filters-trigger" in html
    assert "or-filters-panel" in html
    assert "or-filters-panel-title" in html
    assert "setTableFilter('status'" in html
    assert "filtersOpen" in html
    assert "toggleFilters" in html
    assert "or-filter-chip" in html
    assert "Published" in html
    assert "resetTableFilters" in html
    assert "removeTableFilter('status')" in html
    assert "or-list-toolbar-end" in html and "or-table-search" in html
    assert 'aria-label="Filter"' in html

    host.setTableFilter("status", "draft")
    assert host.table_filters == {"status": "draft"}
    assert host.page == 1
    host.setTableFilter("status", "")
    assert host.table_filters == {}
    host.removeTableFilter("status")
    assert host.table_filters == {}
    host.table_filters = {"status": "draft"}
    host.resetTableFilters()
    assert host.table_filters == {}
    host.applyTableFilters({"status": "published"})
    assert host.table_filters == {"status": "published"}
    assert host.page == 1


def test_ternary_filter_defaults() -> None:
    rows = [
        {"id": 1, "featured": True},
        {"id": 2, "featured": False},
        {"id": 3, "featured": 1},
    ]
    filt = TernaryFilter.make("featured")
    assert list(filt.get_options()) == ["", "1", "0"]
    assert len(filt.apply(rows, "")) == 3
    assert [r["id"] for r in filt.apply(rows, "1")] == [1, 3]
    assert [r["id"] for r in filt.apply(rows, "0")] == [2]


def test_empty_state_actions_and_record_url() -> None:
    table = (
        Table.make()
        .columns([TextColumn.make("title")])
        .records([])
        .empty_state_heading("Empty")
        .empty_state_description("Add one")
        .header_actions([])
        .empty_state_actions([])
        .record_url(lambda record, **_: f"/posts/{record.get('id')}")
    )
    # with header create via empty fallback path — use records + record_url on row
    filled = (
        Table.make()
        .columns([TextColumn.make("title")])
        .records([{"id": 9, "title": "Nine"}])
        .record_url(lambda record, **_: f"/view/{record['id']}")
    )
    html = filled.render()
    assert "or-tr-clickable" in html
    assert 'data-record-url="/view/9"' in html
    assert "or-table-record-card-title" in html

    empty = table.render()
    assert "Empty" in empty and "Add one" in empty


def test_resource_default_record_url() -> None:
    table = _Post.get_table()
    assert table._record_url is not None
    url = table._resolve_record_url({"id": 2})
    assert url and "2" in url


def test_deferred_filters_and_empty_create_cta() -> None:
    table = (
        Table.make()
        .columns([TextColumn.make("title")])
        .filters([SelectFilter.make("status").options({"a": "A"})])
        .defer_filters()
        .filter_state({"status": "a"})
        .records([])
        .header_actions([])
    )
    # Attach a create-like header action via empty_state_actions
    from almasix.orbit.actions.action import Action

    table.empty_state_actions([Action.make("create").label("Create").url("/create")])
    html = table.render(skip_header_actions=True)
    assert "Apply filters" in html and "data-defer-filters" in html
    assert "applyDeferred()" in html
    assert "or-filters-trigger" in html
    assert "or-filter-chip" in html
    assert "Create" in html and "or-empty-state-actions" in html

    host = ListRecordsHost.bind(
        panel=Panel.make("admin").path("admin").resources([_Post]).login(False),
        resource=_Post,
    )()
    host.mount()
    host.removeTableFilter("")
    host.selected = ["1", "2"]
    html2 = host.render()
    assert "data-selected=" in html2
    assert "orbitDropdown" in html2
    assert "menuOpen" in html2
    assert "or-th-actions" in html2
    assert "wire:ignore" in html2 and "conduit:ignore" in html2
    assert "or-select-all" in html2
    assert ":checked=\"pageFullySelected\"" not in html2
    assert "data-total=" in html2
    assert "selectAllResults()" in html2
    assert "or-ta-selection-indicator" in html2
    assert "Deselect all" in html2
    assert "Bulk actions" in html2
    host.select_all = True
    host.selected = ["1"]
    assert host.get_selected_ids() == ["1", "2", "3"]
    host.select_all = False
    assert host.get_selected_ids() == ["1"]


def test_filter_apply_branches_and_record_url_callable() -> None:
    rows = [{"id": 1, "status": "a", "flag": True}, {"id": 2, "status": "b", "flag": False}]
    assert SelectFilter.make(None).apply(rows, "a") == rows
    assert SelectFilter.make("").apply(rows, "a") == rows
    assert SelectFilter.make("status").apply(rows, "") == rows
    assert SelectFilter.make("status").apply(rows, None) == rows
    assert SelectFilter.make("status").query(lambda q, v: q).apply(rows, "x") == rows
    obj_rows = [type("R", (), {"status": "a", "flag": False})()]
    assert len(SelectFilter.make("status").apply(obj_rows, "a")) == 1
    assert TernaryFilter.make(None).apply(rows, "1") == rows
    assert len(TernaryFilter.make("flag").apply(obj_rows, "0")) == 1
    assert TernaryFilter.make("flag").query(lambda q, v: []).apply(rows, "1") == []

    silent = (
        Table.make()
        .columns([TextColumn.make("title")])
        .filters([SelectFilter.make("status").options({"a": "A"})])
        .filter_state({"status": "a"})
        .records([{"id": 1, "title": "t", "status": "a"}])
    )
    silent._filters[0]._indicate = False
    silent._filters[0]._name = None  # type: ignore[attr-defined]
    assert "or-filter-chip" not in silent.render()

    nameless = (
        Table.make()
        .columns([TextColumn.make("title")])
        .filters([SelectFilter.make(None).options({"a": "A"})])
        .filter_state({"": "a"})
        .records([{"id": 1, "title": "t"}])
    )
    assert "or-filter-chip" not in nameless.render()

    def _url(record, *, panel=None):
        return f"/p/{record['id']}"

    linked = (
        Table.make()
        .columns([TextColumn.make("title")])
        .records([{"id": 3, "title": "C"}])
        .record_url(_url)
    )
    assert 'data-record-url="/p/3"' in linked.render(panel="x")

    def _url2(record):
        return f"/q/{record['id']}"

    linked2 = (
        Table.make()
        .columns([TextColumn.make("title")])
        .records([{"id": 4, "title": "D"}])
        .record_url(_url2)
    )
    assert "/q/4" in linked2.render()

    assert 'data-record-url="/posts"' in (
        Table.make()
        .columns([TextColumn.make("title")])
        .records([{"id": 5, "title": "E"}])
        .record_url("/posts")
        .render()
    )
    assert Table.make().record_url(lambda _r, **_: "")._resolve_record_url({}) is None


def test_grid_layout_empty_header_cta_and_card_cell() -> None:
    from almasix.orbit.actions.action import Action
    from almasix.orbit.tables.columns import Column

    class _Plain(Column):
        def render_cell(self, record: object, **ctx: object) -> str:
            return str(record.get("title") if isinstance(record, dict) else "")  # type: ignore[union-attr]

    grid = Table.make().layout("grid").content_grid({"md": 2, "xl": 4, "sm": 1})
    assert grid._content_grid is not None
    html = (
        Table.make()
        .columns([_Plain.make("title"), TextColumn.make("status")])
        .records([{"id": 1, "title": "Card", "status": "ok"}])
        .content_grid({"md": 2, "xl": 3})
        .layout("grid")
        .render()
    )
    assert "or-table-content-grid" in html
    assert "or-table-record-card-title" in html
    assert "data-grid-sm" not in html or "data-grid-md" in html

    empty = (
        Table.make()
        .columns([TextColumn.make("title")])
        .records([])
        .header_actions([Action.make("create").label("New").url("/new")])
        .render(skip_header_actions=True)
    )
    assert "New" in empty and "or-empty-state-actions" in empty


def test_filter_attribute_alignment_and_pagination_window() -> None:
    from almasix.orbit.tables.table import _pagination_pages

    rows = [{"id": 1, "state": "open"}, {"id": 2, "state": "closed"}]
    filt = SelectFilter.make("status").attribute("state").options({"open": "Open"})
    assert filt.get_attribute() == "state"
    assert [r["id"] for r in filt.apply(rows, "open")] == [1]

    col = TextColumn.make("amount").align_end().label("Amount")
    assert TextColumn.make("x").align_start().get_alignment() == "start"
    assert TextColumn.make("y").align_center().get_alignment() == "center"
    html = (
        Table.make()
        .columns([TextColumn.make("title"), col])
        .records([{"id": 1, "title": "A", "amount": "9"}])
        .render()
    )
    assert "or-align-end" in html

    assert _pagination_pages(1, 1) == [1]
    assert _pagination_pages(1, 0) == []
    assert _pagination_pages(1, 5) == [1, 2, 3, 4, 5]
    assert None in _pagination_pages(5, 20)
    assert _pagination_pages(5, 20)[0] == 1
    assert _pagination_pages(5, 20)[-1] == 20
