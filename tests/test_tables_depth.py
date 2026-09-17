"""Depth tests for table summaries / grouping / layout and action presets.

These modules are standalone until the parent wires them into ``Table.render`` /
``Column.summarize`` (forms currently owns ``table.py`` / ``columns.py`` / ``action.py``).
"""

from __future__ import annotations

from datetime import date, datetime

from almasix.orbit.actions.action import DeleteAction, EditAction
from almasix.orbit.actions.import_export import ExportAction, ImportAction
from almasix.orbit.actions.presets import (
    ActionGroup,
    ForceDeleteAction,
    ForceDeleteBulkAction,
    ReplicateAction,
    RestoreAction,
    RestoreBulkAction,
)
from almasix.orbit.tables.columns import TextColumn
from almasix.orbit.tables.grouping import Group, GroupBucket
from almasix.orbit.tables.layout import Panel, Split, Stack
from almasix.orbit.tables.summaries import Average, Count, Range, Sum, Summarizer

# --- Summaries -----------------------------------------------------------------


def test_sum_average_count_range() -> None:
    records = [
        {"amount": 10, "rating": 4, "sku": "aaa"},
        {"amount": 20, "rating": 5, "sku": "zzz"},
        {"amount": None, "rating": 3, "sku": "mmm"},
    ]
    assert Sum.make().attribute("amount").summarize(records) == 30.0
    avg = Average.make().attribute("rating").summarize(records)
    assert avg == 4.0
    assert Count.make().summarize(records) == 3
    assert Count.make().attribute("amount").summarize(records) == 2
    rng = Range.make().attribute("amount").summarize(records)
    assert rng == (10.0, 20.0) or rng == (10, 20)


def test_summarizer_using_query_format_and_render() -> None:
    records = [{"n": 100}, {"n": 200}, {"n": 50}]
    custom = (
        Summarizer.make("custom")
        .label("Half sum")
        .using(lambda records, attribute=None, **_: sum(r["n"] for r in records) / 2)
    )
    assert custom.summarize(records) == 175.0
    scoped = Sum.make().attribute("n").query(lambda records, **_: [r for r in records if r["n"] >= 100])
    assert scoped.summarize(records) == 300.0

    money = Sum.make().attribute("n").money("EUR", divide_by=100, decimal_places=2)
    assert money.format_value(money.summarize(records)) == "EUR 3.50"
    numeric = Average.make().attribute("n").numeric(decimal_places=1)
    assert numeric.format_value(150) == "150.0"
    prefixed = Sum.make().prefix("Total: ").suffix(" pts").format_value(3)
    assert prefixed == "Total: 3 pts"
    limited = Range.make().limit(3).format_value(("abcdef", "zzzzzz"))
    assert limited.endswith("…")

    html = Sum.make("s").label("Sum").attribute("n").render(records=records, attribute="n")
    assert "or-summary-Sum" in html and "Sum" in html
    hidden = Sum.make().label("Hidden").hidden_label().render(state=1)
    assert "or-sr-only" in hidden
    assert Sum.make().hidden().render(state=1) == ""
    d = Sum.make().to_dict()
    assert d["type"] == "Sum"


def test_count_icons_and_range_variants() -> None:
    records = [{"icon": "a"}, {"icon": "b"}, {"icon": "a"}, {"icon": None}]
    html = Count.make().icons().attribute("icon").render(records=records, attribute="icon")
    assert "or-summary-icons" in html and 'data-icon="a"' in html

    dates = [{"d": "2024-01-01 10:00"}, {"d": "2024-01-02 11:00"}]
    r = Range.make().attribute("d").minimal_date_time_difference()
    assert r.format_value(r.summarize(dates)) == "2024-01-01 – 2024-01-02"
    same_day = [{"d": "2024-01-01 10:00"}, {"d": "2024-01-01 11:00"}]
    assert "10:00" in r.format_value(r.summarize(same_day))

    text = Range.make().attribute("sku").minimal_textual_difference()
    skus = [{"sku": "apple"}, {"sku": "apricot"}]
    formatted = text.format_value(text.summarize(skus))
    assert "ap" in formatted and "–" in formatted

    with_null = Range.make().attribute("x").exclude_null(False)
    assert with_null.summarize([{"x": None}, {"x": 1}]) is not None

    empty = Range.make().attribute("n").summarize([])
    assert empty is None
    assert Average.make().attribute("n").summarize([]) is None
    assert Sum.make().attribute("n").summarize([]) == 0.0

    objs = [type("R", (), {"n": 2})(), type("R", (), {"n": 4})()]
    assert Sum.make().attribute("n").summarize(objs) == 6.0


