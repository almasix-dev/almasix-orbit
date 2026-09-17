
"""Table filters."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate


class Filter(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._query: Callable[..., Any] | None = None
        self._options: dict[Any, Any] | Callable[..., dict[Any, Any]] = {}
        self._indicate: bool = True

    def query(self, callback: Callable[..., Any]) -> Self:
        self._query = callback
        return self

    def options(self, options: dict[Any, Any] | Callable[..., dict[Any, Any]]) -> Self:
        self._options = options
        return self

    def get_options(self, **ctx: Any) -> dict[Any, Any]:
        opts = self._options
        return dict(evaluate(opts, **ctx) if callable(opts) else opts)

    def apply(self, query: Any, value: Any) -> Any:
        if self._query is None or value in (None, "", []):
            return query
        return self._query(query, value)


class SelectFilter(Filter):
    pass


class TernaryFilter(Filter):
    pass


class FilterGroup(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._filters: list[Filter] = []

    def filters(self, filters: list[Filter]) -> Self:
        self._filters = list(filters)
        return self
