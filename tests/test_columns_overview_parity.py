"""Columns overview shared API parity (Filament tables/columns/overview)."""

from __future__ import annotations

import pytest
from almasix.orbit.panels.conduit.hosts import ListRecordsHost
from almasix.orbit.tables import Column, Table, TextColumn


@pytest.fixture(autouse=True)
def _clear_configure_using() -> None:
    Column._configure_using.clear()
    yield
    Column._configure_using.clear()


def test_state_default_placeholder_and_tooltip() -> None:
    col = (
        TextColumn.make("nickname")
        .state(lambda record: record.get("nickname"))
        .default("fallback")
        .placeholder("No nickname")
        .tooltip("cell tip")
        .header_tooltip("header tip")
    )
    assert col.resolve_state({"nickname": None}) == "fallback"
    assert col.resolve_state({"nickname": "Ada"}) == "Ada"
    empty = col.state(None).default(None).placeholder("Empty")
    cell = empty.render_cell({"nickname": None})
    assert "or-cell-placeholder" in cell
    assert "Empty" in cell
    assert 'title="cell tip"' in col.render_cell({"nickname": "x"})
    table = Table.make().columns([col]).records([{"nickname": "x"}])
    html = table.render()
    assert 'title="header tip"' in html


def test_sortable_searchable_multi_key_and_query() -> None:
    records = [
        {"id": 1, "first": "Ada", "last": "Lovelace"},
        {"id": 2, "first": "Grace", "last": "Hopper"},
        {"id": 3, "first": "Ada", "last": "Byron"},
    ]
    col = TextColumn.make("full").sortable(["last", "first"]).searchable(["first", "last"])
    table = (
        Table.make()
        .columns([col])
        .records(records)
        .sort("full", "asc")
    )
    names = [(r["last"], r["first"]) for r in table.get_records()]
    assert names == [("Byron", "Ada"), ("Hopper", "Grace"), ("Lovelace", "Ada")]

    table.search("hop")
    assert [r["id"] for r in table.get_records()] == [2]

    def sort_query(records: list, direction: str) -> list:
        return sorted(records, key=lambda r: r["id"], reverse=(direction == "desc"))

    qcol = TextColumn.make("id").sortable(query=sort_query)
    t2 = Table.make().columns([qcol]).records(records).sort("id", "desc")
    assert [r["id"] for r in t2.get_records()] == [3, 2, 1]

    scol = TextColumn.make("first").searchable(
        query=lambda record, search: str(record.get("last", "")).lower().startswith(search)
    )
    t3 = Table.make().columns([scol]).records(records).search("lov")
    assert [r["id"] for r in t3.get_records()] == [1]


def test_width_grow_wrap_header_url_new_tab_attrs() -> None:
    col = (
        TextColumn.make("site")
        .width(120)
        .grow()
        .wrap_header()
        .vertically_align_center()
        .url("https://example.com")
        .open_url_in_new_tab()
        .extra_cell_attributes({"data-cell": "1"})
        .extra_header_attributes({"data-head": "1"})
        .extra_attributes({"data-extra": "yes"})
    )
    cell = col.render_cell({"site": "x"})
    assert 'target="_blank"' in cell
    assert 'data-cell="1"' in cell
    assert 'data-extra="yes"' in cell
    assert "or-col-grow" in cell
    assert "or-v-align-center" in cell
    assert "width:120px" in cell

    table = Table.make().columns([col]).records([{"site": "x"}])
    html = table.render()
    assert "or-th-wrap" in html
    assert 'data-head="1"' in html


def test_hidden_visible_and_column_order() -> None:
    a = TextColumn.make("a")
    b = TextColumn.make("b")
    hidden = TextColumn.make("secret").hidden()
    table = (
        Table.make()
        .columns([a, b, hidden])
        .records([{"a": 1, "b": 2, "secret": 3}])
        .column_order(["b", "a"])
        .reorderable_columns()
    )
    assert [c.get_name() for c in table.display_columns()] == ["b", "a"]
    html = table.render(column_order=["b", "a"])
    assert "or-columns-item-draggable" in html
    assert html.index(">B<") < html.index(">A<") or "data-sort-column=\"b\"" in html


def test_column_configure_using() -> None:
    Column.configure_using(lambda c: c.align_end())
    col = TextColumn.make("x")
    assert col.get_alignment() == "end"