def test_summarizer_query_non_list_and_non_numeric() -> None:
    records = [{"n": "x"}, {"n": 5}]
    assert Sum.make().attribute("n").summarize(records) == 5.0
    # query returning iterable that's not a list
    s = Sum.make().attribute("n").query(lambda records, **_: (r for r in records if r["n"] == 5))
    assert s.summarize(records) == 5.0
    # using wins over calculate
    assert Sum.make().using(lambda **_: 99).summarize([{"n": 1}]) == 99
    assert Summarizer.make().summarize([]) is None
    assert Range.make().format_value(None) == ""
    assert Range.make().format_value(("a", "a")) == "a"
    money_bad = Sum.make().money("USD")._format_scalar("nope")
    assert money_bad == "nope"

    # query returning None / non-iterable falls back
    assert Sum.make().attribute("n").query(lambda **_: None).summarize([{"n": 2}]) == 2.0
    assert Sum.make().attribute("n").query(lambda **_: 123).summarize([{"n": 2}]) == 2.0
    assert Sum.make().get_attribute() is None or Sum.make("n").get_attribute() == "n"
    assert Sum.make().is_label_hidden() is False
    assert Sum.make().hidden_label().is_label_hidden() is True

    # format branches: int-looking float, decimal numeric, None scalar, non-numeric numeric()
    assert Sum.make().numeric()._format_scalar(3.0) == "3"
    assert Sum.make().numeric()._format_scalar(3.5) == "3.5"
    assert Sum.make().numeric()._format_scalar(None) == ""
    assert Sum.make().numeric()._format_scalar("na") == "na"
    assert Sum.make().format_value(None) == ""
    # identical date range
    same = Range.make().minimal_date_time_difference().format_value(("2024-01-01", "2024-01-01"))
    assert same == "2024-01-01"
    short_dates = Range.make().minimal_date_time_difference().format_value(("x", "y"))
    assert "–" in short_dates
    # incomparable range values fall back to str
    mixed_range = Range.make().attribute("v").exclude_null(False)
    assert mixed_range.summarize([{"v": 1}, {"v": "z"}]) is not None
    # Count without icons falls through to super().render
    assert "or-summary-Count" in Count.make().label("N").render(state=3)
    # Count icons WITH visible label
    assert "Total" in Count.make().label("Total").icons().render(
        records=[{"icon": "a"}], attribute="icon"
    )
    # Range minimal text identical strings
    assert Range.make().minimal_textual_difference().format_value(("aa", "aa")) == "aa"
    # Range minimal_date with non-str tuple still formats via _minimal_dates
    assert "1" in Range.make().minimal_date_time_difference().format_value((1, 2))
    # hidden label branch in Summarizer.render
    assert "or-sr-only" in Sum.make("amt").label("Amt").hidden_label().render(state=1)
    # no label
    assert "or-summary-value" in Sum.make().render(state=1)


# --- Grouping ------------------------------------------------------------------


def test_group_partition_and_render() -> None:
    records = [
        {"status": "draft", "title": "A"},
        {"status": "published", "title": "B"},
        {"status": "draft", "title": "C"},
    ]
    group = Group.make("status").label("Status").collapsible()
    buckets = group.partition(records)
    assert len(buckets) == 2
    draft = next(b for b in buckets if b.key == "draft")
    assert len(draft.records) == 2
    assert "Status: draft" in draft.title

    no_prefix = Group.make("status").title_prefixed_with_label(False)
    assert no_prefix.title_from_record(records[0]) == "draft"

    custom = (
        Group.make("status")
        .get_key_from_record_using(lambda record, **_: record["status"].upper())
        .get_title_from_record_using(lambda record, **_: record["status"].title())
        .get_description_from_record_using(lambda record, **_: "desc")
        .direction("desc")
    )
    parts = custom.partition(records)
    assert parts[0].key in {"DRAFT", "PUBLISHED"}
    assert parts[0].description == "desc"
    header = custom.render_header(parts[0], colspan=3, collapsed=True)
    assert "or-group-header" in header and 'colspan="3"' in header

    html = group.render(records=records, colspan=2)
    assert "or-group-header" in html and "draft" in html
    assert group.to_dict()["collapsible"] is True
    assert isinstance(buckets[0], GroupBucket)


