
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


class TrashedFilter(SelectFilter):
    """Soft-delete scope filter (without / with / only trashed)."""

    WITH_TRASHED = "with"
    ONLY_TRASHED = "only"

    def __init__(self, name: str | None = "trashed") -> None:
        super().__init__(name)
        self._options = {
            "": "Without trashed",
            self.WITH_TRASHED: "With trashed",
            self.ONLY_TRASHED: "Only trashed",
        }
        self._indicate = True

    def apply(self, query: Any, value: Any) -> Any:
        if self._query is not None:
            return super().apply(query, value)
        if value in (None, ""):
            return [r for r in query if not _is_trashed(r)]
        if value == self.WITH_TRASHED:
            return list(query)
        if value == self.ONLY_TRASHED:
            return [r for r in query if _is_trashed(r)]
        return query


def _is_trashed(record: Any) -> bool:
    if isinstance(record, dict):
        if record.get("deleted_at") is not None:
            return True
        return bool(record.get("trashed"))
    deleted = getattr(record, "deleted_at", None)
    if deleted is not None:
        return True
    return bool(getattr(record, "trashed", False))


class FilterGroup(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._filters: list[Filter] = []

    def filters(self, filters: list[Filter]) -> Self:
        self._filters = list(filters)
        return self
