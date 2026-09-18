"""Extra coverage for column types, list host mutations, and related chrome."""

from __future__ import annotations

import sys
from datetime import date, datetime
from types import ModuleType

from almasix.orbit.actions.action import Action, CreateAction, EditAction
from almasix.orbit.forms.components import TextInput
from almasix.orbit.panels.conduit.hosts import ListRecordsHost
from almasix.orbit.panels.pages.resource_pages import EditRecord, Tab, ViewRecord
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.support.urls import resolve_public_url
from almasix.orbit.tables import (
    ColumnGroup,
    Grid,
    Group,
    IconColumn,
    ImageColumn,
    SelectColumn,
    Split,
    Stack,
    Table,
    TextColumn,
    View,
)
from almasix.orbit.tables.filters import SelectFilter
from almasix.orbit.tables.summaries import Range, Sum


class _Obj:
    def __init__(self, **kwargs: object) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_record_id_and_column_edge_paths() -> None:
    class NoId:
        pass

    assert "or-td" in TextColumn.make("x").render_cell(NoId())
    col = TextColumn.make("n").summarize(["not-a-summarizer", Sum.make().label("S")])
    assert len(col.get_summarizers()) == 2
    assert TextColumn.make("d").date()._format_display_value("not-a-date") == "not-a-date"
    assert "or-align-end" in TextColumn.make("a").alignment("end")._td_classes("extra")
    colored = TextColumn.make("s").color(lambda record, state, **_: "warning").render_cell({"s": "x"})
    assert "or-color-warning" in colored
    icon = (
        IconColumn.make("flag")
        .true_icon("heroicon-o-check-circle")
        .false_icon("heroicon-o-x-circle")
        .size("lg")
        .boolean()
        .render_cell({"flag": True})
    )
    assert "or-icon-size-lg" in icon
    empty_img = ImageColumn.make("u").render_cell({"u": None})
    assert empty_img == '<td class="or-td"></td>'
    defaulted = ImageColumn.make("u").default_image_url("/fallback.png").render_cell({"u": None})
    assert "/fallback.png" in defaulted
    named = ImageColumn.make("u").size("md").render_cell({"u": "http://a"})
    assert "or-avatar-md" in named
    group = ColumnGroup.make([TextColumn.make("a"), TextColumn.make("b")]).label("Pair")
    assert len(group.get_columns()) == 2


def test_money_date_list_and_object_columns() -> None:
    money = TextColumn.make("cents").money("USD", divide_by=100).render_cell({"cents": 1234})
    assert "USD" in money and "12.34" in money
    assert "2024-01-02" in TextColumn.make("d").date().render_cell({"d": date(2024, 1, 2)})
    assert "2024" in TextColumn.make("d").date_time().render_cell(
        {"d": datetime(2024, 1, 2, 3, 4)}
    )
    assert "2024" in TextColumn.make("d").date().render_cell({"d": "2024-05-06T12:00:00"})
    listed = TextColumn.make("tags").list_with_line_breaks().render_cell({"tags": ["a", "b"]})
    assert "a" in listed and "b" in listed
    obj = _Obj(id=7, title="Hello")
    assert 'data-record-id="7"' in SelectColumn.make("title").options({"Hello": "H"}).render_cell(obj)


def test_layout_view_grid_to_dict_and_null_content() -> None:
    rec = {"a": "1"}
    grid = Grid.make([TextColumn.make("a")]).columns(3)
    assert grid.to_dict()["columns"] == 3
    view = View.make([TextColumn.make("a")])
    assert "or-layout-view" in view.render_cell(rec)
    null_body = View.make([TextColumn.make("a")]).content(lambda **_: None).render_cell(rec)
    assert "or-layout-view" in null_body
    split = Split.make([TextColumn.make("a")]).from_("md").collapsible().collapsed()
    assert "or-split-from-md" in split.render_cell(rec)
    stack = Stack.make([TextColumn.make("a")]).space(2)
    assert "or-stack" in stack.render_cell(rec)


def test_summaries_inherit_column_money_and_numeric() -> None:
    col = TextColumn.make("amount").money("EUR", divide_by=1)
    s = Sum.make().label("Total").hidden_label()
    html = s.render(state=12.5, column=col)
    assert "or-sr-only" in html
    assert "EUR" in html
    num_col = TextColumn.make("n").numeric(3)
    s2 = Sum.make()
    assert s2._format_for_column(1.5, num_col) == "1.500"
    assert s2._format_for_column("nope", num_col) == s2.format_value("nope")
    bad_money = Sum.make()._format_for_column("x", col)
    assert bad_money == Sum.make().format_value("x")
    rng = Range.make().minimal_textual_difference()
    assert rng.format_value(("alpha", "alpine")) != ""


