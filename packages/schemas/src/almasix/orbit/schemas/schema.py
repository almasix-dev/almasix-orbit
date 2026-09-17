
"""Schema container — Filament 5 schemas package analogue."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from almasix.orbit.schemas.layouts import child_render_state
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
        """Collect dehydrated state for all fields, including those nested in layouts."""
        out: dict[str, Any] = {}
        try:
            from almasix.orbit.forms.walk import iter_fields

            fields = iter_fields(self._components)
        except ImportError:
            fields = [c for c in self._components if c.is_dehydrated() and c.get_state_path()]

        for c in fields:
            if not c.is_dehydrated():
                continue
            path = c.get_state_path()
            if not path:
                continue
            if path in self._state:
                value = self._state[path]
            elif c.get_default() is not None:
                value = c.get_default()
            else:
                continue
            mutate = getattr(c, "get_dehydrate_state_using", None)
            if callable(mutate):
                cb = mutate()
                if cb is not None:
                    from almasix.orbit.support.evaluate import evaluate

                    value = evaluate(cb, value, state=self._state, field=c)
            out[path] = value
        return out

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["columns"] = self._columns
        base["components"] = [c.to_dict() for c in self._components]
        return base

    def render(self, state: Any = None, **ctx: Any) -> str:
        data = state if isinstance(state, dict) else self._state
        parts = [
            c.render(child_render_state(c, data if isinstance(data, dict) else None), **ctx)
            for c in self._components
            if c.is_visible(**ctx)
        ]
        cols = self._columns
        return f'<div class="or-schema or-schema-cols-{cols}">' + "".join(parts) + "</div>"
