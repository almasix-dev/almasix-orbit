"""Tests for almasix.orbit.widgets."""

from __future__ import annotations

from almasix.orbit.tables.columns import TextColumn
from almasix.orbit.tables.table import Table
from almasix.orbit.widgets.widget import (
    ChartWidget,
    Stat,
    StatsOverviewWidget,
    TableWidget,
    Widget,
    WidgetConfiguration,
)


def test_stats_chart_table_widgets() -> None:
    cfg = WidgetConfiguration(columns=3, polling=30)
    assert cfg.columns == 3

    base = Widget.make("w").heading("H").description("D").column_span_full()
    assert base.get_data() is None
    assert "or-col-span-full" in base.render()
    assert base.render_body() == ""

    stats = StatsOverviewWidget.make().stats(
        [Stat(label="Users", value=10, description="All", color="success", icon="heroicon-o-users")]
    )
    assert len(stats.get_stats()) == 1
    html = stats.render()
    assert "or-stats" in html and "Users" in html and "10" in html

    chart = (
        ChartWidget.make()
        .chart_type("bar")
        .labels(["a", "b"])
        .datasets([{"data": [1, 2]}])
        .heading("Chart")
    )
    data = chart.get_data()
    assert data["type"] == "bar" and data["labels"] == ["a", "b"]
    assert "or-chart" in chart.render()

    table = Table.make().columns([TextColumn.make("name")]).records([{"name": "A"}])
    tw = TableWidget.make().table(table).heading("T")
    assert "or-table" in tw.render()
    assert TableWidget.make().render_body() == ""
