"""Infolist builder — Schema-compatible read-only record view."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from almasix.orbit.schemas.schema import Schema
from almasix.orbit.support.component import Component


class Infolist(Schema):
    def schema(self, components: Sequence[Component]) -> Self:  # type: ignore[override]
        return self.components(components)

    def render(self, state: Any = None, **ctx: Any) -> str:
        record = state if state is not None else self.get_state()
        render_ctx = {**ctx}
        if self._operation is not None and "operation" not in render_ctx:
            render_ctx["operation"] = self._operation
        if self.is_inline_label() or ctx.get("inline_label"):
            render_ctx["inline_label"] = True
        parts: list[str] = []
        for c in self.get_components():
            if not c.is_visible(record=record, **render_ctx):
                continue
            # Layouts (Section, Grid, …) and entries both expose render().
            parts.append(c.render(record, record=record, **render_ctx))
        cols = self._columns
        cols_c = f" or-infolist-cols-{cols}" if cols else ""
        return f'<dl class="or-infolist{cols_c}">{"".join(parts)}</dl>'
