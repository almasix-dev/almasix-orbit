"""Chart widget with Chart.js or ApexCharts."""

from __future__ import annotations

import json
from enum import StrEnum
from typing import Any, Self

from almasix.orbit.support.html import e
from almasix.orbit.widgets.widget import Widget


class ChartLibrary(StrEnum):
    CHARTJS = "chartjs"
    APEX = "apex"


class ChartWidget(Widget):
    """Dashboard chart supporting Chart.js (default) or ApexCharts."""

    def __init__(self, name: str | None = "chart") -> None:
        super().__init__(name)
        self._chart_type = "line"
        self._datasets: list[dict[str, Any]] = []
        self._labels: list[str] = []
        self._options: dict[str, Any] = {}
        self._apex_options: dict[str, Any] | None = None
        self._library: ChartLibrary = ChartLibrary.CHARTJS
        self._color: str = "primary"
        self._max_height: str | None = "300px"
        self._filters: dict[str, str] = {}
        self._filter: str | None = None
        self._empty_state_heading: str | None = None
        self._empty_state_description: str | None = None
        self._collapsible: bool = False

    def chart_library(self, library: ChartLibrary | str) -> Self:
        self._library = ChartLibrary(library)
        return self

    def chart_type(self, kind: str) -> Self:
        self._chart_type = kind
        return self

    def labels(self, labels: list[str] | tuple[str, ...]) -> Self:
        self._labels = list(labels)
        return self

    def datasets(self, datasets: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> Self:
        self._datasets = list(datasets)
        return self

    def options(self, options: dict[str, Any]) -> Self:
        self._options = dict(options)
        return self

    def apex_options(self, options: dict[str, Any]) -> Self:
        self._apex_options = dict(options)
        return self

    def color(self, color: str) -> Self:
        self._color = color
        return self

    def max_height(self, height: str) -> Self:
        self._max_height = height
        return self

    def filters(self, filters: dict[str, str]) -> Self:
        self._filters = dict(filters)
        return self

    def filter(self, key: str) -> Self:
        self._filter = key
        return self

    def empty_state_heading(self, text: str) -> Self:
        self._empty_state_heading = text
        return self

    def empty_state_description(self, text: str) -> Self:
        self._empty_state_description = text
        return self

    def collapsible(self, condition: bool = True) -> Self:
        self._collapsible = bool(condition)
        return self

    def get_data(self) -> dict[str, Any]:
        """Return Chart.js-shaped payload (type / labels / datasets / options)."""
        return {
            "type": self._chart_type,
            "labels": list(self._labels),
            "datasets": list(self._datasets),
            "options": dict(self._options),
        }

    def get_apex_options(self) -> dict[str, Any]:
        if self._apex_options is not None:
            return dict(self._apex_options)
        data = self.get_data()
        series: list[dict[str, Any]] = []
        for ds in data["datasets"]:
            series.append(
                {
                    "name": ds.get("label") or "",
                    "data": list(ds.get("data") or []),
                }
            )
        chart_type = data["type"]
        if chart_type == "doughnut":
            chart_type = "donut"
        options: dict[str, Any] = {
            "chart": {"type": chart_type, "toolbar": {"show": False}},
            "series": series if chart_type not in {"pie", "donut"} else (series[0]["data"] if series else []),
            "labels": data["labels"] if chart_type in {"pie", "donut"} else None,
            "xaxis": {"categories": data["labels"]} if chart_type not in {"pie", "donut"} else None,
        }
        # Drop null keys for cleaner JSON.
        options = {k: v for k, v in options.items() if v is not None}
        if self._options:
            # Shallow-merge Chart.js-style options into Apex when translating.
            options = {**options, **self._options}
        return options

    def _is_empty(self) -> bool:
        if self._library == ChartLibrary.APEX and self._apex_options:
            return False
        return not self._labels and not self._datasets

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        if self._is_empty() and (
            self._empty_state_heading or self._empty_state_description
        ):
            heading = e(self._empty_state_heading or "No data")
            desc = (
                f'<p class="or-chart-empty-desc">{e(self._empty_state_description)}</p>'
                if self._empty_state_description
                else ""
            )
            return (
                f'<div class="or-chart-empty">'
                f'<p class="or-chart-empty-heading">{heading}</p>{desc}</div>'
            )

        filters_html = ""
        if self._filters:
            active = self._filter or next(iter(self._filters), None)
            tabs = []
            for key, label in self._filters.items():
                sel = " is-active" if key == active else ""
                tabs.append(
                    f'<button type="button" class="or-chart-filter{sel}" '
                    f'data-filter="{e(key)}">{e(label)}</button>'
                )
            filters_html = f'<div class="or-chart-filters">{"".join(tabs)}</div>'

        if self._library == ChartLibrary.APEX:
            payload = self.get_apex_options()
            library = ChartLibrary.APEX.value
        else:
            payload = self.get_data()
            library = ChartLibrary.CHARTJS.value

        height = e(self._max_height) if self._max_height else ""
        style = f' style="max-height:{height}"' if height else ""
        color = e(self._color)
        collapse_attr = ' data-collapsible="true"' if self._collapsible else ""
        encoded = e(json.dumps(payload))
        chart = (
            f'<div class="or-chart or-color-{color}" data-chart-library="{library}" '
            f'data-chart="{encoded}" x-data="orbitChart" role="img" '
            f'aria-label="chart"{style}{collapse_attr}></div>'
        )
        return f"{filters_html}{chart}"
