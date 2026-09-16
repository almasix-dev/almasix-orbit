
"""Infolist builder."""

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
        parts = [
            c.render(record, record=record, **ctx)
            for c in self.get_components()
            if c.is_visible(record=record, **ctx)
        ]
        return f'<dl class="or-infolist">{"".join(parts)}</dl>'
