"""Base dashboard widget (Filament Widget analogue)."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e

ColumnSpan = int | str | Mapping[str, int | str]

# Class attribute names that Filament sets on the class; fluent methods share these
# names, so __init_subclass__ moves int/str/dict/bool values onto _class_* slots.
_CLASS_CONFIG_KEYS = (
    "sort",
    "column_span",
    "polling_interval",
    "heading",
    "description",
    "is_lazy",
    "lazy",
)


@dataclass
class WidgetConfiguration:
    """Layout hints for dashboard grids (columns + optional polling seconds)."""

    columns: int = 2
    polling: int | None = None


def normalize_polling_interval(value: int | float | str | None) -> str | None:
    """Normalize seconds or strings like ``\"5s\"`` / ``\"10s\"`` for markup."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        n = int(value)
        return f"{n}s" if n > 0 else None
    text = str(value).strip()
    return text or None


def column_span_classes(span: ColumnSpan | None, *, full: bool = False) -> str:
    """Build ``or-col-span-*`` classes from int / ``full`` / breakpoint dict."""
    if full or span == "full":
        return "or-col-span-full"
    if span is None:
        return ""
    if isinstance(span, Mapping):
        classes: list[str] = []
        for bp, value in span.items():
            token = str(bp).strip().lower()
            if value == "full":
                classes.append(f"or-col-span-{token}-full" if token else "or-col-span-full")
            else:
                classes.append(f"or-col-span-{token}-{int(value)}")
        return " ".join(classes)
    if isinstance(span, str):
        return f"or-col-span-{span}" if span.isdigit() else ""
    return f"or-col-span-{int(span)}"