def test_group_date_and_dot_path() -> None:
    records = [
        {"created_at": datetime(2024, 1, 1, 12, 0), "author": {"name": "Ada"}},
        {"created_at": date(2024, 1, 1), "author": {"name": "Ada"}},
        {"created_at": "2024-01-02T09:00:00", "author": {"name": "Bob"}},
    ]
    by_date = Group.make("created_at").date()
    buckets = by_date.partition(records)
    assert len(buckets) == 2

    by_author = Group.make("author.name").title_prefixed_with_label(False)
    authors = by_author.partition(records)
    assert {b.key for b in authors} == {"Ada", "Bob"}

    # missing nested path
    assert Group.make("author.missing").key_from_record({"author": {}}) is None
    assert Group.make("author.missing").key_from_record({"author": None}) is None
    obj = type("R", (), {})()
    obj.author = type("A", (), {"name": "Zoe"})()
    assert Group.make("author.name").key_from_record(obj) == "Zoe"

    mixed = Group.make("x").partition([{"x": 1}, {"x": "a"}])
    assert len(mixed) == 2

    g = (
        Group.make("status")
        .collapsible()
        .direction("asc")
        .order_query_using(lambda q, direction, **_: q)
        .scope_query_by_key_using(lambda q, key, **_: q)
        .group_query_using(lambda q, **_: q)
    )
    assert g.is_collapsible() is True
    assert g.get_direction() == "asc"
    assert g._order_query is not None and g._scope_query is not None and g._group_query is not None
    # empty label + prefix still yields title body
    bare = Group.make("status")
    bare._label = ""
    assert bare.title_from_record({"status": "x"}) == "x" or "x" in bare.title_from_record({"status": "x"})
    # custom title returning None
    none_title = Group.make("status").get_title_from_record_using(lambda **_: None)
    assert none_title.title_from_record({"status": "x"}) == ""


# --- Layout --------------------------------------------------------------------


def test_split_stack_panel_render_cell() -> None:
    record = {"name": "Ada", "email": "a@x.com", "phone": "123"}
    split = (
        Split.make(
            [
                TextColumn.make("name"),
                Stack.make([TextColumn.make("email"), TextColumn.make("phone")])
                .space(1)
                .alignment("end")
                .visible_from("md"),
            ]
        )
        .from_breakpoint("md")
        .grow(False)
    )
    cell = split.render_cell(record)
    assert cell.startswith('<td class="or-td or-td-layout">')
    assert "or-split" in cell and "or-stack" in cell and "or-split-from-md" in cell
    assert "Ada" in cell and "a@x.com" in cell

    assert split.from_("lg")._from == "lg"
    flat = split.flat_columns()
    assert [c.get_name() for c in flat] == ["name", "email", "phone"]

    panel = Panel.make([TextColumn.make("name")]).collapsible().collapsed(False)
    phtml = panel.render_cell(record)
    assert "or-panel" in phtml and 'data-collapsed="false"' in phtml

    # make with name string
    named = Split.make("row").schema([TextColumn.make("name")])
    assert named.get_name() == "row"
    assert "or-split" in named.render(record=record)
    d = named.to_dict()
    assert d["components"] and d["grow"] is True

    hidden = Stack.make([TextColumn.make("name")]).hidden()
    assert hidden.render_cell(record) == ""

    # nested layout via render_cell_inner path + non-column child
    from almasix.orbit.support.component import Component

    class Plain(Component):
        def render(self, state=None, **ctx):
            return "<span>plain</span>"

    nested = Stack.make([Split.make([TextColumn.make("name")]), Plain.make("p")])
    assert "plain" in nested.render_cell_inner(record)
    assert "or-layout-item" in nested.render_cell_inner(record)

    # components() alias, hidden_from, collapsible split/stack, non-td render_cell
    stacked = (
        Stack.make("s")
        .components([TextColumn.make("name")])
        .hidden_from("sm")
        .collapsible()
        .collapsed(True)
    )
    assert stacked.get_components()[0].get_name() == "name"
    assert "or-hidden-from-sm" in stacked.render_cell_inner(record)
    assert 'data-collapsible="true"' in stacked.render_cell_inner(record)
    assert 'data-collapsible="true"' in Split.make([TextColumn.make("name")]).collapsible().render_cell_inner(
        record
    )

    class OddColumn(TextColumn):
        def render_cell(self, record, **ctx):
            return "<span>odd</span>"

    odd = Stack.make([OddColumn.make("name")])
    assert "odd" in odd.render_cell_inner(record)

    class Layoutish(Split):
        pass

    # child with render_cell_inner only (no render_cell) — LayoutComponent path
    inner_only = Stack.make([Layoutish.make([TextColumn.make("name")])])
    assert "or-split" in inner_only.render_cell_inner(record)

    # invisible child skipped
    skipped = Stack.make([TextColumn.make("name").hidden()])
    assert skipped.render_cell_inner(record) == "" or "Ada" not in skipped.render_cell_inner(record)

    # td-like but not closed with </td>
    class AlmostTd(TextColumn):
        def render_cell(self, record, **ctx):
            return "<td class='x'>partial"

    assert "partial" in Stack.make([AlmostTd.make("name")]).render_cell_inner(record)

    # child with only render_cell_inner (mask render_cell)
    class InnerOnly(Component):
        def render_cell_inner(self, record, **ctx):
            return "<em>inner</em>"

    assert "inner" in Stack.make([InnerOnly.make("i")]).render_cell_inner(record)

    import pytest

    with pytest.raises(NotImplementedError):
        from almasix.orbit.tables.layout import LayoutComponent

        LayoutComponent.make().render_cell_inner(record)


