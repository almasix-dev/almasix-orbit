
"""Layout components for schemas."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon


class Layout(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._schema: list[Component] = []
        self._dense = False
        self._gap: bool | str = True
        self._defer_loading = False

    def schema(self, components: Sequence[Component]) -> Self:
        self._schema = list(components)
        return self

    def dense(self, condition: bool = True) -> Self:
        self._dense = condition
        return self

    def gap(self, value: bool | str = True) -> Self:
        self._gap = value
        return self

    def defer_loading(self, condition: bool = True) -> Self:
        self._defer_loading = condition
        return self

    def get_child_components(self) -> list[Component]:
        return list(self._schema)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["schema"] = [c.to_dict() for c in self._schema]
        d["dense"] = self._dense
        return d

    def _layout_classes(self, base: str) -> str:
        classes = [base]
        if self._dense:
            classes.append("or-dense")
        if self._gap is False:
            classes.append("or-gap-none")
        elif isinstance(self._gap, str):
            classes.append(f"or-gap-{self._gap}")
        return " ".join(classes)

    def render_children(self, state: Any = None, **ctx: Any) -> str:
        data = state if isinstance(state, dict) else {}
        return "".join(
            c.render(data.get(c.get_state_path() or "") if data else None, **ctx)
            for c in self._schema
            if c.is_visible(**ctx)
        )


class Grid(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._columns = 2
        self._grid_container = False

    def columns(self, count: int) -> Self:
        self._columns = count
        return self

    def grid_container(self, condition: bool = True) -> Self:
        self._grid_container = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        classes = self._layout_classes(f"or-grid or-grid-cols-{self._columns}")
        if self._grid_container:
            classes += " or-grid-container"
        defer = ' data-defer="true"' if self._defer_loading else ""
        return f'<div class="{classes}"{defer}>{self.render_children(state, **ctx)}</div>'


class Flex(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._grow = True
        self._from: str | None = None

    def grow(self, condition: bool = True) -> Self:
        self._grow = condition
        return self

    def from_breakpoint(self, value: str) -> Self:
        """Stack below breakpoint (e.g. ``md``), flex row from that size up."""
        self._from = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        classes = self._layout_classes("or-flex")
        if self._grow:
            classes += " or-flex-grow"
        if self._from:
            classes += f" or-flex-from-{e(self._from)}"
        children = []
        for child in self._schema:
            if not child.is_visible(**ctx):
                continue
            data = state if isinstance(state, dict) else {}
            inner = child.render(data.get(child.get_state_path() or "") if data else None, **ctx)
            span = child._column_span
            span_cls = f" or-col-span-{span}" if span else ""
            children.append(f'<div class="or-flex-item{span_cls}">{inner}</div>')
        return f'<div class="{classes}">{"".join(children)}</div>'


class Section(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._heading: str | None = None
        self._description: str | None = None
        self._collapsible = False
        self._collapsed = False

    def heading(self, text: str) -> Self:
        self._heading = text
        return self

    def description(self, text: str) -> Self:
        self._description = text
        return self

    def collapsible(self, condition: bool = True) -> Self:
        self._collapsible = condition
        return self

    def collapsed(self, condition: bool = True) -> Self:
        self._collapsed = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        title = e(self._heading or self.get_label())
        desc = f'<p class="or-section-desc">{e(self._description)}</p>' if self._description else ""
        return (
            f'<section class="or-section" data-collapsible="{str(self._collapsible).lower()}" '
            f'data-collapsed="{str(self._collapsed).lower()}">'
            f'<header class="or-section-header"><h3 class="or-section-title">{title}</h3>{desc}</header>'
            f'<div class="or-section-body">{self.render_children(state, **ctx)}</div>'
            f"</section>"
        )


class Tabs(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._tabs: list[tuple[str, list[Component]]] = []

    def tabs(self, *tab_defs: tuple[str, Sequence[Component]]) -> Self:
        self._tabs = [(label, list(comps)) for label, comps in tab_defs]
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        nav = []
        bodies = []
        for i, (label, comps) in enumerate(self._tabs):
            active = " is-active" if i == 0 else ""
            nav.append(f'<button type="button" class="or-tab{active}" data-tab="{i}">{e(label)}</button>')
            inner = "".join(
                c.render((state or {}).get(c.get_state_path() or "") if isinstance(state, dict) else None, **ctx)
                for c in comps
            )
            bodies.append(f'<div class="or-tab-panel{active}" data-panel="{i}">{inner}</div>')
        return (
            '<div class="or-tabs" x-data="{ tab: 0 }">'
            f'<div class="or-tabs-nav">{"".join(nav)}</div>'
            f'<div class="or-tabs-body">{"".join(bodies)}</div>'
            "</div>"
        )


class Fieldset(Layout):
    def render(self, state: Any = None, **ctx: Any) -> str:
        legend = e(self.get_label())
        return (
            f'<fieldset class="or-fieldset"><legend class="or-fieldset-legend">{legend}</legend>'
            f"{self.render_children(state, **ctx)}</fieldset>"
        )


class Wizard(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._steps: list[tuple[str, list[Component]]] = []

    def steps(self, *step_defs: tuple[str, Sequence[Component]]) -> Self:
        self._steps = [(label, list(comps)) for label, comps in step_defs]
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        parts = []
        for i, (label, comps) in enumerate(self._steps):
            inner = "".join(
                c.render((state or {}).get(c.get_state_path() or "") if isinstance(state, dict) else None, **ctx)
                for c in comps
            )
            parts.append(
                f'<div class="or-wizard-step" data-step="{i}">'
                f'<h4 class="or-wizard-step-title">{e(label)}</h4>{inner}</div>'
            )
        return f'<div class="or-wizard" x-data="{{ step: 0 }}">{"".join(parts)}</div>'


class Callout(Layout):
    """Status callout with optional footer actions."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._description: str | None = None
        self._status: str = "info"
        self._color: str | None = None
        self._icon: str | None = None
        self._icon_color: str | None = None
        self._footer_actions: list[Component] = []
        self._footer_alignment: str = "start"

    def description(self, text: str) -> Self:
        self._description = text
        return self

    def status(self, value: str) -> Self:
        self._status = value
        return self

    def danger(self) -> Self:
        return self.status("danger")

    def info(self) -> Self:
        return self.status("info")

    def success(self) -> Self:
        return self.status("success")

    def warning(self) -> Self:
        return self.status("warning")

    def color(self, value: str) -> Self:
        self._color = value
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def icon_color(self, value: str) -> Self:
        self._icon_color = value
        return self

    def footer_actions(self, actions: Sequence[Component]) -> Self:
        self._footer_actions = list(actions)
        return self

    def footer_actions_alignment(self, value: str) -> Self:
        self._footer_alignment = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        color = self._color or self._status
        title = e(self.get_label(**ctx) or self._status.title())
        desc = f'<p class="or-callout-desc">{e(self._description)}</p>' if self._description else ""
        body = self.render_children(state, **ctx)
        ic_name = self._icon or {
            "danger": "heroicon-o-x-mark",
            "success": "heroicon-o-check",
            "warning": "heroicon-o-bell",
            "info": "heroicon-o-information-circle",
        }.get(self._status, "heroicon-o-information-circle")
        ic = render_icon(ic_name)
        icon_color = self._icon_color or color
        footer = ""
        if self._footer_actions:
            acts = "".join(a.render(state, **ctx) for a in self._footer_actions)
            footer = (
                f'<div class="or-callout-footer or-align-{e(self._footer_alignment)}">{acts}</div>'
            )
        return (
            f'<div class="or-callout or-callout-{e(self._status)} or-color-{e(color)}" role="status">'
            f'<div class="or-callout-icon or-color-{e(icon_color)}">{ic}</div>'
            f'<div class="or-callout-body"><div class="or-callout-title">{title}</div>'
            f"{desc}{body}</div>{footer}</div>"
        )


class EmptyState(Layout):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._heading: str | None = None
        self._description: str | None = None
        self._icon: str | None = None
        self._actions: list[Component] = []

    def heading(self, text: str) -> Self:
        self._heading = text
        return self

    def description(self, text: str) -> Self:
        self._description = text
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def actions(self, actions: Sequence[Component]) -> Self:
        self._actions = list(actions)
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        title = e(self._heading or self.get_label(**ctx) or "Nothing here")
        desc = f'<p class="or-empty-state-desc">{e(self._description)}</p>' if self._description else ""
        ic = f'<div class="or-empty-state-icon">{render_icon(self._icon)}</div>' if self._icon else ""
        acts = "".join(a.render(state, **ctx) for a in self._actions)
        actions_html = f'<div class="or-empty-state-actions">{acts}</div>' if acts else ""
        body = self.render_children(state, **ctx)
        return (
            f'<div class="or-empty-state or-schema-empty">'
            f"{ic}<h3 class=\"or-empty-state-heading\">{title}</h3>{desc}{body}{actions_html}</div>"
        )
