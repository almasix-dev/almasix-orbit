"""Table cell layout components (Split, Stack, Panel, Grid, View).

Parent wiring (into ``table.py`` / ``columns.py``):
- Allow ``Table.columns([...])`` to accept layout components alongside ``Column``.
- ``Table.flat_columns()`` should recurse layout children to collect searchable/sortable columns.
- In ``Table.render`` row cells, when a column entry is a layout component, call
  ``layout.render_cell(record, **ctx)`` (single ``<td>`` wrapping the layout) instead of
  ``column.render_cell``.
- Header row: layouts typically span one logical column (label from first child or layout label).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e


class LayoutComponent(Component):
    """Base for table column layouts."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._components: list[Component] = []
        self._grow = True
        self._collapsible = False
        self._collapsed = True
        self._visible_from: str | None = None
        self._hidden_from: str | None = None
        self._alignment: str = "start"
        self._space: int | None = None

    @classmethod
    def make(cls, components: Sequence[Component] | str | None = None) -> Self:  # type: ignore[override]
        if isinstance(components, str) or components is None:
            inst = cls(components if isinstance(components, str) else None)
            return inst
        inst = cls(None)
        inst.schema(components)
        return inst

    def schema(self, components: Sequence[Component]) -> Self:
        self._components = list(components)
        return self

    def components(self, items: Sequence[Component]) -> Self:
        return self.schema(items)

    def get_components(self) -> list[Component]:
        return list(self._components)

    def grow(self, condition: bool = True) -> Self:
        self._grow = condition
        return self

    def collapsible(self, condition: bool = True) -> Self:
        self._collapsible = condition
        return self

    def collapsed(self, condition: bool = True) -> Self:
        self._collapsed = condition
        return self

    def visible_from(self, breakpoint: str) -> Self:
        self._visible_from = breakpoint
        return self

    def hidden_from(self, breakpoint: str) -> Self:
        self._hidden_from = breakpoint
        return self

    def alignment(self, value: str) -> Self:
        self._alignment = value
        return self

    def space(self, value: int) -> Self:
        self._space = value
        return self

    def flat_columns(self) -> list[Component]:
        out: list[Component] = []
        for child in self._components:
            flat = getattr(child, "flat_columns", None)
            if callable(flat):
                out.extend(flat())
            else:
                out.append(child)
        return out

    def _responsive_classes(self, base: str) -> str:
        classes = [base]
        if self._grow:
            classes.append("or-grow")
        else:
            classes.append("or-grow-none")
        if self._visible_from:
            classes.append(f"or-visible-from-{self._visible_from}")
        if self._hidden_from:
            classes.append(f"or-hidden-from-{self._hidden_from}")
        if self._space is not None:
            classes.append(f"or-space-{self._space}")
        classes.append(f"or-align-{self._alignment}")
        return " ".join(classes)

    def _render_child(self, child: Component, record: Any, **ctx: Any) -> str:
        if not child.is_visible(record=record, **ctx):
            return ""
        render_cell = getattr(child, "render_cell", None)
        if callable(render_cell):
            # Column.render_cell wraps <td>; strip outer td for nested layouts
            html = render_cell(record, **ctx)
            if html.startswith("<td") and html.endswith("</td>"):
                # Extract inner HTML of a single td
                close = html.find(">")
                if close != -1:
                    return f'<div class="or-layout-item">{html[close + 1 : -5]}</div>'
            return f'<div class="or-layout-item">{html}</div>'
        render_layout_cell = getattr(child, "render_cell_inner", None)
        if callable(render_layout_cell):
            return f'<div class="or-layout-item">{render_layout_cell(record, **ctx)}</div>'
        return f'<div class="or-layout-item">{child.render(record, record=record, **ctx)}</div>'

    def render_cell_inner(self, record: Any, **ctx: Any) -> str:
        raise NotImplementedError

    def render_cell(self, record: Any, **ctx: Any) -> str:
        if not self.is_visible(record=record, **ctx):
            return ""
        inner = self.render_cell_inner(record, **ctx)
        return f'<td class="or-td or-td-layout">{inner}</td>'

    def render(self, state: Any = None, **ctx: Any) -> str:
        record = ctx.get("record", state)
        inner_ctx = {k: v for k, v in ctx.items() if k != "record"}
        return self.render_cell_inner(record, **inner_ctx)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "components": [c.to_dict() for c in self._components],
                "grow": self._grow,
                "collapsible": self._collapsible,
                "collapsed": self._collapsed,
                "visible_from": self._visible_from,
                "alignment": self._alignment,
                "space": self._space,
            }
        )
        return d