class Widget(Component):
    """Dashboard widget base with sort, span, polling, lazy, and can_view."""

    _class_sort: ClassVar[int] = 0
    _class_column_span: ClassVar[ColumnSpan | None] = None
    _class_polling_interval: ClassVar[int | str | None] = None
    _class_heading: ClassVar[str | None] = None
    _class_description: ClassVar[str | None] = None
    _class_is_lazy: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for key in _CLASS_CONFIG_KEYS:
            if key not in cls.__dict__:
                continue
            raw = cls.__dict__[key]
            if callable(raw):
                continue
            if key == "sort":
                cls._class_sort = int(raw)  # type: ignore[assignment]
            elif key == "column_span":
                cls._class_column_span = raw  # type: ignore[assignment]
            elif key == "polling_interval":
                cls._class_polling_interval = raw  # type: ignore[assignment]
            elif key == "heading":
                cls._class_heading = None if raw is None else str(raw)
            elif key == "description":
                cls._class_description = None if raw is None else str(raw)
            else:
                # is_lazy / lazy
                cls._class_is_lazy = bool(raw)
            setattr(cls, key, Widget.__dict__[key])

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._heading: str | None = type(self)._class_heading
        self._description: str | None = type(self)._class_description
        self._column_span_full = False
        self._sort: int | None = None
        self._column_span_value: ColumnSpan | None = type(self)._class_column_span
        self._polling_interval: int | str | None = type(self)._class_polling_interval
        self._lazy: bool = bool(type(self)._class_is_lazy)
        self._can_view_override: bool | Callable[..., bool] | None = None
        self._page_filters: dict[str, Any] = {}
        if self._column_span_value == "full":
            self._column_span_full = True

    @classmethod
    def from_class(cls, item: type[Widget] | Widget | Any) -> Widget:
        """Instantiate from a registered class or pass through a Widget instance."""
        if isinstance(item, Widget):
            return item
        if isinstance(item, type) and issubclass(item, Widget):
            return item.make()
        raise TypeError(f"Expected Widget class or instance, got {type(item)!r}")

    @classmethod
    def instantiate(cls, item: type[Widget] | Widget | Any) -> Widget:
        """Alias for :meth:`from_class`."""
        return cls.from_class(item)

    @classmethod
    def can_view(cls, **ctx: Any) -> bool:
        """Whether this widget class may appear on the dashboard."""
        return True

    @classmethod
    def render_for_dashboard(cls, **ctx: Any) -> str:
        """Make an instance and render it (for class registration)."""
        return cls.make().render(**ctx)

    def heading(self, text: str) -> Self:  # noqa: F811
        self._heading = text
        return self

    def description(self, text: str) -> Self:  # noqa: F811
        self._description = text
        return self

    def get_heading(self) -> str | None:
        return self._heading

    def get_description(self) -> str | None:
        return self._description

    def sort(self, value: int) -> Self:  # noqa: F811
        self._sort = int(value)
        return self

    def get_sort(self) -> int:
        if self._sort is not None:
            return self._sort
        return int(getattr(type(self), "_class_sort", 0) or 0)

    def column_span(self, span: ColumnSpan) -> Self:  # type: ignore[override]
        self._column_span_value = span
        self._column_span_full = span == "full"
        self._column_span = span if isinstance(span, (int, str)) else None
        return self

    def column_span_full(self, condition: bool = True) -> Self:
        self._column_span_full = condition
        if condition:
            self._column_span_value = "full"
        return self

    def get_column_span(self) -> ColumnSpan | None:
        if self._column_span_full:
            return "full"
        return self._column_span_value

    def polling_interval(self, value: int | str | None) -> Self:  # noqa: F811
        self._polling_interval = value
        return self

    def get_polling_interval(self) -> str | None:
        return normalize_polling_interval(self._polling_interval)

    def lazy(self, condition: bool = True) -> Self:  # noqa: F811
        self._lazy = bool(condition)
        return self

    def is_lazy(self) -> bool:  # noqa: F811
        return bool(self._lazy)

    def can_view_when(self, condition: bool | Callable[..., bool]) -> Self:
        """Instance-level override for :meth:`can_view`."""
        self._can_view_override = condition
        return self

    def check_can_view(self, **ctx: Any) -> bool:
        if self._can_view_override is not None:
            return bool(evaluate(self._can_view_override, **ctx))
        return bool(type(self).can_view(**ctx))

    def page_filters(self, filters: Mapping[str, Any] | None) -> Self:
        self._page_filters = dict(filters or {})
        return self

    def get_page_filters(self, **ctx: Any) -> dict[str, Any]:
        if self._page_filters:
            return dict(self._page_filters)
        raw = ctx.get("page_filters")
        return dict(raw) if isinstance(raw, Mapping) else {}

    def filter_value(self, key: str, default: Any = None, **ctx: Any) -> Any:
        return self.get_page_filters(**ctx).get(key, default)

    def get_data(self) -> Any:
        return None

    def span_class_attr(self) -> str:
        classes = column_span_classes(self.get_column_span(), full=self._column_span_full)
        return f" {classes}" if classes else ""

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.check_can_view(**ctx):
            return ""
        if "page_filters" in ctx and not self._page_filters:
            filters = ctx.get("page_filters")
            if isinstance(filters, Mapping):
                self._page_filters = dict(filters)

        title = e(self._heading or self.get_label())
        desc = (
            f'<p class="or-widget-desc">{e(self._description)}</p>' if self._description else ""
        )
        body = self.render_body(state, **ctx)
        span = self.span_class_attr()
        poll = self.get_polling_interval()
        poll_attr = f' data-polling="{e(poll)}"' if poll else ""
        lazy_attr = ' data-lazy="true"' if self.is_lazy() else ""
        lazy_placeholder = (
            '<div class="or-widget-lazy-placeholder" aria-hidden="true"></div>'
            if self.is_lazy()
            else ""
        )
        return (
            f'<section class="or-widget{span}" data-widget="{e(self.get_name() or "")}"'
            f"{poll_attr}{lazy_attr}>"
            f'<header class="or-widget-header"><h3>{title}</h3>{desc}</header>'
            f'<div class="or-widget-body">{lazy_placeholder}{body}</div></section>'
        )

    def render_body(self, state: Any = None, **ctx: Any) -> str:
        return ""


def resolve_widgets(
    items: Sequence[type[Widget] | Widget | Any],
    **ctx: Any,
) -> list[Widget]:
    """Instantiate, authorize, and sort widgets for a dashboard grid."""
    widgets: list[Widget] = []
    for item in items:
        widget = Widget.from_class(item)
        if ctx.get("page_filters") is not None and isinstance(ctx["page_filters"], Mapping):
            widget.page_filters(ctx["page_filters"])
        if not widget.check_can_view(**ctx):
            continue
        widgets.append(widget)
    widgets.sort(key=lambda w: w.get_sort())
    return widgets


def render_widgets(
    items: Sequence[type[Widget] | Widget | Any | str],
    **ctx: Any,
) -> list[str]:
    """Render widget classes/instances; HTML strings pass through after widgets."""
    widget_items: list[type[Widget] | Widget] = []
    html_bits: list[str] = []
    for item in items:
        if isinstance(item, str):
            html_bits.append(item)
        elif isinstance(item, Widget):
            widget_items.append(item)
        elif isinstance(item, type) and issubclass(item, Widget):
            widget_items.append(item)
        # Non-widget / non-string entries (legacy junk) are ignored.
    out = [html for w in resolve_widgets(widget_items, **ctx) if (html := w.render(**ctx))]
    out.extend(html_bits)
    return out