# --- Action presets ------------------------------------------------------------


def test_action_presets_and_import_export() -> None:
    rep = ReplicateAction.make().exclude_attributes(["id", "slug"])
    assert rep.get_label() == "Replicate"
    assert rep.get_exclude_attributes() == ["id", "slug"]
    assert rep.to_dict()["exclude_attributes"] == ["id", "slug"]

    force = ForceDeleteAction.make()
    assert force._requires_confirmation is True and force._color == "danger"
    assert ForceDeleteBulkAction.make().get_label() == "Force delete selected"
    assert RestoreAction.make()._color == "success"
    assert RestoreBulkAction.make().get_label() == "Restore selected"

    imported: list[str] = []
    imp = (
        ImportAction.make()
        .importer(lambda path, **_: imported.append(path) or 1)
        .accepted_file_types([".csv"])
        .options({"delimiter": ","})
    )
    assert imp.get_importer() is not None
    assert imp.call("/tmp/x.csv") == 1 and imported == ["/tmp/x.csv"]
    assert imp.to_dict()["has_importer"] is True
    assert 'data-import="true"' in imp.render()

    exp = (
        ExportAction.make()
        .exporter(lambda **_: "csv-bytes")
        .formats(["csv", "xlsx"])
        .columns(["name"])
        .filename(lambda **_: "posts")
    )
    assert exp.get_exporter() is not None
    assert exp.call() == "csv-bytes"
    assert exp.get_filename() == "posts"
    assert ExportAction.make().filename(lambda **_: None).get_filename() == "export"
    assert 'data-export="true"' in exp.render()
    assert exp.to_dict()["formats"] == ["csv", "xlsx"]

    # action() overrides importer/exporter
    assert ImportAction.make().action(lambda: "via-action").call() == "via-action"
    assert ExportAction.make().action(lambda: "via-action").call() == "via-action"
    assert ImportAction.make().call() is None
    assert ExportAction.make().call() is None
    assert ImportAction.make().hidden().render() == ""
    assert ExportAction.make().authorize(False).render() == ""


def test_action_group_dropdown_and_button_group() -> None:
    group = ActionGroup.make([EditAction.make(), DeleteAction.make()]).label("More")
    html = group.render()
    assert "or-dropdown" in html and "or-dropdown-menu" in html
    assert "Edit" in html and "Delete" in html

    btn = ActionGroup.make("g").actions([EditAction.make()]).button_group()
    assert "or-btn-group" in btn.render()
    assert btn.flat_actions()[0].get_name() == "edit"
    assert btn.get_actions()[0].get_name() == "edit"
    # dropdown() toggles back from button group
    assert ActionGroup.make([EditAction.make()]).button_group().dropdown().to_dict()["dropdown"] is True

    nested = ActionGroup.make([ActionGroup.make([EditAction.make()]), DeleteAction.make()])
    assert len(nested.flat_actions()) == 2
    assert nested.to_dict()["dropdown"] is True

    empty = ActionGroup.make([EditAction.make().hidden()])
    assert empty.render() == ""
    assert ActionGroup.make().hidden().render() == ""
    assert ActionGroup.make([EditAction.make()]).authorize(False).render() == ""

    # package re-exports
    from almasix.orbit.actions import ActionGroup as AG
    from almasix.orbit.tables import Average as Avg
    from almasix.orbit.tables import Group as G
    from almasix.orbit.tables import Split as S

    assert AG is ActionGroup and Avg is Average and G is Group and S is Split


# --- Column / filter / action depth ------------------------------------------------


