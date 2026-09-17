"""Index table search / sort / pagination chrome and ListRecordsHost wiring."""

from __future__ import annotations

from almasix.orbit.panels.conduit.hosts import ListRecordsHost
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.tables import Table, TextColumn


class _Post(Resource):
    model = type("Post", (), {})
    navigation_label = "Posts"
    slug = "posts"
    records = [
        {"id": i, "title": f"Post {i:02d}", "status": "draft" if i % 2 else "published"}
        for i in range(1, 16)
    ]

    @classmethod
    def get_records(cls):
        return list(cls.records)

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status").sortable(),
            ]
        )


def _host(**state):
    panel = Panel.make("admin").path("admin").resources([_Post]).login(False)
    host_cls = ListRecordsHost.bind(panel=panel, resource=_Post)
    host = host_cls(**state)
    host.mount()
    return host


def test_list_host_applies_search_sort_paginate() -> None:
    host = _host(table_search="Post 01", table_sort="title", table_sort_direction="asc", page=1, per_page=10)
    html = host.render()
    assert "or-table-search" in html
    assert "setTableSearch($event.target.value)" in html
    assert "Post 01" in html
    assert "Post 02" not in html
    assert "or-th-sortable" in html
    assert "sortBy('title')" in html


def test_list_host_sort_by_toggles_direction() -> None:
    host = _host()
    host.sortBy("title")
    assert host.table_sort == "title"
    assert host.table_sort_direction == "asc"
    host.sortBy("title")
    assert host.table_sort_direction == "desc"
    host.sortBy("status")
    assert host.table_sort == "status"
    assert host.table_sort_direction == "asc"
    assert host.page == 1


def test_list_host_pagination_actions() -> None:
    host = _host(per_page=5)
    html = host.render()
    assert "or-table-pagination" in html
    assert "Showing 1 to 5 of 15 results" in html
    assert "gotoPage(2)" in html
    assert "gotoPage(3)" in html
    assert "setPerPage($event.target.value)" in html
    assert "or-per-page-split" in html
    assert "or-per-page-select" in html
    assert "Per page" in html
    assert 'aria-current="page">1</button>' in html
    assert "or-table-pagination-nav" in html
    assert "or-table-pagination-page" in html

    host.gotoPage(2)
    html2 = host.render()
    assert "Showing 6 to 10 of 15 results" in html2
    assert "Post 06" in html2

    host.setPerPage(25)
    assert host.per_page == 25
    assert host.page == 1
    html3 = host.render()
    assert "Showing 1 to 15 of 15 results" in html3

    host.table_search = "Post 99"
    host.clearSearch()
    assert host.table_search == ""
    host.setTableSearch("Post 01")
    assert host.table_search == "Post 01"
    assert host.page == 1


def test_table_sort_header_and_pagination_meta() -> None:
    table = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status").sortable(),
            ]
        )
        .records(
            [
                {"id": i, "title": f"T{i}", "status": "a" if i % 2 else "b"}
                for i in range(1, 12)
            ]
        )
        .search("T1")
        .sort("title", "desc")
        .paginate(1, 5)
    )
    html = table.render()
    assert "or-th-sorted-desc" in html
    assert html.count("or-th-sort-icon-wrap") == 2
    assert "or-th-sort-icon-active" in html
    assert 'data-sort-column="status"' in html
    assert "or-table-search-input" in html
    assert "Clear" in html
    assert "or-table-pagination" in html
    assert "Showing 1 to 3 of 3 results" in html
    meta = table.pagination_meta()
    assert meta["total"] == 3  # T1, T10, T11
    assert meta["from"] == 1
    assert table.has_searchable_columns() is True

    asc = (
        Table.make()
        .columns([TextColumn.make("title").sortable()])
        .records([{"id": 1, "title": "A"}])
        .sort("title", "asc")
        .paginate(1, 10)
    )
    asc_html = asc.render()
    assert "or-th-sorted-asc" in asc_html
    assert "heroicon-o-chevron-up" in asc_html or "chevron-up" in asc_html or 'd="m4.5 15.75' in asc_html


def test_pagination_edge_cases_and_host_guards() -> None:
    table = (
        Table.make()
        .columns([TextColumn.make("title")])
        .records([{"id": 1, "title": "A"}])
    )
    table._paginated = False
    assert table._render_pagination_chrome() == ""
    meta = table.pagination_meta()
    assert meta["last_page"] == 1 and meta["to"] == 1

    empty = Table.make().columns([TextColumn.make("title")]).records([]).paginate(1, 10)
    assert empty._render_pagination_chrome() == ""

    over = (
        Table.make()
        .columns([TextColumn.make("title").sortable()])
        .records([{"id": i, "title": f"R{i}"} for i in range(5)])
        .paginate(99, 2)
    )
    assert len(over.get_records()) == 1  # clamped to last page
    assert over._page == 3
    html = over.paginate(1, 15).render()
    assert 'value="15" selected' in html
    assert "or-per-page-select" in html

    host = _host()
    host.sortBy("")
    assert host.table_sort == ""
    host.gotoPage("nope")
    assert host.page == 1
    host.setPerPage("x")
    assert host.per_page == 10

    from almasix.orbit.panels.pages.resource_pages import ListRecords

    class Bound(ListRecords):
        pass

    Bound.resource = _Post  # type: ignore[misc]
    html2 = Bound.render(records=_Post.get_records(), page="bad", per_page="bad")
    assert "or-table-pagination" in html2


def test_toolbar_filters_above_search_and_row_action_dropdown() -> None:
    host = _host()
    html = host.render()
    tools_idx = html.find("or-list-toolbar-tools")
    search_idx = html.find("or-table-search")
    assert tools_idx != -1 and search_idx != -1
    assert tools_idx < search_idx
    assert "or-list-toolbar-divider" in html
    assert "or-action-group" in html
    assert "heroicon-o-ellipsis-vertical" in html or "or-btn-icon" in html


def test_column_manager_toggle_and_summaries_flag() -> None:
    from almasix.orbit.tables import Count, Sum

    table = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").searchable().sortable().toggleable(),
                TextColumn.make("views")
                .toggleable()
                .summarize(Sum.make().label("Total"), Count.make()),
            ]
        )
        .records([{"id": i, "title": f"T{i}", "views": i} for i in range(1, 6)])
        .paginate(1, 10)
        .summaries(page=True, all=False)
    )
    html = table.render()
    assert "or-table-columns" in html
    assert 'data-sort-column="title"' in html
    assert "or-tfoot" in html or "or-summary-row" in html
    assert 'data-summary-scope="page"' in html
    assert 'data-summary-scope="all"' not in html

    hidden = table.toggled_columns({"title": True, "views": False}).render()
    assert "<th class=\"or-th\">Views</th>" not in hidden
    assert 'data-summary-scope="page"' not in hidden

    host = _host()
    host.toggleColumn("title")
    assert host.toggled_columns.get("title") is False
    html_hidden = host.render()
    assert 'data-sort-column="title"' not in html_hidden
    host.toggleColumn("title", True)
    assert host.toggled_columns.get("title") is True
    host.toggleColumn("title", "false")
    assert host.toggled_columns.get("title") is False
    html2 = host.render()
    assert "toggleColumn('title', $event.target.checked)" in html2
    host.resetToggledColumns()
    assert host.toggled_columns == {}
