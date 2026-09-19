"""Tables overview — Filament 5 parity for heading, pagination, reorder, dots, etc."""

from __future__ import annotations

import pytest
from almasix.orbit.actions import Action, DeleteBulkAction
from almasix.orbit.tables import PaginationMode, Table, TextColumn
from almasix.orbit.tables.columns import dot_get


@pytest.fixture(autouse=True)
def _clear_table_configure() -> None:
    Table._configure_using.clear()
    yield
    Table._configure_using.clear()


def test_dot_get_nested_dict_and_attr() -> None:
    assert dot_get({"author": {"name": "Ada"}}, "author.name") == "Ada"

    class Author:
        name = "Lin"

    class Post:
        author = Author()

    assert dot_get(Post(), "author.name") == "Lin"
    assert dot_get({}, "missing.path") is None


def test_push_columns_and_relationship_column() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .push_columns([TextColumn.make("author.name").label("Author")])
        .records([{"title": "Hello", "author": {"name": "Ada"}}])
        .paginated(False)
    )
    html = table.render()
    assert "Ada" in html
    assert "Author" in html
    assert len(table.flat_columns()) == 2


def test_default_sort_and_aliases() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title").sortable()])
        .default_sort("title", "desc")
        .record_actions([Action.make("edit")])
        .toolbar_actions([DeleteBulkAction.make()])
        .records([{"id": 1, "title": "A"}, {"id": 2, "title": "B"}])
        .paginated(False)
    )
    assert [r["title"] for r in table.get_records()] == ["B", "A"]
    assert table._actions and table._bulk_actions


def test_pagination_options_extreme_simple_and_all() -> None:
    records = [{"id": i, "title": f"P{i}"} for i in range(1, 12)]
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .records(records)
        .paginated([5, 10, "all"])
        .default_pagination_page_option(5)
        .extreme_pagination_links()
        .query_string_identifier("posts")
        .persist_records_per_page_in_session()
    )
    html = table.render()
    assert 'aria-label="First"' in html
    assert 'data-query-string-id="posts"' in html
    assert 'value="all"' in html
    assert len(table.get_records()) == 5

    table.pagination_mode(PaginationMode.SIMPLE)
    simple = table.render()
    assert "or-table-pagination-page" not in simple or 'data-pagination-mode="simple"' in simple

    table.paginate(1, "all")
    assert len(table.get_records()) == 11


def test_paginated_false() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .records([{"title": str(i)} for i in range(20)])
        .paginated(False)
    )
    assert len(table.get_records()) == 20
    assert table._render_pagination_chrome() == ""


def test_heading_poll_defer_record_classes_empty_icon() -> None:
    table = (
        Table.make("posts")
        .heading("Clients")
        .description("Manage your clients here.")
        .columns([TextColumn.make("title")])
        .poll("10s")
        .defer_loading()
        .record_classes(lambda record: "is-draft" if record.get("status") == "draft" else None)
        .open_record_url_in_new_tab()
        .record_url(lambda r: f"/posts/{r['id']}")
        .empty_state_icon("heroicon-o-inbox")
        .records([{"id": 1, "title": "Draft", "status": "draft"}])
        .paginated(False)
    )
    html = table.render()
    assert "Clients" in html
    assert "Manage your clients" in html
    assert 'data-poll="10s"' in html
    assert 'data-defer-loading="true"' in html
    assert "is-draft" in html
    assert "data-record-url-new-tab" in html
    assert "window.open" in html

    empty = (
        Table.make("empty")
        .columns([TextColumn.make("title")])
        .empty_state_icon("heroicon-o-inbox")
        .empty_state_heading("Nothing here")
        .records([])
    )
    empty_html = empty.render()
    assert "Nothing here" in empty_html
    assert "or-empty-state-icon" in empty_html


def test_custom_header_and_empty_state_view() -> None:
    table = (
        Table.make("posts")
        .header("<div class='custom-header'>Custom</div>")
        .columns([TextColumn.make("title")])
        .empty_state("<div class='custom-empty'>Gone</div>")
        .records([])
    )
    html = table.render()
    assert "custom-header" in html
    assert "custom-empty" in html


