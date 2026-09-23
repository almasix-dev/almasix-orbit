"""Fluent Stat card for StatsOverviewWidget."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon


class Stat(Component):
    """Fluent statistic card with optional full-bleed sparkline chart."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._label: str | None = name
        self._value: Any = None
        self._description: str | None = None
        self._description_icon: str | None = None
        self._color: str = "primary"
        self._chart_color: str | None = None
        self._icon: str | None = None
        self._chart: list[float | int] = []
        self._url: str | None = None
        self._placeholder: str | None = None

    @classmethod
    def make(cls, label: str | None = None, value: Any = None) -> Self:  # type: ignore[override]
        inst = cls(label)
        if value is not None:
            inst._value = value
        return inst

    def label(self, text: str) -> Self:  # type: ignore[override]
        self._label = text
        self._name = text
        return self

    def value(self, value: Any) -> Self:
        self._value = value
        return self

    def description(self, text: str) -> Self:  # type: ignore[override]
        self._description = text
        return self

    def description_icon(self, icon_name: str) -> Self:
        self._description_icon = icon_name
        return self

    def color(self, color: str) -> Self:
        self._color = color
        return self

    def chart_color(self, color: str) -> Self:
        """Override sparkline stroke/fill color (defaults to the card ``.color``)."""
        self._chart_color = color
        return self

    def icon(self, icon_name: str) -> Self:
        self._icon = icon_name
        return self

    def chart(self, points: Sequence[float | int]) -> Self:
        self._chart = [float(p) for p in points]
        return self

    def url(self, url: str) -> Self:
        self._url = url
        return self

    def placeholder(self, text: str) -> Self:
        self._placeholder = text
        return self

    def extra_attributes(self, attrs: Mapping[str, Any]) -> Self:  # type: ignore[override]
        self._extra_attributes.update(dict(attrs))
        return self

    def get_label(self, **ctx: Any) -> str:  # type: ignore[override]
        if self._label is not None:
            return str(self._label)
        return super().get_label(**ctx)

    def render(self, state: Any = None, **ctx: Any) -> str:
        label = e(self.get_label(**ctx))
        value = self._value if self._value is not None else self._placeholder
        value_html = e("" if value is None else value)
        color = e(self._color)
        icon_html = ""
        if self._icon:
            icon_html = (
                f'<div class="or-stat-icon">{render_icon(self._icon, size=22, css_class="or-icon")}</div>'
            )
        desc = ""
        if self._description:
            di = ""
            if self._description_icon:
                di = render_icon(
                    self._description_icon,
                    size=14,
                    css_class="or-icon or-stat-desc-icon",
                )
            desc = f'<p class="or-stat-desc">{di}{e(self._description)}</p>'
        spark = ""
        has_chart = bool(self._chart)
        if has_chart:
            chart_token = self._chart_color or self._color
            payload = e(json.dumps({"values": self._chart, "color": chart_token}))
            spark = (
                f'<div class="or-stat-chart or-color-{e(chart_token)}" data-sparkline="{payload}" '
                f'x-data="orbitSparkline" role="img" aria-label="trend">'
                # Themeable color carriers for stroke / fill.
                f'<span class="or-stat-chart-border" aria-hidden="true"></span>'
                f'<span class="or-stat-chart-bg" aria-hidden="true"></span>'
                f"</div>"
            )
        attrs = self.get_extra_attributes(**ctx)
        extra = "".join(f' {e(k)}="{e(v)}"' for k, v in attrs.items())
        body = (
            f'<div class="or-stat-body">'
            f"{icon_html}"
            f'<div class="or-stat-copy">'
            f'<p class="or-stat-label">{label}</p>'
            f'<p class="or-stat-value">{value_html}</p>{desc}'
            f"</div></div>"
        )
        chart_cls = " or-stat-has-chart" if has_chart else ""
        tag = "a" if self._url else "div"
        href = f' href="{e(self._url)}"' if self._url else ""
        return (
            f'<{tag} class="or-stat{chart_cls} or-color-{color}"{href}{extra}>'
            f"{body}{spark}</{tag}>"
        )