def test_column_summarize_money_date_description() -> None:
    from almasix.orbit.tables.columns import TextColumn

    col = (
        TextColumn.make("amount")
        .summarize([Sum.make().label("Total"), Average.make().label("Avg")])
        .money("USD", divide_by=100)
        .description("Gross amount in cents")
    )
    assert len(col.get_summarizers()) == 2
    rec = {"amount": 12345}
    cell = col.render_cell(rec)
    assert "USD 123.45" in cell and "data-description=" in cell
    assert col.to_dict()["has_summarizers"] is True

    date_col = TextColumn.make("created_at").date("%d/%m/%Y")
    assert "15/01/2024" in date_col.render_cell({"created_at": "2024-01-15"})
    assert "01/2024" in date_col.render_cell(
        {"created_at": datetime(2024, 1, 15, 12, 0)}
    )


def test_trashed_filter() -> None:
    from almasix.orbit.tables.filters import TrashedFilter

    rows = [
        {"id": 1, "deleted_at": None},
        {"id": 2, "deleted_at": "2024-01-01"},
        {"id": 3, "trashed": True},
    ]
    f = TrashedFilter.make()
    assert f.get_options()[""] == "Without trashed"
    assert f.apply(rows, None) == [rows[0]]
    assert len(f.apply(rows, TrashedFilter.WITH_TRASHED)) == 3
    assert len(f.apply(rows, TrashedFilter.ONLY_TRASHED)) == 2

    obj = type("R", (), {"deleted_at": None, "trashed": False})()
    obj2 = type("R", (), {"deleted_at": "x", "trashed": False})()
    assert TrashedFilter.make().apply([obj, obj2], None) == [obj]


def test_action_slide_over_and_modal_width() -> None:
    from almasix.orbit.actions.action import Action

    action = (
        Action.make("edit")
        .label("Edit")
        .slide_over()
        .modal_width("2xl")
        .requires_confirmation()
    )
    assert action.is_slide_over() is True
    assert action.is_modal() is True
    assert action.get_modal_width() == "2xl"
    html = action.render()
    assert 'data-slide-over="true"' in html
    assert 'data-modal-width="2xl"' in html
    assert action.to_dict()["slide_over"] is True

    dynamic = Action.make("w").modal_width(lambda **_: "4xl")
    assert dynamic.get_modal_width() == "4xl"


def test_import_export_column_map_and_limits() -> None:
    imp = (
        ImportAction.make()
        .column_map({"title": "Title", "body": "Body"})
        .chunk_size(250)
        .max_rows(1000)
    )
    d = imp.to_dict()
    assert d["column_map"] == {"title": "Title", "body": "Body"}
    assert d["chunk_size"] == 250
    assert d["max_rows"] == 1000
    assert imp.get_column_map()["title"] == "Title"

    exp = (
        ExportAction.make()
        .column_map({"name": "Name"})
        .chunk_size(100)
        .max_rows(500)
    )
    assert exp.get_chunk_size() == 100
    assert exp.get_max_rows() == 500


def test_group_aliases() -> None:
    records = [{"status": "a"}, {"status": "b"}, {"status": "a"}]
    group = Group.make("status")
    buckets = group.group_records(records)
    assert len(buckets) == 2
    assert group.get_key_from_record(records[0]) == "a"


# --- Panels / auth / notifications ---------------------------------------------


def test_discover_classes_and_panel_load_discovered(tmp_path) -> None:
    import textwrap

    from almasix.orbit.panels.discover import discover_classes
    from almasix.orbit.panels.panel import Panel
    from almasix.orbit.panels.resource import Resource

    mod_path = tmp_path / "discovered_resource.py"
    mod_path.write_text(
        textwrap.dedent(
            """
            from almasix.orbit.panels.resource import Resource

            class AutoPostResource(Resource):
                navigation_label = "Auto Posts"
            """
        )
    )
    found = discover_classes(str(mod_path), base_class=Resource)
    assert len(found) == 1
    assert found[0].__name__ == "AutoPostResource"

    panel = Panel.make("admin").discover_resources(str(tmp_path)).load_discovered()
    names = [r.__name__ for r in panel.get_resources()]
    assert "AutoPostResource" in names


def test_password_reset_render() -> None:
    from almasix.orbit.panels.auth import PasswordReset

    html = PasswordReset.render()
    assert "or-page-password-reset" in html
    assert "Email reset link" in html
    assert 'wire:submit="requestReset"' in html


