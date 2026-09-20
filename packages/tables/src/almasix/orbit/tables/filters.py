"""Table filters."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate


class Filter(Component):
    """Base table filter.

    Without ``.options()``, Filament-style chrome is a checkbox (or ``.toggle()``).
    When the control is on, ``.query()`` scopes the records.
    """

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._query: Callable[..., Any] | None = None
        self._options: dict[Any, Any] | Callable[..., dict[Any, Any]] = {}
        self._indicate: bool = True
        self._indicate_using: Callable[..., Any] | None = None
        self._attribute: str | None = None
        self._toggle: bool = False
        self._ui: str | None = None  # "checkbox" | "toggle" | "select" | None=auto

    def query(self, callback: Callable[..., Any]) -> Self:
        self._query = callback
        return self

    def options(self, options: dict[Any, Any] | Callable[..., dict[Any, Any]]) -> Self:
        self._options = options
        return self

    def attribute(self, name: str) -> Self:
        """Column / attribute used when applying the default filter query (Filament parity)."""
        self._attribute = name
        return self

    def indicate(self, condition: bool = True) -> Self:
        """Whether this filter contributes an indicator chip when active."""
        self._indicate = condition
        return self

    def indicate_using(self, callback: Callable[..., Any]) -> Self:
        """Custom chip value text. Return ``None`` / ``""`` to hide the chip."""
        self._indicate_using = callback
        return self

    def toggle(self, condition: bool = True) -> Self:
        """Use a toggle switch instead of a checkbox for boolean filters."""
        self._toggle = condition
        if condition:
            self._ui = "toggle"
        return self

    def get_attribute(self) -> str:
        return self._attribute or self.get_name() or ""

    def get_options(self, **ctx: Any) -> dict[Any, Any]:
        opts = self._options
        return dict(evaluate(opts, **ctx) if callable(opts) else opts)

    def is_boolean_filter(self) -> bool:
        """True when chrome should be checkbox/toggle (no select options)."""
        if self._ui in ("checkbox", "toggle"):
            return True
        if self._ui == "select":
            return False
        if isinstance(self, SelectFilter) and not isinstance(self, TernaryFilter):
            return False
        if isinstance(self, TernaryFilter):
            return False
        opts = self._options
        if callable(opts):
            return False
        return not opts

    def is_toggle(self) -> bool:
        return bool(self._toggle) or self._ui == "toggle"

    def should_indicate(self) -> bool:
        return bool(self._indicate)

    def resolve_indicator(self, value: Any, **ctx: Any) -> str | None:
        if not self.should_indicate():
            return None
        if self._indicate_using is not None:
            text = evaluate(
                self._indicate_using,
                state=value,
                value=value,
                filter=self,
                **ctx,
            )
            if text in (None, ""):
                return None
            return str(text)
        if self.is_boolean_filter():
            return "Yes" if _is_truthy_filter_value(value) else None
        opts = self.get_options(**ctx)
        if isinstance(value, (list, tuple, set)):
            labels = [str(opts.get(v, opts.get(str(v), v))) for v in value]
            return ", ".join(labels) if labels else None
        return str(opts.get(value, opts.get(str(value), value)))

    def apply(self, query: Any, value: Any) -> Any:
        if self.is_boolean_filter():
            if not _is_truthy_filter_value(value):
                return query
            if self._query is None:
                return query
            return self._query(query, value)
        if self._query is None or value in (None, "", []):
            return query
        return self._query(query, value)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "attribute": self._attribute,
                "indicate": self._indicate,
                "toggle": self._toggle,
                "boolean": self.is_boolean_filter(),
            }
        )
        return d


class SelectFilter(Filter):
    """Select filter — defaults to equality on the filter attribute (or name)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._ui = "select"
        self._multiple: bool = False
        self._selectable_placeholder: bool = True

    def multiple(self, condition: bool = True) -> Self:
        self._multiple = condition
        return self

    def selectable_placeholder(self, condition: bool = True) -> Self:
        """When False, omit the blank “All” option (Filament ``selectablePlaceholder``)."""
        self._selectable_placeholder = condition
        return self

    def is_multiple(self) -> bool:
        return bool(self._multiple)

    def has_selectable_placeholder(self) -> bool:
        return bool(self._selectable_placeholder)

    def apply(self, query: Any, value: Any) -> Any:
        if self._query is not None:
            return super().apply(query, value)
        if value in (None, "", []):
            return query
        key = self.get_attribute()
        if not key:
            return query
        wanted: set[str]
        if self._multiple and isinstance(value, (list, tuple, set)):
            wanted = {str(v) for v in value if v not in (None, "")}
        else:
            wanted = {str(value)}
        if not wanted:
            return query
        out: list[Any] = []
        for record in query:
            if isinstance(record, dict):
                current = record.get(key)
            else:
                current = getattr(record, key, None)
            if isinstance(current, (list, tuple, set)):
                if wanted & {str(v) for v in current}:
                    out.append(record)
            elif str(current) in wanted:
                out.append(record)
        return out

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "multiple": self._multiple,
                "selectable_placeholder": self._selectable_placeholder,
            }
        )
        return d