class Split(LayoutComponent):
    """Horizontal split that can stack below a breakpoint (``.from_breakpoint``)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._from: str | None = None

    def from_breakpoint(self, value: str) -> Self:
        self._from = value
        return self

    # Filament uses ->from('md'); offer alias
    def from_(self, value: str) -> Self:
        return self.from_breakpoint(value)

    def render_cell_inner(self, record: Any, **ctx: Any) -> str:
        classes = self._responsive_classes("or-split")
        if self._from:
            classes += f" or-split-from-{e(self._from)}"
        children = "".join(self._render_child(c, record, **ctx) for c in self._components)
        collapsible_attrs = ""
        if self._collapsible:
            collapsible_attrs = (
                f' data-collapsible="true" data-collapsed="{str(self._collapsed).lower()}"'
            )
        return f'<div class="{classes}"{collapsible_attrs}>{children}</div>'


class Stack(LayoutComponent):
    """Vertical stack of columns inside a cell / split."""

    def render_cell_inner(self, record: Any, **ctx: Any) -> str:
        classes = self._responsive_classes("or-stack")
        children = "".join(self._render_child(c, record, **ctx) for c in self._components)
        collapsible_attrs = ""
        if self._collapsible:
            collapsible_attrs = (
                f' data-collapsible="true" data-collapsed="{str(self._collapsed).lower()}"'
            )
        return f'<div class="{classes}"{collapsible_attrs}>{children}</div>'


class Panel(LayoutComponent):
    """Styled collapsible panel wrapping nested layout / columns."""

    def render_cell_inner(self, record: Any, **ctx: Any) -> str:
        classes = self._responsive_classes("or-panel")
        children = "".join(self._render_child(c, record, **ctx) for c in self._components)
        collapsed = str(self._collapsed).lower()
        collapsible = "true" if self._collapsible else "false"
        return (
            f'<div class="{classes}" data-collapsible="{collapsible}" '
            f'data-collapsed="{collapsed}">{children}</div>'
        )


class Grid(LayoutComponent):
    """Responsive multi-column grid inside a cell (Filament ``Columns\\Layout\\Grid``)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._columns_count: int = 2

    def columns(self, count: int) -> Self:  # type: ignore[override]
        self._columns_count = max(1, int(count))
        return self

    def render_cell_inner(self, record: Any, **ctx: Any) -> str:
        n = self._columns_count
        classes = self._responsive_classes(f"or-layout-grid or-cols-{n}")
        children = "".join(self._render_child(c, record, **ctx) for c in self._components)
        return f'<div class="{classes}">{children}</div>'

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["columns"] = self._columns_count
        return d


class View(LayoutComponent):
    """Custom HTML layout wrapper (Filament ``Columns\\Layout\\View``).

    Distinct from ``ViewColumn`` (a single table column). Use ``.content()`` for a
    custom wrapper, and/or ``.schema()`` for nested columns rendered inside.
    """

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._view_html: Any = None

    def content(self, html: Any) -> Self:
        self._view_html = html
        return self

    def render_cell_inner(self, record: Any, **ctx: Any) -> str:
        from almasix.orbit.support.evaluate import evaluate

        classes = self._responsive_classes("or-layout-view")
        children = "".join(self._render_child(c, record, **ctx) for c in self._components)
        if self._view_html is not None:
            body = evaluate(self._view_html, record=record, children=children, **ctx)
            if body is None:
                body = children
            else:
                body = str(body)
                if "{children}" in body:
                    body = body.replace("{children}", children)
        else:
            body = children
        return f'<div class="{classes}">{body}</div>'