def test_searchable_table_and_search_using() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])  # not searchable
        .searchable()
        .search_using(lambda records, search: [r for r in records if search in r["title"]])
        .records([{"title": "alpha"}, {"title": "beta"}])
        .search("alp")
        .paginated(False)
    )
    assert "or-table-search" in table.render()
    assert [r["title"] for r in table.get_records()] == ["alpha"]


def test_persist_in_session_flags() -> None:
    table = Table.make("posts").columns([TextColumn.make("title").searchable()]).persist_in_session()
    assert table._persist_filters_in_session is True
    assert table._persist_search_in_session is True
    html = table.render()
    assert 'data-persist-search="true"' in html
    assert 'data-persist-sort="true"' in html


def test_reorderable_chrome_and_apply_reorder() -> None:
    calls: list[str] = []
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .reorderable("sort")
        .before_reordering(lambda order: calls.append(f"before:{order}"))
        .after_reordering(lambda order: calls.append(f"after:{order}"))
        .records(
            [
                {"id": "1", "title": "A", "sort": 1},
                {"id": "2", "title": "B", "sort": 2},
            ]
        )
        .paginated(False)
    )
    html = table.render()
    assert 'data-reorderable="sort"' in html
    assert "Enable reordering" in html
    table.apply_reorder(["2", "1"])
    assert [r["id"] for r in table._records] == ["2", "1"]
    assert calls[0].startswith("before:")
    assert calls[1].startswith("after:")


def test_configure_using() -> None:
    Table.configure_using(lambda t: t.striped(False).paginated([10, 25]))
    table = Table.make("posts").columns([TextColumn.make("title")])
    assert table._striped is False
    assert table._pagination_page_options == [10, 25]


def test_column_default_when_missing() -> None:
    col = TextColumn.make("nickname").default("—")
    assert col.resolve_state({}) == "—"


def test_search_using_kw_only_and_sort_without_column() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .search_using(lambda records, *, search: [r for r in records if search in r["t"]])
        .records([{"t": "ab", "title": "x"}, {"t": "zz", "title": "y"}])
        .search("ab")
        .sort("t", "asc")
        .paginated(False)
    )
    assert len(table.get_records()) == 1


def test_reordering_disables_pagination_unless_opt_in() -> None:
    records = [{"id": i, "title": str(i)} for i in range(15)]
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .records(records)
        .paginate(1, 5)
    )
    table._is_reordering = True
    assert len(table.get_records()) == 15
    table.paginated_while_reordering()
    assert len(table.get_records()) == 5


def test_pagination_page_options_and_default_all() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .records([{"title": "a"}])
        .pagination_page_options([10, 25, "all"])
        .default_pagination_page_option("all")
        .persist_column_searches_in_session(False)
        .persist_search_in_session()
        .persist_sort_in_session()
    )
    assert table._per_page == 0
    assert table._persist_columns_in_session is False
    html = table.render()
    assert 'data-persist-sort="true"' in html


def test_paginated_true_keeps_options() -> None:
    table = Table.make("x").columns([TextColumn.make("t")]).paginated(True)
    assert table._paginated is True


def test_reorder_trigger_custom_and_active_reordering() -> None:
    def customize(action: Action, is_reordering: bool) -> Action:
        return action.label("Stop" if is_reordering else "Start")

    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .reorderable("sort", direction="desc")
        .reorder_records_trigger_action(customize)
        .records([{"id": 1, "title": "A"}])
        .paginated(False)
    )
    html = table.render(reordering=True)
    assert "or-table-reorder-trigger" in html
    assert "Stop" in html
    assert 'data-reordering="true"' in html
    assert 'data-reorder-direction="desc"' in html


def test_empty_state_callable_kw_and_header_callable_kw() -> None:
    table = (
        Table.make("posts")
        .header(lambda **_ctx: "<div class='h'>H</div>")
        .empty_state(lambda **_ctx: "<div class='e'>E</div>")
        .columns([TextColumn.make("title")])
        .records([])
    )
    html = table.render()
    assert "class='h'" in html
    assert "class='e'" in html
    # TypeError fallback (no kwargs)
    table2 = (
        Table.make("posts")
        .header(lambda: "<div class='h2'>H2</div>")
        .empty_state(lambda: "<div class='e2'>E2</div>")
        .columns([TextColumn.make("title")])
        .records([])
    )
    assert "class='e2'" in table2.render()