def test_table_chrome_groups_pagination_summaries_select_all() -> None:
    group_a = Group.make("status").label("Status")
    group_b = Group.make("kind").label("Kind")
    records = [
        {"id": 1, "title": "A", "status": "a", "kind": "x", "note": "n1", "amount": 10},
        {"id": 2, "title": "B", "status": "b", "kind": "y", "note": "n2", "amount": 20},
    ] + [
        {"id": i, "title": f"R{i}", "status": "a", "kind": "x", "note": "n", "amount": i}
        for i in range(3, 60)
    ]
    table = (
        Table.make()
        .columns(
            [
                TextColumn.make("title")
                .searchable()
                .sortable()
                .visible_from("md")
                .hidden_from("xl"),
                TextColumn.make("amount").money("USD").summarize(Sum.make().label("Total")),
                ColumnGroup.make("Meta", [TextColumn.make("kind").label("Kind").sortable()]),
                Split.make([TextColumn.make("note").label("Note")]),
            ]
        )
        .filters([SelectFilter.make("status").options({"a": "A"})])
        .defer_filters()
        .groups([group_a, group_b])
        .default_group(group_a)
        .actions([Action.make("ping").label("Ping")])
        .actions_as_dropdown(False)
        .bulk_actions([Action.make("delete_bulk").label("Delete")])
        .header_actions([CreateAction.make().label("New")])
        .records(records)
        .paginate(3, 5)
        .summaries(page=True, all=True)
    )
    html = table.render(
        table_group="kind",
        toggled_columns={"title": True},
        selected=["1"],
        select_all=True,
    )
    assert "or-table-pagination" in html
    assert "Meta" in html
    assert "or-summary" in html
    assert 'data-select-all="true"' in html
    assert table.actions_as_dropdown(True) is table

    hidden = (
        Table.make()
        .columns(
            [
                TextColumn.make("gone").toggleable(is_toggled_hidden_by_default=True),
                ColumnGroup.make(
                    "Empty",
                    [TextColumn.make("gone2").toggleable(is_toggled_hidden_by_default=True)],
                ),
            ]
        )
        .records([{"gone": 1, "gone2": 2}])
        .render()
    )
    assert "or-th-group" not in hidden


def test_action_object_record_and_form_schema() -> None:
    obj = _Obj(id=42, title="Hi")
    edit = (
        EditAction.make()
        .modal()
        .form([TextInput.make("title")])
        .render(obj, record=obj)
    )
    assert 'data-record-id="42"' in edit
    assert "Hi" in edit
    assert Action.make("x").get_form_schema() == []
    assert Action.make("x").call() is None
    assert (
        Action.make("x")
        .requires_confirmation(False)
        .without_confirmation(False)
        .needs_confirmation()
        is False
    )


def test_list_host_mutations_and_filtered_selection() -> None:
    class Demo(Resource):
        model = type("X", (), {})
        records_mutable = True
        records = [
            {"id": 1, "title": "A", "status": "draft"},
            {"id": 2, "title": "B", "status": "published"},
            _Obj(id=3, title="C", status="draft"),
        ]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def get_tabs(cls):
            return [
                Tab("all").modify_query_using(lambda rows: rows),
                Tab("drafts").modify_query_using(
                    lambda rows: [
                        r
                        for r in rows
                        if (r.get("status") if isinstance(r, dict) else r.status) == "draft"
                    ]
                ),
            ]

        @classmethod
        def table(cls, table):
            return table.columns(
                [
                    TextColumn.make("title").searchable().sortable().toggleable(),
                    TextColumn.make("status").toggleable(),
                ]
            ).filters(
                [SelectFilter.make("status").options({"draft": "Draft", "published": "Pub"})]
            )

    panel = Panel.make("cov-host").path("/cov-host")
    Host = ListRecordsHost.bind(panel=panel, resource=Demo)
    host = Host()
    host.mount()
    host.setTableFilter("", "x")
    host.applyTableFilters({"status": "", "ok": "draft"})
    assert host.table_filters == {"ok": "draft"}
    host.setTableGroup("status")
    assert host.table_group == "status"
    host.toggleColumn("")
    host.toggleColumn("title", "yes")
    host.table_search = "A"
    host.table_sort = "title"
    host.table_sort_direction = "desc"
    host.table_filters = {"status": "draft"}
    assert host._filtered_table() is not None
    host.select_all = True
    ids = host.get_selected_ids()
    assert "1" in ids
    host.updateColumnState("1", "title", "AA")
    assert host.records[0]["title"] == "AA"
    host.update_column_state("", "title", "x")
    host.update_column_state("3", "title", "CC")
    assert any(getattr(r, "title", None) == "CC" for r in host.records)
    host.selected = ["1", "2"]
    host.select_all = False
    host.mountAction("delete_bulk")
    assert all(host._record_key(r) not in {"1", "2"} for r in host.records)
    host.records = [{"id": "x", "title": "Z"}, _Obj(id=9, title="Y")]
    host.mountAction("create", data={"title": "N"})
    host.mountAction("edit", record_id="9", data={"title": "YY"})
    assert any(getattr(r, "title", None) == "YY" for r in host.records)
    host.mountAction("edit", record_id="x", data={"title": "ZZ"})
    assert any(isinstance(r, dict) and r.get("title") == "ZZ" for r in host.records)
    host.mountAction("force_delete", record_id="x")
    assert all(host._record_key(r) != "x" for r in host.records)
    host.mountAction("custom_ping", record_id="9")


