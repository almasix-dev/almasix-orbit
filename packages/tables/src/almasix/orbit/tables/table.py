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
        self._stacked_on_mobile: bool = True
        self._layout: str = "table"
        self._kanban_status: str | None = None

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

    def stacked_on_mobile(self, condition: bool = True) -> Self:
        """Below ``md``, render each row as a label/value card (Filament parity)."""
        self._stacked_on_mobile = condition
        return self

    def layout(self, mode: str) -> Self:
        """``table`` (default), ``grid`` (content_grid), or ``kanban``."""
        self._layout = mode
        if mode == "grid" and self._content_grid is None:
            self._content_grid = {"md": 2, "xl": 3}
        return self

    def kanban_status(self, attribute: str) -> Self:
        self._kanban_status = attribute
        self._layout = "kanban"
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
        if ctx.get("has_bulk"):
            cells.append('<td class="or-td or-td-summary" data-summary-scope="' + e(scope) + '"></td>')
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
        select = ""
        if ctx.get("has_bulk"):
            rid = e(str(self._record_value(record, "id") or id(record)))
            select = (
                f'<td class="or-td or-td-select">'
                f'<input type="checkbox" class="or-row-check" data-record-id="{rid}" '
                f'@change="toggle(\'{rid}\', $event.target.checked)" '
                f'aria-label="Select row" /></td>'
            )
        cells = select + "".join(c.render_cell(record, **ctx) for c in display)
        if self._actions:
            acts = self._render_actions(self._actions, record, **ctx)
            cells += f'<td class="or-td or-td-actions"><div class="or-row-actions">{acts}</div></td>'
        return f'<tr class="or-tr or-list-row">{cells}</tr>'

    def _render_record_card(self, record: Any, display: list[Column | LayoutComponent], **ctx: Any) -> str:
        fields: list[str] = []
        for col in display:
            label = e(self._header_label(col, **ctx))
            if isinstance(col, Column):
                cell = col.render_cell(record, **ctx)
                # strip td wrapper if present
                if cell.startswith("<td"):
                    inner = cell[cell.find(">") + 1 : cell.rfind("</td>")]
                else:
                    inner = cell
            else:
                inner = col.render_cell(record, **ctx) if hasattr(col, "render_cell") else ""
            fields.append(
                f'<div class="or-table-field"><span class="or-table-field-label">{label}</span>'
                f'<div class="or-table-field-value">{inner}</div></div>'
            )
        footer = ""
        if self._actions:
            footer = (
                f'<div class="or-table-record-card-actions">'
                f"{self._render_actions(self._actions, record, **ctx)}</div>"
            )
        return (
            f'<article class="or-table-record-card or-card">'
            f'<div class="or-table-record-card-body">{"".join(fields)}</div>{footer}</article>'
        )

    def _render_stacked_cards(
        self, records: Sequence[Any], display: list[Column | LayoutComponent], **ctx: Any
    ) -> str:
        if not self._stacked_on_mobile or self._layout == "kanban" or self._groups_only:
            return ""
        cards = "".join(self._render_record_card(r, display, **ctx) for r in records)
        return f'<div class="or-table-stacked" aria-hidden="false">{cards}</div>'

    def _render_kanban(self, records: Sequence[Any], display: list[Column | LayoutComponent], **ctx: Any) -> str:
        attr = self._kanban_status or "status"
        buckets: dict[str, list[Any]] = {}
        for record in records:
            key = str(self._record_value(record, attr) or "Unset")
            buckets.setdefault(key, []).append(record)
        cols = []
        for status, items in buckets.items():
            cards = "".join(self._render_record_card(r, display, **ctx) for r in items)
            cols.append(
                f'<div class="or-kanban-column" data-status="{e(status)}">'
                f'<h3 class="or-kanban-column-title">{e(status)}</h3>'
                f'<div class="or-kanban-column-body">{cards}</div></div>'
            )
        return f'<div class="or-kanban" data-status-attr="{e(attr)}">{"".join(cols)}</div>'

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
            "stacked_on_mobile": self._stacked_on_mobile,
            "layout": self._layout,
            "kanban_status": self._kanban_status,
        }

    def render(self, state: Any = None, **ctx: Any) -> str:
        skip_header_actions = bool(ctx.pop("skip_header_actions", False))
        page_records = self.get_records()
        all_records = self.get_all_filtered_records()
        display = self.display_columns()
        flat = self.flat_columns()
        has_actions = bool(self._actions)
        has_bulk = bool(self._bulk_actions)
        colspan = len(display) + (1 if has_actions else 0) + (1 if has_bulk else 0)
        row_ctx = {**ctx, "has_bulk": has_bulk}

        header_cells: list[str] = []
        if has_bulk:
            header_cells.append(
                '<th class="or-th or-th-select">'
                '<input type="checkbox" class="or-row-check" '
                '@change="toggleAll($event.target.checked)" '
                ':checked="pageFullySelected" '
                'aria-label="Select all on page" /></th>'
            )
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
                        rows.append(self._render_row(record, display, **row_ctx))
                group_summary = self._render_summary_cells(
                    display,
                    bucket.records,
                    scope="group",
                    has_actions=has_actions,
                    has_bulk=has_bulk,
                    **ctx,
                )
                if group_summary:
                    rows.append(group_summary)
        else:
            for record in page_records:
                rows.append(self._render_row(record, display, **row_ctx))

        body = "".join(rows) or (
            f'<tr class="or-tr"><td class="or-td or-empty" colspan="{colspan}">'
            f'<div class="or-empty-state"><h3>{e(self._empty_state_heading)}</h3>'
            f'{f"<p>{e(self._empty_state_description)}</p>" if self._empty_state_description else ""}'
            f"</div></td></tr>"
        )

        footer_parts: list[str] = []
        page_foot = self._render_summary_cells(
            display, page_records, scope="page", has_actions=has_actions, has_bulk=has_bulk, **ctx
        )
        all_foot = self._render_summary_cells(
            display, all_records, scope="all", has_actions=has_actions, has_bulk=has_bulk, **ctx
        )
        if page_foot:
            footer_parts.append(page_foot)
        if all_foot and all_records != page_records:
            footer_parts.append(all_foot)
        elif all_foot and not page_foot:
            footer_parts.append(all_foot)
        if all_foot and page_foot and all_records == page_records:
            footer_parts = [all_foot]
        tfoot = (
            f'<tfoot class="or-tfoot">{"".join(footer_parts)}</tfoot>' if footer_parts else ""
        )

        striped = " or-table-striped" if self._striped else ""
        grid_attr = ""
        wrap_extra = ""
        if self._content_grid or self._layout == "grid":
            grid = self._content_grid or {"md": 2, "xl": 3}
            cols = grid.get("columns") or grid.get("md") or 2
            grid_attr = f' data-content-grid="{e(cols)}"'
            for bp in ("sm", "md", "lg", "xl", "2xl"):
                if bp in grid:
                    grid_attr += f' data-grid-{bp}="{e(grid[bp])}"'
            wrap_extra = " or-table-content-grid"

        toolbar_end = ""
        if self._header_actions and not skip_header_actions:
            toolbar_end += (
                f'<div class="or-list-toolbar-actions">'
                f'{self._render_actions(self._header_actions, None, **ctx)}</div>'
            )
        groups_chooser = ""
        if self._groups:
            opts = "".join(
                f'<option value="{e(g.get_name() or "")}">'
                f'{e(g.get_label(**ctx) or g.get_name())}</option>'
                for g in self._groups
            )
            groups_chooser = (
                f'<div class="or-table-groups-chooser">'
                f'<label class="or-filter-label">Group</label>'
                f'<select class="or-select or-select-sm" wire:model="tableGroup">{opts}</select></div>'
            )

        filters = self._render_filter_chrome(**ctx)
        toolbar = ""
        if filters or toolbar_end or groups_chooser:
            toolbar = (
                f'<div class="or-list-toolbar">'
                f'<div class="or-list-toolbar-start">{filters}{groups_chooser}</div>'
                f'<div class="or-list-toolbar-end">{toolbar_end}</div>'
                f"</div>"
            )

        bulk_bar = ""
        if self._bulk_actions:
            bulk_bar = (
                '<div class="or-list-bulk or-table-bulk-actions" '
                'x-show="selected.length > 0" x-cloak>'
                '<span class="or-list-bulk-label">'
                '<span x-text="selected.length"></span> selected</span>'
                f'<div class="or-list-bulk-actions">'
                f'{self._render_actions(self._bulk_actions, None, **ctx)}</div>'
                '<button type="button" class="or-btn or-btn-ghost or-btn-sm" @click="clear()">'
                "Clear</button></div>"
            )

        _ = flat
        stacked = self._render_stacked_cards(page_records, display, **ctx)
        stacked_cls = " or-table-has-stacked" if stacked else ""
        selection_attr = ' x-data="orbitTableSelection"' if has_bulk else ""

        if self._layout == "kanban":
            return (
                f'<div class="or-table-wrap or-list-card or-table-kanban">'
                f"{toolbar}{self._render_kanban(page_records, display, **ctx)}</div>"
            )

        return (
            f'<div class="or-table-wrap or-list-card{wrap_extra}{stacked_cls}"'
            f"{grid_attr}{selection_attr}>"
            f"{toolbar}{bulk_bar}"
            f'<div class="or-list-table-scroll or-table-desktop">'
            f'<table class="or-table{striped}">'
            f'<thead class="or-thead"><tr>{headers}</tr></thead>'
            f'<tbody class="or-tbody">{body}</tbody>'
            f"{tfoot}</table></div>"
            f"{stacked}</div>"
        )
