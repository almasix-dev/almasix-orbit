
"""Layout components for schemas."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e


class Layout(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._schema: list[Component] = []

    def schema(self, components: Sequence[Component]) -> Self:
        self._schema = list(components)
        return self

    def get_child_components(self) -> list[Component]:
        return list(self._schema)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["schema"] = [c.to_dict() for c in self._schema]
        return d

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

    def columns(self, count: int) -> Self:
        self._columns = count
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        return f'<div class="or-grid or-grid-cols-{self._columns}">{self.render_children(state, **ctx)}</div>'


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
