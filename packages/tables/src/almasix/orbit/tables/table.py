"""Table builder."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.actions.action import Action
from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e
from almasix.orbit.tables.columns import Column, ColumnGroup
from almasix.orbit.tables.filters import Filter
from almasix.orbit.tables.grouping import Group
from almasix.orbit.tables.layout import LayoutComponent

ColumnLike = Column | ColumnGroup | LayoutComponent


class Table(Component):
    def __init__(self, name: str | None = "table") -> None:
        super().__init__(name)
        self._columns: list[ColumnLike] = []
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
        self._default_group: Group | None = None
        self._groups: list[Group] = []
        self._groups_only = False
        self._collapsed_groups_by_default = False
        self._content_grid: dict[str, Any] | None = None
        self._persist_filters_in_session = False
        self._filters_session_key: str | None = None
        self._defer_filters = False
        self._query_builder: Any | None = None

    def columns(self, columns: Sequence[ColumnLike]) -> Self:
        self._columns = list(columns)
        return self

    def filters(self, filters: Sequence[Filter]) -> Self:
        self._filters = list(filters)
        return self

    def filter_state(self, state: dict[str, Any]) -> Self:
        self._filter_state = dict(state)
        return self

    def persist_filters_in_session(
        self,
        condition: bool = True,
        *,
        key: str | None = None,
    ) -> Self:
        self._persist_filters_in_session = condition
        if key is not None:
            self._filters_session_key = key
        return self

    def defer_filters(self, condition: bool = True) -> Self:
        self._defer_filters = condition
        return self

    def query_builder(self, builder: Any) -> Self:
        """Attach a QueryBuilder (or compatible) rendered in the filter chrome."""
        self._query_builder = builder
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

    def default_group(self, group: Group | str | None) -> Self:
        if group is None:
            self._default_group = None
        elif isinstance(group, str):
            self._default_group = Group.make(group)
        else:
            self._default_group = group
        return self

    def groups(self, groups: Sequence[Group | str]) -> Self:
        out: list[Group] = []
        for g in groups:
            out.append(Group.make(g) if isinstance(g, str) else g)
        self._groups = out
        return self

    def groups_only(self, condition: bool = True) -> Self:
        self._groups_only = condition
        return self

    def collapsed_groups_by_default(self, condition: bool = True) -> Self:
        self._collapsed_groups_by_default = condition
        return self

    def content_grid(self, columns: int | dict[str, Any] | None = 2, **kwargs: Any) -> Self:
        if columns is None:
            self._content_grid = None
        elif isinstance(columns, dict):
            self._content_grid = dict(columns)
        else:
            self._content_grid = {"columns": columns, **kwargs}
        return self

    def flat_columns(self) -> list[Column]:
        out: list[Column] = []
        for col in self._columns:
            if isinstance(col, ColumnGroup):
                out.extend(col.get_columns())
            elif isinstance(col, LayoutComponent):
                for child in col.flat_columns():
                    if isinstance(child, Column):
                        out.append(child)
            elif isinstance(col, Column):
                out.append(col)
        return out

    def display_columns(self) -> list[Column | LayoutComponent]:
        """Top-level column entries used for header/body cell counts (layouts = 1 cell)."""
        out: list[Column | LayoutComponent] = []
        for col in self._columns:
            if isinstance(col, ColumnGroup):
                out.extend(col.get_columns())
            elif isinstance(col, (Column, LayoutComponent)):
                out.append(col)
        return out

    def _filtered_records(self) -> list[Any]:
        records = list(self._records)
        if self._filter_state and self._filters:
            for f in self._filters:
                key = f.get_name() or ""
                if key in self._filter_state:
                    records = f.apply(records, self._filter_state[key])
        if self._query_builder is not None and hasattr(self._query_builder, "apply"):
            records = self._query_builder.apply(records)
        if self._search:
            records = [r for r in records if self._record_matches_search(r)]
        if self._sort:
            reverse = self._sort_direction == "desc"
            records = sorted(
                records,
                key=lambda r: self._record_value(r, self._sort),
                reverse=reverse,
            )
        return records

    def get_records(self) -> list[Any]:
        records = self._filtered_records()
        if self._paginated:
            start = (self._page - 1) * self._per_page
            return records[start : start + self._per_page]
        return records

    def get_all_filtered_records(self) -> list[Any]:
        return self._filtered_records()

    def get_total(self) -> int:
        return len(self._filtered_records())

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

    def _render_actions(self, actions: Sequence[Action], record: Any | None, **ctx: Any) -> str:
        parts: list[str] = []
        for action in actions:
            if record is not None:
                parts.append(action.render(record, record=record, **ctx))
            else:
                parts.append(action.render(**ctx))
        return "".join(parts)

    def _header_label(self, col: Column | LayoutComponent, **ctx: Any) -> str:
        label = col.get_label(**ctx)
        if label:
            return label
        if isinstance(col, LayoutComponent):
            for child in col.flat_columns():
                child_label = child.get_label(**ctx)
                if child_label:
                    return str(child_label)
        return col.get_name() or ""

    def _render_filter_chrome(self, **ctx: Any) -> str:
        if not self._filters and self._query_builder is None:
            return ""
        attrs = []
        if self._persist_filters_in_session:
            key = self._filters_session_key or (self.get_name() or "table")
            attrs.append(f'data-filters-session="{e(key)}"')
        if self._defer_filters:
            attrs.append('data-defer-filters="true"')
        attr_s = (" " + " ".join(attrs)) if attrs else ""
        parts: list[str] = []
        for f in self._filters:
            name = e(f.get_name() or "")
            label = e(f.get_label(**ctx) or name)
            opts = f.get_options(**ctx)
            options_html = "".join(
                f'<option value="{e(k)}">{e(v)}</option>' for k, v in opts.items()
            )
            current = self._filter_state.get(f.get_name() or "")
            selected = "" if current in (None, "") else str(current)
            # mark selected
            if selected:
                options_html = "".join(
                    f'<option value="{e(k)}"'
                    f'{" selected" if str(k) == selected else ""}>{e(v)}</option>'
                    for k, v in opts.items()
                )
            parts.append(
                f'<div class="or-table-filter" data-filter="{name}">'
                f'<label class="or-filter-label">{label}</label>'
                f'<select class="or-select or-filter-select" name="filters.{name}" '
                f'wire:model="tableFilters.{name}">{options_html}</select></div>'
            )
        qb_html = ""
        if self._query_builder is not None and hasattr(self._query_builder, "render"):
            qb_html = self._query_builder.render(**ctx)
        apply_btn = ""
        if self._defer_filters:
            apply_btn = (
                '<button type="button" class="or-btn or-btn-primary or-filter-apply" '
                'wire:click="applyTableFilters">Apply</button>'
            )
        return (
            f'<div class="or-table-filters"{attr_s}>'
            f'<div class="or-table-filters-row">{"".join(parts)}</div>'
            f"{qb_html}{apply_btn}</div>"
        )

    def _render_summary_cells(
        self,
        display: list[Column | LayoutComponent],
        records: Sequence[Any],
        *,
        scope: str,
        has_actions: bool,
        **ctx: Any,
    ) -> str:
        cells: list[str] = []
        any_summary = False
        for col in display:
            if isinstance(col, Column) and col.get_summarizers():
                any_summary = True
                inner = "".join(
                    s.render(
                        records=records,
                        attribute=col.get_name(),
                        **ctx,
                    )
                    for s in col.get_summarizers()
                )
                cells.append(f'<td class="or-td or-td-summary" data-summary-scope="{e(scope)}">{inner}</td>')
            else:
                cells.append(f'<td class="or-td or-td-summary" data-summary-scope="{e(scope)}"></td>')
        if not any_summary:
            return ""
        if has_actions:
            cells.append(f'<td class="or-td or-td-summary" data-summary-scope="{e(scope)}"></td>')
        return f'<tr class="or-tr or-summary-row" data-summary-scope="{e(scope)}">{"".join(cells)}</tr>'

    def _render_row(
        self,
        record: Any,
        display: list[Column | LayoutComponent],
        **ctx: Any,
    ) -> str:
        cells = "".join(c.render_cell(record, **ctx) for c in display)
        if self._actions:
            acts = self._render_actions(self._actions, record, **ctx)
            cells += f'<td class="or-td or-td-actions">{acts}</td>'
        return f'<tr class="or-tr">{cells}</tr>'

    def to_dict(self) -> dict[str, Any]:
        return {
            "columns": [c.to_dict() for c in self.flat_columns()],
            "filters": [f.to_dict() for f in self._filters],
            "actions": [a.to_dict() for a in self._actions],
            "bulk_actions": [a.to_dict() for a in self._bulk_actions],
            "total": self.get_total(),
            "page": self._page,
            "per_page": self._per_page,
            "groups_only": self._groups_only,
            "persist_filters": self._persist_filters_in_session,
            "defer_filters": self._defer_filters,
            "content_grid": self._content_grid,
        }

    def render(self, state: Any = None, **ctx: Any) -> str:
        page_records = self.get_records()
        all_records = self.get_all_filtered_records()
        display = self.display_columns()
        flat = self.flat_columns()
        has_actions = bool(self._actions)
        colspan = len(display) + (1 if has_actions else 0)

        header_cells: list[str] = []
        for col in self._columns:
            if isinstance(col, ColumnGroup):
                span = len(col.get_columns())
                header_cells.append(
                    f'<th class="or-th or-th-group" colspan="{span}">'
                    f'{e(col.get_label(**ctx))}</th>'
                )
            elif isinstance(col, LayoutComponent):
                header_cells.append(
                    f'<th class="or-th or-th-layout">{e(self._header_label(col, **ctx))}</th>'
                )
            else:
                sortable = getattr(col, "is_sortable", lambda: False)()
                header_cells.append(
                    f'<th class="or-th" data-sortable="{str(sortable).lower()}">'
                    f'{e(col.get_label(**ctx))}</th>'
                )
        headers = "".join(header_cells)
        if has_actions:
            headers += '<th class="or-th or-th-actions">Actions</th>'

        active_group = self._default_group
        if active_group is None and self._groups:
            active_group = self._groups[0]

        rows: list[str] = []
        if active_group is not None and page_records:
            collapsed = self._collapsed_groups_by_default
            for bucket in active_group.partition(page_records):
                rows.append(
                    active_group.render_header(
                        bucket,
                        colspan=colspan,
                        collapsed=collapsed,
                        **ctx,
                    )
                )
                if not self._groups_only:
                    for record in bucket.records:
                        rows.append(self._render_row(record, display, **ctx))
                group_summary = self._render_summary_cells(
                    display,
                    bucket.records,
                    scope="group",
                    has_actions=has_actions,
                    **ctx,
                )
                if group_summary:
                    rows.append(group_summary)
        else:
            for record in page_records:
                rows.append(self._render_row(record, display, **ctx))

        body = "".join(rows) or (
            f'<tr class="or-tr"><td class="or-td or-empty" colspan="{colspan}">'
            f'<div class="or-empty-state"><h3>{e(self._empty_state_heading)}</h3>'
            f'{f"<p>{e(self._empty_state_description)}</p>" if self._empty_state_description else ""}'
            f"</div></td></tr>"
        )

        footer_parts: list[str] = []
        page_foot = self._render_summary_cells(
            display, page_records, scope="page", has_actions=has_actions, **ctx
        )
        all_foot = self._render_summary_cells(
            display, all_records, scope="all", has_actions=has_actions, **ctx
        )
        if page_foot:
            footer_parts.append(page_foot)
        if all_foot and all_records != page_records:
            footer_parts.append(all_foot)
        elif all_foot and not page_foot:
            footer_parts.append(all_foot)
        # When page == all, still show one summary row
        if all_foot and page_foot and all_records == page_records:
            footer_parts = [all_foot]
        tfoot = (
            f'<tfoot class="or-tfoot">{"".join(footer_parts)}</tfoot>' if footer_parts else ""
        )

        striped = " or-table-striped" if self._striped else ""
        grid_attr = ""
        wrap_extra = ""
        if self._content_grid:
            cols = self._content_grid.get("columns", 2)
            grid_attr = f' data-content-grid="{e(cols)}"'
            wrap_extra = " or-table-content-grid"

        header_bar = ""
        if self._header_actions:
            header_bar = (
                f'<div class="or-table-header-actions">'
                f'{self._render_actions(self._header_actions, None, **ctx)}</div>'
            )
        bulk_bar = ""
        if self._bulk_actions:
            bulk_bar = (
                f'<div class="or-table-bulk-actions">'
                f'{self._render_actions(self._bulk_actions, None, **ctx)}</div>'
            )
        groups_chooser = ""
        if self._groups:
            opts = "".join(
                f'<option value="{e(g.get_name() or "")}">{e(g.get_label(**ctx) or g.get_name())}</option>'
                for g in self._groups
            )
            groups_chooser = (
                f'<div class="or-table-groups-chooser">'
                f'<select class="or-select" wire:model="tableGroup">{opts}</select></div>'
            )

        # silence unused flat when only used for search — keep referenced
        _ = flat

        return (
            f'<div class="or-table-wrap{wrap_extra}"{grid_attr}>'
            f"{header_bar}{bulk_bar}{groups_chooser}"
            f"{self._render_filter_chrome(**ctx)}"
            f'<table class="or-table{striped}">'
            f'<thead class="or-thead"><tr>{headers}</tr></thead>'
            f'<tbody class="or-tbody">{body}</tbody>'
            f"{tfoot}</table></div>"
        )