def test_host_reorder_columns() -> None:
    from almasix.orbit import Resource

    class Demo(Resource):
        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns(
                [TextColumn.make("a").toggleable(), TextColumn.make("b").toggleable()]
            ).records([{"a": 1, "b": 2}]).reorderable_columns()

        @classmethod
        def get_records(cls) -> list:
            return [{"a": 1, "b": 2}]

    host = ListRecordsHost()
    host.get_resource = lambda: Demo  # type: ignore[method-assign]
    host.records = [{"a": 1, "b": 2}]
    host.reorderColumns(["b", "a"])
    assert host.column_order == ["b", "a"]
    host.reorderColumns('["a","b"]')
    assert host.column_order == ["a", "b"]
    host.reorderColumns(None)
    assert host.column_order == []
    host.reorderColumns("b, a")
    assert host.column_order == ["b", "a"]
    host.reorderColumns("not-json")
    assert host.column_order == ["not-json"]
    host.reorderColumns(42)
    assert host.column_order == []
    host.resetColumnOrder()
    assert host.column_order == []


def test_attrs_html_bool_and_alignment_helpers() -> None:
    from almasix.orbit.tables.columns import ColumnGroup, _attrs_to_html

    assert 'disabled' in _attrs_to_html({"disabled": True, "x": False, "y": None})
    col = (
        TextColumn.make("n")
        .vertically_align_start()
        .vertically_align_end()
        .sortable(False)
        .searchable(False)
        .width("10rem")
        .extra_cell_attributes({"style": "color:red"})
        .extra_header_attributes({"style": "font-weight:700"})
    )
    assert col.get_vertical_alignment() == "end"
    assert "width:10rem" in col._width_style()
    cell = col.render_cell({"n": "x"})
    assert "color:red" in cell
    table = Table.make().columns([col]).records([{"n": "x"}])
    assert "font-weight:700" in table.render()

    # boolean empty without placeholder
    assert "No" in TextColumn.make("ok").boolean().render_cell({"ok": None})

    # search query: evaluate returns non-bool, positional call TypeErrors
    def kw_only(*, record, search):  # type: ignore[no-untyped-def]
        return "hit" if search in str(record.get("x", "")).lower() else ""

    weird3 = TextColumn.make("x").searchable(query=kw_only)
    assert weird3.matches_search({"x": "Hello"}, "hel") is True
    assert weird3.matches_search({"x": "Nope"}, "zz") is False

    # sort query positional / kw-only fallbacks
    def sort_pos(records, direction):  # type: ignore[no-untyped-def]
        return sorted(records, key=lambda r: r["id"], reverse=direction == "desc")

    def sort_kw(*, records, direction):  # type: ignore[no-untyped-def]
        return sorted(records, key=lambda r: r["id"], reverse=direction == "desc")

    rows = [{"id": 1}, {"id": 2}]
    t_pos = (
        Table.make()
        .columns([TextColumn.make("id").sortable(query=sort_pos)])
        .records(rows)
        .sort("id", "desc")
    )
    assert [r["id"] for r in t_pos.get_records()] == [2, 1]

    t_kw = (
        Table.make()
        .columns([TextColumn.make("id").sortable(query=sort_kw)])
        .records(rows)
        .sort("id", "asc")
    )
    assert [r["id"] for r in t_kw.get_records()] == [1, 2]

    def sort_fallback(*args, **kwargs):  # type: ignore[no-untyped-def]
        if kwargs and not args:
            raise TypeError("kwargs")
        if not args and not kwargs:
            raise TypeError("empty")
        if len(args) == 2 and not kwargs:
            raise TypeError("positional pair")
        records = args[0]
        direction = kwargs.get("direction", "asc")
        return sorted(records, key=lambda r: r["id"], reverse=direction == "desc")

    t_fb = (
        Table.make()
        .columns([TextColumn.make("id").sortable(query=sort_fallback)])
        .records(rows)
        .sort("id", "desc")
    )
    assert [r["id"] for r in t_fb.get_records()] == [2, 1]

    # ColumnGroup ordering via first child name
    table = (
        Table.make()
        .columns(
            [
                TextColumn.make("z"),
                ColumnGroup.make("G", [TextColumn.make("a"), TextColumn.make("b")]),
            ]
        )
        .column_order(["a", "z"])
        .records([{"z": 1, "a": 2, "b": 3}])
    )
    names = []
    for col in table._ordered_top_level():
        if isinstance(col, ColumnGroup):
            names.append("G")
        else:
            names.append(col.get_name())
    assert names[0] == "G"

    # Group with no matching child names stays at end
    table2 = (
        Table.make()
        .columns(
            [
                ColumnGroup.make("Other", [TextColumn.make("x")]),
                TextColumn.make("z"),
            ]
        )
        .column_order(["z"])
        .records([{"z": 1, "x": 2}])
    )
    ordered = table2._ordered_top_level()
    assert ordered[0].get_name() == "z"
    assert isinstance(ordered[1], ColumnGroup)
