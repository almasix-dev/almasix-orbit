
"""Schema container — Filament 5 schemas package analogue."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component


class Schema(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._components: list[Component] = []
        self._state: dict[str, Any] = {}
        self._columns: int = 1

    def components(self, components: Sequence[Component]) -> Self:
        self._components = list(components)
        return self

    def schema(self, components: Sequence[Component]) -> Self:
        return self.components(components)

    def get_components(self) -> list[Component]:
        return list(self._components)

    def columns(self, count: int) -> Self:
        self._columns = count
        return self

    def state(self, data: dict[str, Any]) -> Self:
        self._state = dict(data)
        return self

    def get_state(self) -> dict[str, Any]:
        return dict(self._state)

    def fill(self, data: dict[str, Any]) -> Self:
        self._state.update(data)
        return self

    def dehydrate(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for c in self._components:
            if not c.is_dehydrated():
                continue
            path = c.get_state_path()
            if not path:
                continue
            if path in self._state:
                out[path] = self._state[path]
            elif c.get_default() is not None:
                out[path] = c.get_default()
        return out

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["columns"] = self._columns
        base["components"] = [c.to_dict() for c in self._components]
        return base

    def render(self, state: Any = None, **ctx: Any) -> str:
        data = state if isinstance(state, dict) else self._state
        parts = [
            c.render(data.get(c.get_state_path() or "") if isinstance(data, dict) else None, **ctx)
            for c in self._components
            if c.is_visible(**ctx)
        ]
        cols = self._columns
        return f'<div class="or-schema or-schema-cols-{cols}">' + "".join(parts) + "</div>"