class TernaryFilter(SelectFilter):
    """Boolean tri-state filter (All / Yes / No)."""

    TRUE = "1"
    FALSE = "0"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._true_label: str = "Yes"
        self._false_label: str = "No"
        self._placeholder: str = "All"
        self._nullable: bool = False
        self._true_query: Callable[..., Any] | None = None
        self._false_query: Callable[..., Any] | None = None
        self._blank_query: Callable[..., Any] | None = None
        self._refresh_options()

    def _refresh_options(self) -> None:
        self._options = {
            "": self._placeholder,
            self.TRUE: self._true_label,
            self.FALSE: self._false_label,
        }

    def true_label(self, label: str) -> Self:
        self._true_label = label
        self._refresh_options()
        return self

    def false_label(self, label: str) -> Self:
        self._false_label = label
        self._refresh_options()
        return self

    def placeholder(self, label: str) -> Self:
        self._placeholder = label
        self._refresh_options()
        return self

    def nullable(self, condition: bool = True) -> Self:
        """Treat blank/null attribute values as a distinct “false” match when filtering."""
        self._nullable = condition
        return self

    def queries(
        self,
        *,
        true: Callable[..., Any] | None = None,
        false: Callable[..., Any] | None = None,
        blank: Callable[..., Any] | None = None,
    ) -> Self:
        """Custom apply callbacks for each ternary state (Filament ``queries``)."""
        self._true_query = true
        self._false_query = false
        self._blank_query = blank
        return self

    def apply(self, query: Any, value: Any) -> Any:
        if self._query is not None:
            return Filter.apply(self, query, value)
        if value in (None, ""):
            if self._blank_query is not None:
                return self._blank_query(query, value)
            return query
        if value in (True, 1, "1", "true", "yes", self.TRUE):
            if self._true_query is not None:
                return self._true_query(query, value)
            want = True
        elif value in (False, 0, "0", "false", "no", self.FALSE):
            if self._false_query is not None:
                return self._false_query(query, value)
            want = False
        else:
            return query
        key = self.get_attribute()
        if not key:
            return query
        out: list[Any] = []
        for record in query:
            if isinstance(record, dict):
                current = record.get(key)
            else:
                current = getattr(record, key, None)
            if self._nullable and current is None:
                truthy = False
            else:
                truthy = bool(current) and current not in (0, "0", "false", "no", False)
            if truthy is want:
                out.append(record)
        return out


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
            return Filter.apply(self, query, value)
        if value in (None, ""):
            return [r for r in query if not _is_trashed(r)]
        if value == self.WITH_TRASHED:
            return list(query)
        if value == self.ONLY_TRASHED:
            return [r for r in query if _is_trashed(r)]
        return query


def is_trashed(record: Any) -> bool:
    """True when a record carries a ``deleted_at`` timestamp or a ``trashed`` flag."""
    return _is_trashed(record)


def _is_trashed(record: Any) -> bool:
    if isinstance(record, dict):
        if record.get("deleted_at") is not None:
            return True
        return bool(record.get("trashed"))
    deleted = getattr(record, "deleted_at", None)
    if deleted is not None:
        return True
    return bool(getattr(record, "trashed", False))


def _is_truthy_filter_value(value: Any) -> bool:
    return value not in (None, "", False, 0, "0", "false", "no", [])


class FilterGroup(Component):
    """Named group of filters — flattened for apply; rendered with a section title."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._filters: list[Filter | FilterGroup] = []

    def filters(self, filters: list[Filter | FilterGroup]) -> Self:
        self._filters = list(filters)
        return self

    def get_filters(self) -> list[Filter | FilterGroup]:
        return list(self._filters)


def flatten_filters(filters: Sequence[Filter | FilterGroup]) -> list[Filter]:
    """Expand :class:`FilterGroup` nests into a flat filter list (apply + chrome order)."""
    out: list[Filter] = []
    for item in filters:
        if isinstance(item, FilterGroup):
            out.extend(flatten_filters(item._filters))
        else:
            out.append(item)
    return out


class QueryBuilderFilter(Filter):
    """Wraps a QueryBuilder (or any object with ``apply`` / ``render``) as a table filter."""

    def __init__(self, name: str | None = "query") -> None:
        super().__init__(name)
        self._builder: Any = None
        self._ui = "select"  # custom render via builder

    def is_boolean_filter(self) -> bool:
        return False

    def builder(self, builder: Any) -> Self:
        self._builder = builder
        return self

    def get_builder(self) -> Any:
        return self._builder

    def apply(self, query: Any, value: Any) -> Any:
        if self._query is not None:
            return Filter.apply(self, query, value)
        if self._builder is None:
            return query
        if isinstance(value, list) and hasattr(self._builder, "rules"):
            self._builder.rules(value)
        if hasattr(self._builder, "apply"):
            return self._builder.apply(list(query))
        return query

    def render(self, state: Any = None, **ctx: Any) -> str:
        if self._builder is not None and hasattr(self._builder, "render"):
            return self._builder.render(state, **ctx)
        return ""