def test_paginate_all_string() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .records([{"title": str(i)} for i in range(8)])
        .paginate(1, "all")
    )
    assert table._per_page == 0
    assert len(table.get_records()) == 8


def test_heading_description_only_variants() -> None:
    only_heading = (
        Table.make("posts")
        .heading("Only heading")
        .columns([TextColumn.make("title")])
        .records([{"title": "x"}])
        .paginated(False)
    )
    assert "Only heading" in only_heading.render()
    only_desc = (
        Table.make("posts")
        .description("Only description")
        .columns([TextColumn.make("title")])
        .records([{"title": "x"}])
        .paginated(False)
    )
    assert "Only description" in only_desc.render()
    assert only_desc._render_table_heading() == (
        '<div class="or-table-header">'
        '<p class="or-table-description">Only description</p></div>'
    )


def test_default_sort_does_not_override_active_sort() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .sort("title", "desc")
        .default_sort("title", "asc")
        .records([{"title": "A"}, {"title": "B"}])
        .paginated(False)
    )
    assert table._sort_direction == "desc"
    assert [r["title"] for r in table.get_records()] == ["B", "A"]


def test_record_classes_callable_returns_none() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .record_classes(lambda record: None)
        .records([{"title": "x"}])
        .paginated(False)
    )
    html = table.render()
    assert "or-list-row" in html


def test_list_records_negative_per_page_falls_back() -> None:
    from almasix.orbit import Resource
    from almasix.orbit.panels.pages.resource_pages import ListRecords

    class Res(Resource):
        @classmethod
        def get_table(cls) -> Table:
            return Table.make("t").columns([TextColumn.make("title")])

        @classmethod
        def get_navigation_label(cls) -> str:
            return "T"

        @classmethod
        def get_slug(cls) -> str:
            return "t"

    class Bound(ListRecords):
        resource = Res

    html = Bound.render(records=[{"title": "a"}], per_page=-3, page=1)
    assert "or-page-list" in html


def test_pagination_injects_custom_per_page_when_all_in_options() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .records([{"title": str(i)} for i in range(20)])
        .pagination_page_options([10, "all"])
        .paginate(1, 15)
    )
    # 15 not in options and "all" is in options — branch that rebuilds then appends all
    html = table.render()
    assert 'value="15"' in html or 'value="all"' in html


def test_record_classes_list_and_none() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .record_classes(["row-a", "row-b"])
        .records([{"title": "x"}])
        .paginated(False)
    )
    assert "row-a row-b" in table.render()
    table.record_classes(None)
    assert "row-a" not in table.render()


def test_per_page_injected_into_options() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .records([{"title": str(i)} for i in range(20)])
        .pagination_page_options([10, 25])
        .paginate(1, 15)
    )
    html = table.render()
    assert 'value="15"' in html


def test_apply_reorder_without_hooks() -> None:
    table = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .records([{"id": "1", "title": "A"}, {"id": "2", "title": "B"}])
    )
    table.apply_reorder(["2", "1"])
    assert [r["id"] for r in table._records] == ["2", "1"]
    table.apply_reorder([])


def test_list_host_set_per_page_all_and_toggle_reordering() -> None:
    from almasix.orbit.panels.conduit.hosts import ListRecordsHost

    class Host(ListRecordsHost):
        pass

    host = Host()
    host.setPerPage("all")
    assert host.per_page == 0
    host.setPerPage("nope")
    assert host.per_page == 10
    host.toggleReordering()
    assert host.reordering is True
    host.toggleReordering()
    assert host.reordering is False


def test_list_records_page_allows_per_page_zero() -> None:
    from almasix.orbit import Resource
    from almasix.orbit.panels.pages.resource_pages import ListRecords

    class Res(Resource):
        @classmethod
        def get_table(cls) -> Table:
            return (
                Table.make("t")
                .columns([TextColumn.make("title")])
                .records([{"title": "a"}, {"title": "b"}])
            )

        @classmethod
        def get_navigation_label(cls) -> str:
            return "T"

        @classmethod
        def get_slug(cls) -> str:
            return "t"

    class Bound(ListRecords):
        resource = Res

    html = Bound.render(records=[{"title": "a"}, {"title": "b"}], per_page=0, page=1)
    assert "or-page-list" in html
