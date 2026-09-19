"""Table row grouping (``Group``).

Parent wiring (into ``table.py`` — forms owns that file):
- ``Table.default_group(Group | str)`` / ``Table.groups([...])`` / ``Table.groups_only()``.
- In ``Table.render``, partition ``get_records()`` via ``Group.partition(records)``, emit a
  group header row (``Group.render_header``), then member rows (skip members if groups_only).
- When columns have summarizers, render a group summary row using each group's records.
- ``collapsed_groups_by_default`` should pass ``collapsed=True`` into ``render_header``.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e


@dataclass
class GroupBucket:
    key: Any
    title: str
    description: str | None
    records: list[Any]


class Group(Component):
    """Group table rows by an attribute (Filament ``Tables\\Grouping\\Group``)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._get_title: Callable[..., str] | None = None
        self._get_description: Callable[..., str | None] | None = None
        self._get_key: Callable[..., Any] | None = None
        self._title_prefixed_with_label = True
        self._collapsible = False
        self._date = False
        self._direction: str = "asc"
        self._order_query: Callable[..., Any] | None = None
        self._scope_query: Callable[..., Any] | None = None
        self._group_query: Callable[..., Any] | None = None

    def get_title_from_record_using(self, callback: Callable[..., str]) -> Self:
        self._get_title = callback
        return self

    def get_description_from_record_using(self, callback: Callable[..., str | None]) -> Self:
        self._get_description = callback
        return self

    def get_key_from_record_using(self, callback: Callable[..., Any]) -> Self:
        self._get_key = callback
        return self

    def title_prefixed_with_label(self, condition: bool = True) -> Self:
        self._title_prefixed_with_label = condition
        return self

    def collapsible(self, condition: bool = True) -> Self:
        self._collapsible = condition
        return self

    def is_collapsible(self) -> bool:
        return self._collapsible

    def date(self, condition: bool = True) -> Self:
        self._date = condition
        return self

    def direction(self, value: str) -> Self:
        self._direction = value
        return self

    def get_direction(self) -> str:
        return self._direction

    def order_query_using(self, callback: Callable[..., Any]) -> Self:
        self._order_query = callback
        return self

    def scope_query_by_key_using(self, callback: Callable[..., Any]) -> Self:
        self._scope_query = callback
        return self

    def group_query_using(self, callback: Callable[..., Any]) -> Self:
        self._group_query = callback
        return self

    def _dot_get(self, record: Any, path: str) -> Any:
        from almasix.orbit.tables.columns import dot_get

        return dot_get(record, path)

    def key_from_record(self, record: Any) -> Any:
        return self.get_key_from_record(record)

    def get_key_from_record(self, record: Any) -> Any:
        if self._get_key is not None:
            return evaluate(self._get_key, record, record=record)
        attr = self.get_name() or ""
        value = self._dot_get(record, attr)
        if self._date and value is not None:
            if isinstance(value, datetime):
                return value.date().isoformat()
            if isinstance(value, date):
                return value.isoformat()
            text = str(value)
            return text[:10] if len(text) >= 10 else text
        return value

    def title_from_record(self, record: Any) -> str:
        if self._get_title is not None:
            result = evaluate(self._get_title, record, record=record)
            return "" if result is None else str(result)
        key = self.key_from_record(record)
        title = "" if key is None else str(key)
        if self._title_prefixed_with_label:
            label = self.get_label()
            if label:
                return f"{label}: {title}"
        return title

    def description_from_record(self, record: Any) -> str | None:
        if self._get_description is None:
            return None
        result = evaluate(self._get_description, record, record=record)
        return None if result is None else str(result)

    def partition(self, records: Sequence[Any]) -> list[GroupBucket]:
        buckets: dict[Any, GroupBucket] = {}
        order: list[Any] = []
        for record in records:
            key = self.key_from_record(record)
            if key not in buckets:
                buckets[key] = GroupBucket(
                    key=key,
                    title=self.title_from_record(record),
                    description=self.description_from_record(record),
                    records=[],
                )
                order.append(key)
            buckets[key].records.append(record)
        result = [buckets[k] for k in order]
        reverse = self._direction == "desc"
        try:
            result.sort(key=lambda b: (b.key is None, b.key), reverse=reverse)
        except TypeError:
            result.sort(key=lambda b: str(b.key), reverse=reverse)
        return result

    def group_records(self, records: Sequence[Any]) -> list[GroupBucket]:
        """Partition records into group buckets (alias for ``partition``)."""
        return self.partition(records)

    def render_header(
        self,
        bucket: GroupBucket,
        *,
        colspan: int = 1,
        collapsed: bool = False,
        **ctx: Any,
    ) -> str:
        desc = (
            f'<div class="or-group-description">{e(bucket.description)}</div>'
            if bucket.description
            else ""
        )
        collapsible = "true" if self._collapsible else "false"
        collapsed_attr = "true" if collapsed and self._collapsible else "false"
        return (
            f'<tr class="or-tr or-group-header" data-group-key="{e(bucket.key)}" '
            f'data-collapsible="{collapsible}" data-collapsed="{collapsed_attr}">'
            f'<th class="or-th or-group-title" colspan="{colspan}">'
            f'<span class="or-group-title-text">{e(bucket.title)}</span>{desc}'
            f"</th></tr>"
        )

    def render(self, state: Any = None, **ctx: Any) -> str:
        """Render all group headers + optional placeholder for members (parent wires rows)."""
        records = ctx.get("records") or (state if isinstance(state, list) else [])
        colspan = int(ctx.get("colspan") or 1)
        collapsed = bool(ctx.get("collapsed", False))
        header_ctx = {k: v for k, v in ctx.items() if k not in {"colspan", "collapsed", "records"}}
        parts = [
            self.render_header(bucket, colspan=colspan, collapsed=collapsed, **header_ctx)
            for bucket in self.partition(records)
        ]
        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "collapsible": self._collapsible,
                "date": self._date,
                "direction": self._direction,
                "title_prefixed_with_label": self._title_prefixed_with_label,
            }
        )
        return d