def test_live_notifier() -> None:
    from almasix.orbit.notifications import LiveNotifier
    from almasix.orbit.notifications.notification import Notification

    live = LiveNotifier().channel("orders").channel("users")
    assert live.get_channels() == ["orders", "users"]
    live.send(Notification.make("Order shipped").success())
    html = live.render_live()
    assert "or-live-notifier" in html
    assert 'data-channels="orders,users"' in html
    assert "Order shipped" in html


def test_column_and_filter_edge_branches() -> None:
    from almasix.orbit.tables.columns import TextColumn
    from almasix.orbit.tables.filters import TrashedFilter
    from almasix.orbit.tables.summaries import Sum

    col = TextColumn.make("x").summarize(Sum.make().label("S"))
    assert len(col.get_summarizers()) == 1
    assert TextColumn.make("x").get_description() is None
    assert TextColumn.make("x").description(lambda **_: None).get_description() is None
    assert TextColumn.make("x").description(lambda **_: "tip").get_description() == "tip"
    bad_money = TextColumn.make("x").money("EUR").render_cell({"x": "nope"})
    assert "nope" in bad_money
    bad_date = TextColumn.make("x").date("%Y").render_cell({"x": "not-a-date"})
    assert "not-a-date" in bad_date
    assert "2024" in TextColumn.make("x").date("%Y").render_cell({"x": date(2024, 1, 1)})

    custom = TrashedFilter.make().query(lambda q, v: [r for r in q if v])
    assert custom.apply([1, 2], "x") == [1, 2]
    trashed_obj = type("R", (), {"deleted_at": None, "trashed": True})()
    assert TrashedFilter.make().apply([trashed_obj], TrashedFilter.ONLY_TRASHED) == [trashed_obj]


def test_import_export_getters() -> None:
    imp = ImportAction.make()
    assert imp.get_chunk_size() == 500
    assert imp.get_max_rows() is None
    assert imp.get_column_map() == {}
    exp = ExportAction.make()
    assert exp.get_column_map() == {}
    assert exp.get_chunk_size() == 500


