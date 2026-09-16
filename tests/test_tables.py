"""Tests for almasix.orbit.tables."""

from __future__ import annotations

from almasix.orbit.actions.action import EditAction
from almasix.orbit.tables.columns import (
    BadgeColumn,
    BooleanColumn,
    CheckboxColumn,
    ColorColumn,
    Column,
    ColumnGroup,
    IconColumn,
    ImageColumn,
    SelectColumn,
    TagsColumn,
    TextColumn,
    TextInputColumn,
    ToggleColumn,
    ViewColumn,
)
from almasix.orbit.tables.filters import Filter, FilterGroup, SelectFilter, TernaryFilter
from almasix.orbit.tables.table import Table


def test_table_sort_search_paginate_render() -> None:
    records = [
        {"name": "Charlie", "active": True, "color": "#f00", "tags": "a,b", "img": "/a.png"},
        {"name": "Alice", "active": False, "color": "#0f0", "tags": ["x"], "img": ""},
        {"name": "Bob", "active": True, "color": None, "tags": [], "img": "/b.png"},
    ]
    table = (
        Table.make()
        .columns(
            [
                TextColumn.make("name").sortable().searchable().label("Name"),
                BooleanColumn.make("active"),
                BadgeColumn.make("name").color("primary"),
            ]
        )
        .records(records)
        .actions([EditAction.make()])
        .filters([SelectFilter.make("active")])
        .bulk_actions([])
        .header_actions([])
        .query("unused")
        .search("ali")
        .sort("name", "asc")
        .paginate(1, 10)
        .empty_state_heading("Empty")
        .empty_state_description("None yet")
        .striped()
    )
    found = table.get_records()
    assert len(found) == 1 and found[0]["name"] == "Alice"
    assert table.get_total() == 1
    html = table.render()
    assert "or-table-striped" in html and "Alice" in html and "Actions" in html
    d = table.to_dict()
    assert d["total"] == 1

    empty = Table.make().columns([TextColumn.make("name")]).records([]).render()
    assert "or-empty-state" in empty

    page2 = (
        Table.make()
        .columns([TextColumn.make("name").searchable()])
        .records(records)
        .sort("name", "desc")
        .paginate(1, 2)
    )
    assert [r["name"] for r in page2.get_records()] == ["Charlie", "Bob"]
    unpaged = Table.make().columns([TextColumn.make("name")]).records(records)
    unpaged._paginated = False
    assert len(unpaged.get_records()) == 3

    obj_table = Table.make().columns([TextColumn.make("name").searchable()]).records(
        [type("R", (), {"name": "Zed"})()]
    )
    assert obj_table.search("zed").get_total() == 1
    # sort via object attribute path
    objs = [type("R", (), {"name": n})() for n in ("b", "a")]
    sorted_rows = (
        Table.make().columns([TextColumn.make("name")]).records(objs).sort("name").get_records()
    )
    assert [r.name for r in sorted_rows] == ["a", "b"]


def test_columns_render_variants() -> None:
    rec = {"name": "LongNameHere", "ok": 1, "img": "/x.png", "color": "#abc", "tags": ["a", "b"]}
    col = (
        TextColumn.make("name")
        .sortable()
        .searchable()
        .toggleable(False)
        .format_state_using(lambda v: v.upper())
        .badge()
        .boolean(False)
        .color(lambda **_: "success")
        .limit(4)
        .wrap()
        .url("/r")
        .weight("bold")
        .copyable()
    )
    assert col.is_sortable() and col.is_searchable()
    assert col.resolve_state(rec) == "LONG…"
    cell = col.render_cell(rec)
    assert "or-badge" in cell and "or-color-success" in cell
    assert "Yes" in BooleanColumn.make("ok").render_cell(rec)
    assert "or-avatar" in ImageColumn.make("img").render_cell(rec)
    assert ImageColumn.make("img").render_cell({"img": ""}) == '<td class="or-td"></td>'
    assert "or-color-swatch" in ColorColumn.make("color").render_cell(rec)
    assert "or-badge" in TagsColumn.make("tags").render_cell(rec)
    assert "or-badge" in TagsColumn.make("tags").render_cell({"tags": "x, y"})
    assert Column.make("name").to_dict()["sortable"] is False
    group = ColumnGroup.make("g").columns([TextColumn.make("name")])
    assert len(group._columns) == 1
    for cls in (
        IconColumn,
        SelectColumn,
        CheckboxColumn,
        TextInputColumn,
        ToggleColumn,
        ViewColumn,
        BadgeColumn,
    ):
        assert cls.make("x").get_name() == "x"


def test_filters_apply() -> None:
    f = Filter.make("status").options({"a": "A"}).query(lambda q, v: [r for r in q if r == v])
    assert f.apply([1, 2], None) == [1, 2]
    assert f.apply([1, 2], 2) == [2]
    assert isinstance(SelectFilter.make("s"), Filter)
    assert isinstance(TernaryFilter.make("t"), Filter)
    g = FilterGroup.make("g").filters([f])
    assert len(g._filters) == 1
