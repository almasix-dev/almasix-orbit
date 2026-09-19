"""Schema container — Filament 5 schemas package analogue."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, ClassVar, Self

from almasix.orbit.schemas.layouts import child_render_state
from almasix.orbit.support.component import Component


class Schema(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._components: list[Component] = []
        self._state: dict[str, Any] = {}
        self._columns: int = 1
        self._operation: str | None = None
        self._defer_loading = False

    _configure_using: ClassVar[list[Callable[[Schema], None]]] = []

    @classmethod
    def configure_using(cls, callback: Callable[[Schema], None]) -> None:
        """Register a default configurator (Filament ``Schema::configureUsing``)."""
        cls._configure_using.append(callback)

    @classmethod
    def make(cls, name: str | None = None) -> Self:
        instance = cls() if name is None else cls(name)
        for callback in cls._configure_using:
            callback(instance)
        return instance

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

    def operation(self, value: str) -> Self:
        """Set create / edit / view context for dependent visibility (Filament ``operation``)."""
        self._operation = value
        return self

    def get_operation(self) -> str | None:
        return self._operation

    def defer_loading(self, condition: bool = True) -> Self:
        """Mark the schema for deferred client load (``data-defer`` chrome)."""
        self._defer_loading = condition
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
            transform = getattr(c, "apply_dehydrate_transforms", None)
            if callable(transform):
                value = transform(value)
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
        base["operation"] = self._operation
        base["defer_loading"] = self._defer_loading
        base["components"] = [c.to_dict() for c in self._components]
        return base

    def render(self, state: Any = None, **ctx: Any) -> str:
        data = state if isinstance(state, dict) else self._state
        render_ctx = {**ctx}
        if self._operation is not None and "operation" not in render_ctx:
            render_ctx["operation"] = self._operation
        parts = [
            c.render(
                child_render_state(c, data if isinstance(data, dict) else None),
                **render_ctx,
            )
            for c in self._components
            if c.is_visible(**render_ctx)
        ]
        cols = self._columns
        defer = ' data-defer="true"' if self._defer_loading else ""
        return (
            f'<div class="or-schema or-schema-cols-{cols}"{defer}>'
            + "".join(parts)
            + "</div>"
        )