def test_tab_badge_callable_and_resource_width_pages() -> None:
    tab = Tab("drafts").badge(lambda: 3).badge_color("info")
    assert tab.resolve_badge() == 3
    assert "or-list-tab-badge" in tab.render(active=True)

    class Wide(Resource):
        model = type("W", (), {})
        content_max_width = "7xl"
        records = [{"id": 1, "title": "T"}]

        @classmethod
        def form(cls, form):
            return form.schema([TextInput.make("title")])

        @classmethod
        def infolist(cls, infolist):
            from almasix.orbit.infolists.components import TextEntry

            return infolist.schema([TextEntry.make("title")])

    EditRecord.resource = Wide
    ViewRecord.resource = Wide
    assert "max-width" in EditRecord.render(record={"id": 1, "title": "T"})
    assert "max-width" in ViewRecord.render(record=_Obj(id=1, title="T"))


def test_more_edge_hits_for_coverage_gate() -> None:
    # summarize() else branch with a bare non-Summarizer / non-sequence arg
    assert "raw" in TextColumn.make("n").summarize("raw").get_summarizers()
    # date ValueError path (has "T" but invalid iso)
    assert TextColumn.make("d").date()._format_display_value("not-a-dateTxx") == "not-a-dateTxx"
    # boolean text branch in Column.render_cell
    assert "Yes" in TextColumn.make("on").boolean().render_cell({"on": True})
    # empty form schema early return
    assert Action.make("x")._render_form_fields({"a": 1}) == ""
    # columns chrome with nothing toggleable
    bare = Table.make().columns([TextColumn.make("t").toggleable(False)]).records([{"t": 1}])
    assert bare._render_columns_chrome() == ""
    # layout column under column-group headers (non-sortable th path)
    html = (
        Table.make()
        .columns(
            [
                ColumnGroup.make("G", [TextColumn.make("a").label("A")]),
                Split.make([TextColumn.make("b").label("B")]),
            ]
        )
        .records([{"a": 1, "b": 2}])
        .render()
    )
    assert "or-tr-group-headers" in html
    # object setattr failure in update_column_state
    class Frozen:
        __slots__ = ("id",)

        def __init__(self) -> None:
            self.id = 1

    class Mini(Resource):
        model = type("M", (), {})
        records = [Frozen()]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def table(cls, table):
            return table.columns([TextColumn.make("id")])

    host = ListRecordsHost.bind(panel=Panel.make("fz").path("/fz"), resource=Mini)()
    host.mount()
    host.update_column_state("1", "title", "nope")
    # Tab badge callable TypeError → zero-arg retry
    assert Tab("t2").badge(lambda: 9).resolve_badge(record={}) == 9
    assert Tab("t3").badge(lambda: None).resolve_badge(record={}) is None
    # summaries all-only footer when page summaries disabled
    only_all = (
        Table.make()
        .columns([TextColumn.make("amount").summarize(Sum.make())])
        .records([{"amount": 1}, {"amount": 2}])
        .paginate(1, 10)
        .summaries(page=False, all=True)
        .render()
    )
    assert "or-summary" in only_all


def test_resolve_public_url_absolute_stripping() -> None:
    def fake_url(path: str) -> str:
        if path.startswith("proto"):
            return "//cdn.example/asset.png"
        if path.startswith("abs"):
            return "https://cdn.example/logo.svg?v=1"
        return f"/{path.lstrip('/')}"

    mod = ModuleType("almasix.routing.url")
    mod.url = fake_url  # type: ignore[attr-defined]
    sys.modules["almasix.routing.url"] = mod
    try:
        assert resolve_public_url("abs/logo.svg") == "/logo.svg?v=1"
        assert resolve_public_url("proto/x") == "//cdn.example/asset.png"
        assert resolve_public_url("local/x.png").startswith("/")
    finally:
        sys.modules.pop("almasix.routing.url", None)
