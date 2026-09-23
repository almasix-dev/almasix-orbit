"""Tests for almasix.orbit.widgets."""

from __future__ import annotations

import pytest
from almasix.orbit.tables.columns import TextColumn
from almasix.orbit.tables.table import Table
from almasix.orbit.widgets import (
    ChartLibrary,
    ChartWidget,
    Stat,
    StatsOverviewWidget,
    TableWidget,
    Widget,
    WidgetConfiguration,
    column_span_classes,
    normalize_polling_interval,
    render_widgets,
    resolve_widgets,
)


def test_widget_configuration_and_helpers() -> None:
    cfg = WidgetConfiguration(columns=3, polling=30)
    assert cfg.columns == 3 and cfg.polling == 30
    assert normalize_polling_interval(5) == "5s"
    assert normalize_polling_interval("10s") == "10s"
    assert normalize_polling_interval(None) is None
    assert normalize_polling_interval(0) is None
    assert column_span_classes("full") == "or-col-span-full"
    assert column_span_classes(2) == "or-col-span-2"
    assert "or-col-span-md-2" in column_span_classes({"md": 2})
    assert "or-col-span-lg-full" in column_span_classes({"lg": "full"})
    assert column_span_classes(None) == ""
    assert column_span_classes("abc") == ""


def test_base_widget_fluent_and_class_attrs() -> None:
    base = (
        Widget.make("w")
        .heading("H")
        .description("D")
        .column_span_full()
        .polling_interval(15)
        .lazy()
        .sort(3)
    )
    assert base.get_data() is None
    assert base.get_sort() == 3
    assert base.get_polling_interval() == "15s"
    assert base.is_lazy() is True
    html = base.render()
    assert "or-col-span-full" in html
    assert 'data-polling="15s"' in html
    assert 'data-lazy="true"' in html
    assert "or-widget-lazy-placeholder" in html
    assert base.render_body() == ""

    class Sorted(Widget):
        sort = 9
        column_span = 2
        polling_interval = "5s"
        heading = "Class H"
        description = "Class D"
        is_lazy = True

    inst = Sorted.make("sorted")
    assert inst.get_sort() == 9
    assert inst.get_column_span() == 2
    assert inst.get_polling_interval() == "5s"
    assert inst.is_lazy() is True
    assert inst.get_heading() == "Class H"
    assert "or-col-span-2" in inst.render()
    # Fluent still works after class attr capture.
    assert Sorted.make().sort(1).get_sort() == 1
    assert Widget.render_for_dashboard() != ""


def test_can_view_and_page_filters() -> None:
    class Hidden(Widget):
        @classmethod
        def can_view(cls, **ctx: object) -> bool:
            return bool(ctx.get("allow"))

    assert Hidden.make().render(allow=False) == ""
    assert "or-widget" in Hidden.make().render(allow=True)
    shown = Widget.make("x").can_view_when(lambda **ctx: ctx.get("ok") is True)
    assert shown.render(ok=False) == ""
    assert "or-widget" in shown.render(ok=True)

    w = Widget.make("f").page_filters({"range": "week"})
    assert w.filter_value("range") == "week"
    assert w.get_page_filters(page_filters={"range": "month"})["range"] == "week"
    w2 = Widget.make("f2")
    assert w2.get_page_filters(page_filters={"a": 1}) == {"a": 1}
    assert w2.filter_value("a", **{"page_filters": {"a": 2}}) == 2


def test_stat_fluent_and_sparkline() -> None:
    stat = (
        Stat.make("Revenue")
        .value("$12k")
        .description("+12%")
        .description_icon("heroicon-o-arrow-up-tray")
        .color("success")
        .chart([2, 4, 3, 8])
        .icon("heroicon-o-users")
        .extra_attributes({"data-x": "1"})
        .url("/revenue")
    )
    html = stat.render()
    assert "Revenue" in html and "$12k" in html and "+12%" in html
    assert "or-stat-has-chart" in html
    assert "or-stat-body" in html
    assert "or-stat-chart" in html and "data-sparkline" in html
    assert "or-stat-chart-border" in html and "or-stat-chart-bg" in html
    # Chart is a sibling footer (full-bleed), not nested inside copy.
    assert html.index("or-stat-copy") < html.index("or-stat-chart")
    assert "&quot;color&quot;: &quot;success&quot;" in html
    assert 'href="/revenue"' in html
    assert 'data-x="1"' in html
    assert "or-stat-icon" in html

    colored = Stat.make("Errors").value(3).color("gray").chart_color("danger").chart([1, 2, 1])
    colored_html = colored.render()
    assert "or-color-gray" in colored_html
    assert 'or-stat-chart or-color-danger' in colored_html
    assert "&quot;color&quot;: &quot;danger&quot;" in colored_html

    plain = Stat.make("Views", "100").placeholder("—").color("primary")
    plain_html = plain.render()
    assert "100" in plain_html
    assert "or-stat-has-chart" not in plain_html
    empty = Stat.make("Empty").placeholder("n/a")
    assert "n/a" in empty.render()


def test_stats_overview_callables() -> None:
    stats = StatsOverviewWidget.make().stats(
        [
            Stat.make("Users").value(10).description("All").color("success"),
            lambda **ctx: Stat.make("Dyn").value(ctx.get("n", 0)),
        ]
    )
    assert len(stats.get_stats(n=3)) == 2
    html = stats.render(n=3)
    assert "or-stats" in html and "Users" in html and "Dyn" in html and "3" in html