def test_discover_and_panel_load_all_types(tmp_path, monkeypatch) -> None:
    import textwrap

    from almasix.orbit.panels.discover import discover_classes
    from almasix.orbit.panels.panel import Panel
    from almasix.orbit.panels.resource import Resource

    assert discover_classes("no.such.package.xyz", base_class=Resource) == []

    broken = tmp_path / "broken.py"
    broken.write_text("!!!")
    assert discover_classes(str(broken), base_class=Resource) == []

    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "res.py").write_text(
        textwrap.dedent(
            """
            from almasix.orbit.panels.resource import Resource
            class DirResource(Resource):
                pass
            """
        )
    )
    (pkg / "_skip.py").write_text("class Skip(Resource): pass")
    found_dir = discover_classes(str(pkg), base_class=Resource)
    assert any(c.__name__ == "DirResource" for c in found_dir)

    pages_pkg = tmp_path / "pagespkg"
    pages_pkg.mkdir()
    (pages_pkg / "__init__.py").write_text("")
    (pages_pkg / "dash.py").write_text(
        textwrap.dedent(
            """
            from almasix.orbit.panels.page import Page
            class DiscoveredPage(Page):
                title = "Disc"
            """
        )
    )
    widgets_pkg = tmp_path / "widgetspkg"
    widgets_pkg.mkdir()
    (widgets_pkg / "__init__.py").write_text("")
    (widgets_pkg / "stat.py").write_text(
        textwrap.dedent(
            """
            from almasix.orbit.widgets.widget import Widget
            class DiscoveredWidget(Widget):
                pass
            """
        )
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    import importlib

    importlib.import_module("pagespkg")
    importlib.import_module("widgetspkg")

    panel = (
        Panel.make("admin")
        .discover_resources(str(pkg / "res.py"))
        .discover_pages("pagespkg")
        .discover_widgets("widgetspkg")
        .load_discovered()
    )
    assert "DirResource" in [r.__name__ for r in panel.get_resources()]
    assert "DiscoveredPage" in [p.__name__ for p in panel.get_pages()]
    assert "DiscoveredWidget" in [w.__name__ for w in panel.get_widgets()]


def test_panels_platform_depth() -> None:

    from almasix.orbit.panels.auth import AppAuthentication
    from almasix.orbit.panels.cluster import Cluster
    from almasix.orbit.panels.hooks import clear_render_hooks, register_render_hook, render_hook
    from almasix.orbit.panels.pages.resource_pages import Tab
    from almasix.orbit.panels.resource import Resource
    from almasix.orbit.panels.tenancy import Tenancy, Tenant

    class CustomCluster(Cluster):
        slug = "custom"
        navigation_label = "Custom"

    c = CustomCluster.make().pages([]).resources([Resource])
    assert c.get_slug() == "custom"
    assert c.get_navigation_label() == "Custom"
    assert c.get_pages() == []
    assert c.get_resources() == [Resource]

    tenant = Tenant(1, "Acme", slug="acme")
    assert tenant.to_dict()["slug"] == "acme"
    tenancy = (
        Tenancy()
        .model(Tenant)
        .ownership_relationship("org")
        .slug_attribute("slug")
        .name_attribute("name")
        .billing()
        .menu_items([{"label": "Bill"}])
        .current(None)
    )
    assert tenancy.scope_query([1, 2]) == [1, 2]
    assert tenancy.render_switcher() == ""

    tab = Tab("all").icon("heroicon-o-home").badge(3).badge_color("success")
    assert "or-list-tab" in tab.render(active=True)
    assert tab.apply_query([1, 2, 3]) == [1, 2, 3]

    mfa = AppAuthentication()
    user = type("U", (), {"mfa_app_enabled": True})()
    assert mfa.is_enabled(user) is True
    assert "code" in mfa.get_management_schema().render()

    clear_render_hooks()
    register_render_hook("panels::body.end", lambda **_: "<!--scoped-->", scopes=["posts"])
    assert render_hook("panels::body.end", scope="posts") == "<!--scoped-->"
    assert render_hook("panels::body.end", scope="other") == ""


# --- Table.render wiring (summaries / grouping / layout / filters) -------------


def test_table_render_summaries_grouping_layout_filters() -> None:
    from almasix.orbit.actions import ActionGroup, EditAction
    from almasix.orbit.query_builder import QueryBuilder, TextConstraint
    from almasix.orbit.tables import (
        Group,
        QueryBuilderFilter,
        Split,
        Stack,
        Sum,
        Table,
        TextColumn,
        TrashedFilter,
    )

    records = [
        {"name": "A", "status": "open", "amount": 10, "deleted_at": None},
        {"name": "B", "status": "open", "amount": 20, "deleted_at": None},
        {"name": "C", "status": "done", "amount": 30, "deleted_at": "x"},
    ]
    table = (
        Table.make("orders")
        .columns(
            [
                Split.make(
                    [
                        Stack.make([TextColumn.make("name").label("Name")]),
                        TextColumn.make("status").label("Status"),
                    ]
                ).label("Info"),
                TextColumn.make("amount").label("Amt").summarize(Sum.make().label("Total")),
            ]
        )
        .filters([TrashedFilter.make()])
        .filter_state({"trashed": TrashedFilter.WITH_TRASHED})
        .persist_filters_in_session(key="orders-filters")
        .defer_filters()
        .default_group(Group.make("status").collapsible())
        .collapsed_groups_by_default()
        .groups([Group.make("status"), Group.make("name")])
        .content_grid(3)
        .header_actions([EditAction.make().label("New")])
        .actions([ActionGroup.make([EditAction.make()]).label("More")])
        .records(records)
        .paginate(1, 10)
    )
    html = table.render()
    assert "or-table-filters" in html
    assert 'data-filters-session="orders-filters"' in html
    assert 'data-defer-filters="true"' in html
    assert "or-group-header" in html
    assert "or-tfoot" in html and "or-summary" in html
    assert "or-split" in html and "or-stack" in html
    assert 'data-content-grid="3"' in html
    assert "or-action-group" in html or "or-dropdown" in html
    assert "or-table-groups-chooser" in html
    assert table.to_dict()["defer_filters"] is True

    qb = QueryBuilder.make().constraints([TextConstraint.make("name").label("Name")])
    qb_table = (
        Table.make()
        .columns([TextColumn.make("name")])
        .query_builder(qb.rules([{"constraint": "name", "operator": "equals", "value": "A"}]))
        .records(records)
    )
    assert qb_table.get_records() == [records[0]]
    assert "or-query-builder" in qb_table.render()

    qf = QueryBuilderFilter.make().builder(QueryBuilder.make().constraints([TextConstraint.make("name")]))
    assert "or-query-builder" in qf.render()
    applied = qf.apply(
        records,
        [{"constraint": "name", "operator": "equals", "value": "B"}],
    )
    assert applied == [records[1]]

    only = (
        Table.make()
        .columns([TextColumn.make("name"), TextColumn.make("status")])
        .default_group("status")
        .groups_only()
        .records(records[:2])
    )
    only_html = only.render()
    assert "or-group-header" in only_html
    assert ">A<" not in only_html

    money = TextColumn.make("n").numeric(2).visible_from("md").hidden_from("xl")
    cell = money.render_cell({"n": 3.1})
    assert "3.10" in cell and "or-visible-from-md" in cell and "or-hidden-from-xl" in cell
    assert "• a" in TextColumn.make("t").list_with_line_breaks().render_cell({"t": ["a", "b"]})


def test_table_wiring_coverage_branches() -> None:
    from almasix.orbit.actions import EditAction
    from almasix.orbit.schemas.primes import Text
    from almasix.orbit.tables import (
        ColumnGroup,
        Group,
        Panel,
        QueryBuilderFilter,
        Split,
        Sum,
        Table,
        TextColumn,
        TrashedFilter,
    )
    from almasix.orbit.tables.filters import FilterGroup

    # persist without key; clear group; content_grid variants
    t = Table.make("t").persist_filters_in_session().default_group(None)
    assert t._filters_session_key is None
    assert t._default_group is None
    t.content_grid(None)
    assert t._content_grid is None
    t.content_grid({"columns": 4, "md": 2})
    assert t._content_grid["columns"] == 4

    # ColumnGroup + layout non-column child + header label fallback
    split = Split.make([Text.make("prime"), TextColumn.make("n").label("N")]).label(None)
    # force empty label on split
    split._label = None
    table = (
        Table.make()
        .columns(
            [
                ColumnGroup.make("grp").columns(
                    [TextColumn.make("a").label("A"), TextColumn.make("b").label("B")]
                ),
                split,
                TextColumn.make("amount").summarize(Sum.make().label("T")),
            ]
        )
        .actions([EditAction.make()])
        .bulk_actions([EditAction.make().label("Bulk")])
        .groups([Group.make("a")])  # no default_group → uses first of groups
        .records([{"a": 1, "b": 2, "n": 3, "amount": 5, "prime": "x"}])
        .filters([TrashedFilter.make()])
        .filter_state({"trashed": "bogus"})  # unknown value → passthrough line 70
        .paginate(1, 1)
    )
    # more records than page for all vs page footer
    table.records(
        [
            {"a": 1, "b": 2, "n": 3, "amount": 5},
            {"a": 1, "b": 9, "n": 4, "amount": 7},
        ]
    )
    html = table.render()
    assert "or-th-group" in html
    assert "or-tfoot" in html
    assert 'data-summary-scope="page"' in html or 'data-summary-scope="all"' in html
    assert "or-table-bulk-actions" in html
    assert "or-group-header" in html
    assert table.flat_columns()  # includes ColumnGroup children

    # filter selected option rebuild
    sel = (
        Table.make()
        .columns([TextColumn.make("name")])
        .filters([TrashedFilter.make()])
        .filter_state({"trashed": TrashedFilter.ONLY_TRASHED})
        .records([{"name": "x", "deleted_at": "y"}])
    )
    assert "selected" in sel.render()

    # QueryBuilderFilter edge paths
    qf = QueryBuilderFilter.make()
    assert qf.get_builder() is None
    assert qf.apply([1], None) == [1]
    assert qf.render() == ""
    qf.builder(type("B", (), {"rules": lambda self, r: None})())
    assert qf.apply([1, 2], "not-list") == [1, 2]  # no apply → return query at end... wait builder has no apply
    # builder without apply hits return query
    assert qf.apply([1], [{"constraint": "x"}]) == [1]
    custom = QueryBuilderFilter.make().query(lambda q, v: [v]).builder(None)
    assert custom.apply([1], "z") == ["z"]

    fg = FilterGroup.make("g").filters([TrashedFilter.make()])
    assert fg._filters

    # column formatters
    assert TextColumn.make("x").date_time().render_cell({"x": "2024-01-02T10:00:00"})
    assert "5" in TextColumn.make("x").numeric().render_cell({"x": 5})
    assert "1.5" in TextColumn.make("x").numeric().render_cell({"x": 1.5})
    assert "bad" in TextColumn.make("x").numeric().render_cell({"x": "bad"})
    assert TextColumn.make("x")._format_display_value(None) == ""
    html_cell = TextColumn.make("x").html().render_cell({"x": "<b>hi</b>"})
    assert "<b>hi</b>" in html_cell
    md = TextColumn.make("x").markdown().render_cell({"x": "a\nb"})
    assert "<br" in md
    panel = Panel.make([TextColumn.make("z").label("Z")])
    assert "or-panel" in Table.make().columns([panel]).records([{"z": 1}]).render()
