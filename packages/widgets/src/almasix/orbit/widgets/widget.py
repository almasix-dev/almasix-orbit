
"""Dashboard widgets."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e
from almasix.orbit.tables.table import Table


@dataclass
class Stat:
    label: str
    value: Any
    description: str | None = None
    color: str = "primary"
    icon: str | None = None


@dataclass
class WidgetConfiguration:
    columns: int = 2
    polling: int | None = None


class Widget(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._heading: str | None = None
        self._description: str | None = None
        self._column_span_full = False

    def heading(self, text: str) -> Self:
        self._heading = text
        return self

    def description(self, text: str) -> Self:
        self._description = text
        return self

    def column_span_full(self, condition: bool = True) -> Self:
        self._column_span_full = condition
        return self

    def get_data(self) -> Any:
        return None

    def render(self, state: Any = None, **ctx: Any) -> str:
        title = e(self._heading or self.get_label())
        desc = f'<p class="or-widget-desc">{e(self._description)}</p>' if self._description else ""
        body = self.render_body(state, **ctx)
        span = " or-col-span-full" if self._column_span_full else ""
        return (
            f'<section class="or-widget{span}" data-widget="{e(self.get_name() or "")}">'
            f'<header class="or-widget-header"><h3>{title}</h3>{desc}</header>'
            f'<div class="or-widget-body">{body}</div></section>'
        )

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        return ""


class StatsOverviewWidget(Widget):
    def __init__(self, name: str | None = "stats") -> None:
        super().__init__(name)
        self._stats: list[Stat] = []

    def stats(self, stats: Sequence[Stat]) -> Self:
        self._stats = list(stats)
        return self

    def get_stats(self) -> list[Stat]:
        return list(self._stats)

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        cards = []
        for s in self._stats:
            desc = f'<p class="or-stat-desc">{e(s.description)}</p>' if s.description else ""
            cards.append(
                f'<div class="or-stat or-color-{e(s.color)}">'
                f'<p class="or-stat-label">{e(s.label)}</p>'
                f'<p class="or-stat-value">{e(s.value)}</p>{desc}</div>'
            )
        return f'<div class="or-stats">{"".join(cards)}</div>'


class ChartWidget(Widget):
    def __init__(self, name: str | None = "chart") -> None:
        super().__init__(name)
        self._chart_type = "line"
        self._datasets: list[dict[str, Any]] = []
        self._labels: list[str] = []

    def chart_type(self, kind: str) -> Self:
        self._chart_type = kind
        return self

    def labels(self, labels: Sequence[str]) -> Self:
        self._labels = list(labels)
        return self

    def datasets(self, datasets: Sequence[dict[str, Any]]) -> Self:
        self._datasets = list(datasets)
        return self

    def get_data(self) -> dict[str, Any]:
        return {"type": self._chart_type, "labels": self._labels, "datasets": self._datasets}

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        import json

        payload = e(json.dumps(self.get_data()))
        return f'<div class="or-chart" data-chart="{payload}" role="img" aria-label="chart"></div>'


class TableWidget(Widget):
    def __init__(self, name: str | None = "table_widget") -> None:
        super().__init__(name)
        self._table: Table | None = None

    def table(self, table: Table) -> Self:
        self._table = table
        return self

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        if self._table is None:
            return ""
        return self._table.render(state, **ctx)
