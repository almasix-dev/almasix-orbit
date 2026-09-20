"""Default panel Dashboard page (Filament Dashboard analogue)."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, ClassVar

from almasix.orbit.panels.page import Page
from almasix.orbit.support.html import e
from almasix.orbit.widgets.widget import Widget, render_widgets


class Dashboard(Page):
    """Default first page for a panel (home route ``/``)."""

    title = "Dashboard"
    slug = "dashboard"
    navigation_icon: ClassVar[str] = "heroicon-o-home"
    navigation_label: ClassVar[str | None] = "Dashboard"
    # Own sidebar root (apps layout) — not the ungrouped "Menu" bucket.
    navigation_group: ClassVar[str | None] = "Dashboard"
    navigation_sort: ClassVar[int] = -100

    #: Optional alternate route path for multi-dashboard setups (e.g. ``\"analytics\"``).
    route_path: ClassVar[str | None] = None
    #: Persist filter values in the session when True.
    persists_filters_in_session: ClassVar[bool] = False
    #: Optional FilterAction-like header filters (rendered beside the title).
    filters_in_header: ClassVar[bool] = False

    _filters_schema: ClassVar[Any] = None
    _header_filter_actions: ClassVar[Sequence[Any] | None] = None

    @classmethod
    def get_columns(cls) -> int | dict[str, int]:
        """Grid column count (int) or responsive breakpoint map."""
        return 2

    @classmethod
    def get_widgets(cls, panel: Any = None) -> list[Any]:
        """Widgets for this dashboard; default defers to ``panel.get_widgets()``."""
        if panel is not None:
            return list(panel.get_widgets())
        return []

    @classmethod
    def filters_form(cls, schema: Any) -> type[Dashboard]:
        """Store filter form/schema components rendered above the widget grid."""
        cls._filters_schema = schema
        return cls

    @classmethod
    def header_filter_actions(cls, actions: Sequence[Any]) -> type[Dashboard]:
        """Optional FilterAction-like actions rendered in the page header."""
        cls._header_filter_actions = list(actions)
        return cls

    @classmethod
    def get_route_path(cls) -> str | None:
        return cls.route_path

    @classmethod
    def resolve_widget_items(cls, panel: Any = None, **ctx: Any) -> list[Any]:
        """Resolve widget classes/instances; ``ctx['widgets']`` wins when provided."""
        if "widgets" in ctx and ctx["widgets"] is not None:
            return list(ctx["widgets"])
        resolved_panel = panel if panel is not None else ctx.get("panel")
        return list(cls.get_widgets(resolved_panel))

    @classmethod
    def _columns_style(cls, columns: int | dict[str, int]) -> tuple[str, str]:
        if isinstance(columns, Mapping):
            default = int(columns.get("default") or columns.get("lg") or next(iter(columns.values()), 2))
            parts = [f"--or-dashboard-cols: {default}"]
            for bp, n in columns.items():
                if bp in {"default", "lg"} and int(n) == default:
                    continue
                token = str(bp).strip().lower()
                parts.append(f"--or-dashboard-cols-{token}: {int(n)}")
            style = "; ".join(parts)
            data = e(json.dumps(dict(columns)))
            return style, data
        n = int(columns)
        return f"--or-dashboard-cols: {n}", str(n)

    @classmethod
    def _render_filters(cls, **ctx: Any) -> str:
        schema = cls._filters_schema
        if schema is None:
            return ""
        state = ctx.get("page_filters") or ctx.get("filter_state") or {}
        if hasattr(schema, "render"):
            body = schema.render(state, **ctx)
        elif isinstance(schema, Sequence) and not isinstance(schema, (str, bytes)):
            body = "".join(
                c.render(state, **ctx) if hasattr(c, "render") else str(c) for c in schema
            )
        else:
            body = str(schema)
        return f'<div class="or-dashboard-filters">{body}</div>'

    @classmethod
    def _render_header_actions(cls, **ctx: Any) -> str:
        actions = cls._header_filter_actions or ()
        if not actions and not cls.filters_in_header:
            return ""
        bits: list[str] = []
        for action in actions:
            if hasattr(action, "render"):
                bits.append(action.render(**ctx))
            else:
                bits.append(str(action))
        if not bits:
            return ""
        return f'<div class="or-dashboard-header-actions">{"".join(bits)}</div>'

    @classmethod
    def render(cls, **ctx: Any) -> str:
        page_filters = ctx.get("page_filters")
        if page_filters is None:
            page_filters = {}
        ctx = {**ctx, "page_filters": page_filters}

        columns = ctx.get("columns")
        if columns is None:
            columns = cls.get_columns()
        style, data_cols = cls._columns_style(columns)  # type: ignore[arg-type]

        raw_widgets = cls.resolve_widget_items(**ctx)
        # Accept Widget instances, classes, or HTML strings (compat).
        rendered: list[str] = []
        if raw_widgets:
            rendered = render_widgets(raw_widgets, **ctx)
        filters_html = cls._render_filters(**ctx)
        header_actions = cls._render_header_actions(**ctx)

        if rendered:
            cards = "".join(w if isinstance(w, str) else "" for w in rendered)
            body = (
                f"{filters_html}"
                f'<div class="or-dashboard-widgets" style="{style}" data-cols="{data_cols}">'
                f"{cards}</div>"
            )
        elif filters_html:
            body = filters_html
        else:
            brand = e(str(ctx.get("brand") or "Orbit"))
            body = (
                f'<p class="or-muted">Welcome to {brand}. '
                f"Register resources or customize this dashboard.</p>"
            )

        return (
            f'<div class="or-page or-page-dashboard">'
            f'<div class="or-dashboard-heading">'
            f'<h1 class="or-page-title">{e(cls.get_title())}</h1>'
            f"{header_actions}"
            f"</div>"
            f"{body}"
            f"</div>"
        )

    @classmethod
    def mount_widgets(cls, panel: Any, **ctx: Any) -> list[Widget]:
        """Instantiate authorized widgets for advanced callers."""
        from almasix.orbit.widgets.widget import resolve_widgets

        return resolve_widgets(cls.resolve_widget_items(panel, **ctx), **ctx)
