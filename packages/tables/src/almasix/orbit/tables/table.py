"""Table builder."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.actions.action import Action
from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e
from almasix.orbit.tables.columns import Column, ColumnGroup
from almasix.orbit.tables.filters import Filter


class Table(Component):
    def __init__(self, name: str | None = "table") -> None:
        super().__init__(name)
        self._columns: list[Column | ColumnGroup] = []
        self._filters: list[Filter] = []
        self._filter_state: dict[str, Any] = {}
        self._actions: list[Action] = []
        self._bulk_actions: list[Action] = []
        self._header_actions: list[Action] = []
        self._query: Any = None
        self._records: list[Any] = []
        self._search: str = ""
        self._sort: str | None = None
        self._sort_direction: str = "asc"
        self._page = 1
        self._per_page = 10
        self._empty_state_heading = "No records"
        self._empty_state_description: str | None = None
        self._record_url: Callable[..., str] | str | None = None
        self._striped = True
        self._paginated = True

    def columns(self, columns: Sequence[Column | ColumnGroup]) -> Self:
        self._columns = list(columns)
        return self

    def filters(self, filters: Sequence[Filter]) -> Self:
        self._filters = list(filters)
        return self

    def filter_state(self, state: dict[str, Any]) -> Self:
        self._filter_state = dict(state)
        return self

    def actions(self, actions: Sequence[Action]) -> Self:
        self._actions = list(actions)
        return self

    def bulk_actions(self, actions: Sequence[Action]) -> Self:
        self._bulk_actions = list(actions)
        return self

    def header_actions(self, actions: Sequence[Action]) -> Self:
        self._header_actions = list(actions)
        return self

    def query(self, query: Any) -> Self:
        self._query = query
        return self

    def records(self, records: Sequence[Any]) -> Self:
        self._records = list(records)
        return self

    def record_url(self, url: Callable[..., str] | str) -> Self:
        self._record_url = url
        return self

    def flat_columns(self) -> list[Column]:
        out: list[Column] = []
        for col in self._columns:
            if isinstance(col, ColumnGroup):
                out.extend(col.get_columns())
            else:
                out.append(col)
        return out

    def get_records(self) -> list[Any]:
        records = list(self._records)
        if self._filter_state and self._filters:
            for f in self._filters:
                key = f.get_name() or ""
                if key in self._filter_state:
                    records = f.apply(records, self._filter_state[key])
        if self._search:
            records = [r for r in records if self._record_matches_search(r)]
        if self._sort:
            reverse = self._sort_direction == "desc"
            records = sorted(records, key=lambda r: self._record_value(r, self._sort), reverse=reverse)
        if self._paginated:
            start = (self._page - 1) * self._per_page
            return records[start : start + self._per_page]
        return records

    def get_total(self) -> int:
        records = list(self._records)
        if self._filter_state and self._filters:
            for f in self._filters:
                key = f.get_name() or ""
                if key in self._filter_state:
                    records = f.apply(records, self._filter_state[key])
        if self._search:
            records = [r for r in records if self._record_matches_search(r)]
        return len(records)

    def search(self, term: str) -> Self:
        self._search = term
        return self

    def sort(self, column: str, direction: str = "asc") -> Self:
        self._sort = column
        self._sort_direction = direction
        return self

    def paginate(self, page: int = 1, per_page: int = 10) -> Self:
        self._page = page
        self._per_page = per_page
        self._paginated = True
        return self

    def empty_state_heading(self, text: str) -> Self:
        self._empty_state_heading = text
        return self

    def empty_state_description(self, text: str) -> Self:
        self._empty_state_description = text
        return self

    def striped(self, condition: bool = True) -> Self:
        self._striped = condition
        return self

    def _record_value(self, record: Any, key: str) -> Any:
        if isinstance(record, dict):
            return record.get(key) or ""
        return getattr(record, key, "") or ""

    def _record_matches_search(self, record: Any) -> bool:
        term = self._search.lower()
        for col in self.flat_columns():
            if not col.is_searchable():
                continue
            val = col.resolve_state(record)
            if val is not None and term in str(val).lower():
                return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "columns": [c.to_dict() for c in self.flat_columns()],
            "filters": [f.to_dict() for f in self._filters],
            "actions": [a.to_dict() for a in self._actions],
            "bulk_actions": [a.to_dict() for a in self._bulk_actions],
            "total": self.get_total(),
            "page": self._page,
            "per_page": self._per_page,
        }

    def render(self, state: Any = None, **ctx: Any) -> str:
        records = self.get_records()
        flat = self.flat_columns()
        header_cells: list[str] = []
        for col in self._columns:
            if isinstance(col, ColumnGroup):
                span = len(col.get_columns())
                header_cells.append(
                    f'<th class="or-th or-th-group" colspan="{span}">{e(col.get_label(**ctx))}</th>'
                )
            else:
                header_cells.append(
                    f'<th class="or-th" data-sortable="{str(col.is_sortable()).lower()}">'
                    f'{e(col.get_label(**ctx))}</th>'
                )
        headers = "".join(header_cells)
        if self._actions:
            headers += '<th class="or-th or-th-actions">Actions</th>'
        rows = []
        for record in records:
            cells = "".join(c.render_cell(record, **ctx) for c in flat)
            if self._actions:
                acts = "".join(a.render(record, record=record, **ctx) for a in self._actions)
                cells += f'<td class="or-td or-td-actions">{acts}</td>'
            rows.append(f'<tr class="or-tr">{cells}</tr>')
        colspan = len(flat) + (1 if self._actions else 0)
        body = "".join(rows) or (
            f'<tr class="or-tr"><td class="or-td or-empty" colspan="{colspan}">'
            f'<div class="or-empty-state"><h3>{e(self._empty_state_heading)}</h3>'
            f'{f"<p>{e(self._empty_state_description)}</p>" if self._empty_state_description else ""}'
            f"</div></td></tr>"
        )
        striped = " or-table-striped" if self._striped else ""
        return (
            f'<div class="or-table-wrap"><table class="or-table{striped}">'
            f'<thead class="or-thead"><tr>{headers}</tr></thead>'
            f'<tbody class="or-tbody">{body}</tbody></table></div>'
        )