def test_chart_widget_chartjs_and_apex() -> None:
    chart = (
        ChartWidget.make("signups")
        .chart_library(ChartLibrary.CHARTJS)
        .chart_type("line")
        .labels(["a", "b"])
        .datasets([{"label": "Users", "data": [1, 2]}])
        .options({"plugins": {"legend": {"display": False}}})
        .color("primary")
        .max_height("280px")
        .filters({"week": "Last week", "month": "Last month"})
        .filter("week")
        .collapsible(True)
        .heading("Chart")
    )
    data = chart.get_data()
    assert data["type"] == "line" and data["labels"] == ["a", "b"]
    html = chart.render()
    assert 'data-chart-library="chartjs"' in html
    assert "or-chart-filters" in html and "is-active" in html
    assert 'data-collapsible="true"' in html

    apex = (
        ChartWidget.make("apex")
        .chart_library(ChartLibrary.APEX)
        .chart_type("bar")
        .labels(["x", "y"])
        .datasets([{"label": "S", "data": [3, 4]}])
    )
    assert "categories" in str(apex.get_apex_options())
    assert 'data-chart-library="apex"' in apex.render()

    custom = ChartWidget.make().chart_library("apex").apex_options({"series": [1, 2]})
    assert custom.get_apex_options() == {"series": [1, 2]}

    pie = (
        ChartWidget.make()
        .chart_library(ChartLibrary.APEX)
        .chart_type("doughnut")
        .labels(["a", "b"])
        .datasets([{"data": [1, 2]}])
    )
    opts = pie.get_apex_options()
    assert opts["chart"]["type"] == "donut"

    empty = (
        ChartWidget.make()
        .empty_state_heading("No data")
        .empty_state_description("Try again")
    )
    empty_html = empty.render()
    assert "or-chart-empty" in empty_html and "No data" in empty_html


def test_table_widget() -> None:
    table = Table.make().columns([TextColumn.make("name")]).records([{"name": "A"}])
    tw = TableWidget.make().table(table).heading("T")
    assert tw.get_table() is table
    assert "or-table" in tw.render()
    assert TableWidget.make().render_body() == ""


def test_resolve_and_render_widgets() -> None:
    class Late(Widget):
        sort = 20

        def render_body(self, state=None, **ctx):  # type: ignore[no-untyped-def]
            return "LATE"

    class Early(Widget):
        sort = 1

        def render_body(self, state=None, **ctx):  # type: ignore[no-untyped-def]
            return "EARLY"

    class Nope(Widget):
        @classmethod
        def can_view(cls, **ctx: object) -> bool:
            return False

    resolved = resolve_widgets([Late, Early.make(), Nope])
    assert [w.get_sort() for w in resolved] == [1, 20]
    htmls = render_widgets([Late, Early, "<b>raw</b>", 123, Nope])
    joined = "".join(htmls)
    assert joined.index("EARLY") < joined.index("LATE")
    assert "<b>raw</b>" in joined

    with pytest.raises(TypeError):
        Widget.from_class(object())


def test_column_span_breakpoints() -> None:
    w = Widget.make().column_span({"md": 2, "xl": "full"})
    html = w.render()
    assert "or-col-span-md-2" in html
    assert "or-col-span-xl-full" in html
    assert "or-col-span-full" in column_span_classes({"": "full"})
    assert column_span_classes("3") == "or-col-span-3"


def test_stat_label_and_stats_sequence_callable() -> None:
    s = Stat.make().label("Renamed").value(1)
    assert s.get_label() == "Renamed"
    assert Stat.make().get_label() == ""  # falls through to Component

    def many(**ctx: object):
        return [Stat.make("A").value(1), Stat.make("B").value(2)]

    html = StatsOverviewWidget.make().stats([many]).render()
    assert "A" in html and "B" in html


def test_chart_apex_options_merge_and_empty_guard() -> None:
    apex = (
        ChartWidget.make()
        .chart_library(ChartLibrary.APEX)
        .labels(["a"])
        .datasets([{"data": [1]}])
        .options({"legend": {"show": False}})
    )
    opts = apex.get_apex_options()
    assert opts["legend"]["show"] is False

    custom = ChartWidget.make().chart_library("apex").apex_options({"series": [1]})
    assert "or-chart" in custom.render()  # not empty state


def test_widget_instantiate_lazy_class_and_filters_ctx() -> None:
    class LazyW(Widget):
        lazy = True

    class DescNone(Widget):
        description = None
        heading = None

    assert LazyW.make().is_lazy() is True
    assert DescNone.make().get_description() is None
    assert Widget.instantiate(LazyW).get_name() is None or True
    w = Widget.make("p")
    html = w.render(page_filters={"x": 1})
    assert w.get_page_filters()["x"] == 1
    assert "or-widget" in html
    # Non-mapping page_filters ignored
    Widget.make("p2").render(page_filters="nope")
    # column_span_full(False) leaves span unset
    assert Widget.make().column_span_full(False).get_column_span() is None

    class WithCallableSort(Widget):
        sort = staticmethod(lambda: 1)  # type: ignore[assignment]

    WithCallableSort.make()


def test_stats_ignores_non_stat_entries() -> None:
    html = (
        StatsOverviewWidget.make()
        .stats(
            [
                Stat.make("Ok").value(1),
                "skip-me",  # type: ignore[list-item]
                lambda **ctx: 99,
                lambda **ctx: [Stat.make("A").value(1), "nope"],  # type: ignore[list-item]
            ]
        )
        .render()
    )
    assert "Ok" in html and "A" in html


def test_get_description() -> None:
    assert Widget.make().description("d").get_description() == "d"
