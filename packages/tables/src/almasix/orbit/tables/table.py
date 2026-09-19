"""Table builder."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import Any, ClassVar, Self

from almasix.orbit.actions.action import Action
from almasix.orbit.support.component import Component
from almasix.orbit.support.conduit_attrs import conduit_attr
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e
from almasix.orbit.tables.columns import Column, ColumnGroup, dot_get
from almasix.orbit.tables.enums import PaginationMode
from almasix.orbit.tables.filters import Filter
from almasix.orbit.tables.grouping import Group
from almasix.orbit.tables.layout import LayoutComponent

ColumnLike = Column | ColumnGroup | LayoutComponent


def _conduit_click(expression: str) -> str:
    """Emit click handlers without escaping ``'`` inside double-quoted attributes."""
    safe = str(expression).replace("&", "&amp;").replace('"', "&quot;")
    return f' conduit:click="{safe}" wire:click="{safe}"'


def _alpine_wire_call(method_call: str, *, event: str = "change") -> str:
    """Call a Conduit/Livewire host method from Alpine (Conduit has no wire:change calls)."""
    safe = (
        str(method_call)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
    )
    return f' @{event}="orbitWire($el)?.{safe}"'


def _pagination_pages(page: int, last: int) -> list[int | None]:
    """Filament-style page window: first, last, current±2, with ``None`` ellipsis."""
    if last <= 1:
        return [1] if last == 1 else []
    if last <= 7:
        return list(range(1, last + 1))
    window = {1, last}
    for p in range(page - 2, page + 3):
        if 1 <= p <= last:
            window.add(p)
    ordered = sorted(window)
    out: list[int | None] = []
    prev: int | None = None
    for p in ordered:
        if prev is not None and p > prev + 1:
            out.append(None)
        out.append(p)
        prev = p
    return out


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
        self._empty_state_actions: list[Action] = []
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
        self._summaries_page = True
        self._summaries_all = True
        self._actions_as_dropdown = True
        self._toggled_columns: dict[str, bool] | None = None
        self._active_group_name: str | None = None
        self._default_sort: str | None = None
        self._default_sort_direction: str = "asc"
        self._pagination_page_options: list[int | str] = [5, 10, 25, 50]
        self._extreme_pagination_links = False
        self._pagination_mode: PaginationMode = PaginationMode.DEFAULT
        self._persist_records_per_page_in_session = False
        self._persist_search_in_session = False
        self._persist_sort_in_session = False
        self._persist_columns_in_session = True
        self._query_string_identifier: str | None = None
        self._open_record_url_in_new_tab = False
        self._reorderable_column: str | None = None
        self._reorderable_enabled = False
        self._reorderable_direction: str = "asc"
        self._paginated_while_reordering = False
        self._before_reordering: Callable[..., None] | None = None
        self._after_reordering: Callable[..., None] | None = None
        self._reorder_records_trigger: Callable[..., Any] | None = None
        self._heading: str | None = None
        self._description: str | None = None
        self._header_html: Callable[..., str] | str | None = None
        self._poll: str | None = None
        self._defer_loading = False
        self._table_searchable = False
        self._search_using: Callable[..., Any] | None = None
        self._record_classes: Callable[..., Any] | str | list[str] | None = None
        self._empty_state_icon: str | None = None
        self._empty_state_view: Callable[..., str] | str | None = None

    _configure_using: ClassVar[list[Callable[[Table], None]]] = []

    @classmethod
    def configure_using(cls, callback: Callable[[Table], None]) -> None:
        """Register a default configurator (Filament ``Table::configureUsing``)."""
        cls._configure_using.append(callback)

    @classmethod
    def make(cls, name: str | None = "table") -> Self:
        instance = cls() if name is None else cls(name)
        for callback in cls._configure_using:
            callback(instance)
        return instance

    def columns(self, columns: Sequence[ColumnLike]) -> Self:
        self._columns = list(columns)
        return self

    def push_columns(self, columns: Sequence[ColumnLike]) -> Self:
        """Append columns without replacing the existing configuration."""
        self._columns.extend(list(columns))
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

    def record_actions(self, actions: Sequence[Action]) -> Self:
        """Filament v5 alias for :meth:`actions` (per-row actions)."""
        return self.actions(actions)

    def actions_as_dropdown(self, condition: bool = True) -> Self:
        """When True (default), wrap flat row actions in a ⋮ dropdown."""
        self._actions_as_dropdown = condition
        return self

    def bulk_actions(self, actions: Sequence[Action]) -> Self:
        self._bulk_actions = list(actions)
        return self

    def toolbar_actions(self, actions: Sequence[Action]) -> Self:
        """Filament v5 alias — toolbar bulk selection actions."""
        return self.bulk_actions(actions)

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

    def open_record_url_in_new_tab(self, condition: bool = True) -> Self:
        self._open_record_url_in_new_tab = condition
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

    def summaries(self, *, page: bool = True, all: bool = True) -> Self:
        """Toggle page vs all-table summary footer rows (Filament ``->summaries``)."""
        self._summaries_page = page
        self._summaries_all = all
        return self

    def toggled_columns(self, state: dict[str, bool] | None) -> Self:
        """Map of column name → visible. ``None`` uses column defaults."""
        self._toggled_columns = None if state is None else dict(state)
        return self

    def active_group(self, name: str | None) -> Self:
        self._active_group_name = name
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
                for child in col.get_columns():
                    if self._column_is_visible(child):
                        out.append(child)
            elif isinstance(col, Column):
                if self._column_is_visible(col):
                    out.append(col)
            elif isinstance(col, LayoutComponent):
                out.append(col)
        return out

    def _column_is_visible(self, col: Column) -> bool:
        name = col.get_name() or ""
        if self._toggled_columns is not None and name in self._toggled_columns:
            return bool(self._toggled_columns[name])
        if col.is_toggleable() and col.is_toggled_hidden_by_default():
            return False
        return True

    def _toggleable_columns(self) -> list[Column]:
        return [c for c in self.flat_columns() if c.is_toggleable() and c.get_name()]

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
            if self._search_using is not None:
                try:
                    records = list(self._search_using(records, self._search))
                except TypeError:
                    records = list(self._search_using(records, search=self._search))
            else:
                records = [r for r in records if self._record_matches_search(r)]
        sort_col = self._sort or self._default_sort
        sort_dir = self._sort_direction if self._sort else self._default_sort_direction
        if sort_col:
            reverse = sort_dir == "desc"
            col_map = {c.get_name(): c for c in self.flat_columns() if c.get_name()}
            column = col_map.get(sort_col)

            def _sort_key(record: Any) -> Any:
                if column is not None:
                    value = column.resolve_state(record)
                else:
                    value = self._record_value(record, sort_col)
                return "" if value is None else value

            records = sorted(records, key=_sort_key, reverse=reverse)
        return records

    def get_records(self) -> list[Any]:
        records = self._filtered_records()
        reordering = bool(getattr(self, "_is_reordering", False))
        if reordering and not self._paginated_while_reordering:
            return records
        if self._paginated and self._per_page > 0:
            total = len(records)
            max_page = max(1, (total + self._per_page - 1) // self._per_page) if total else 1
            if self._page > max_page:
                self._page = max_page
            start = (self._page - 1) * self._per_page
            return records[start : start + self._per_page]
        return records

    def get_all_filtered_records(self) -> list[Any]:
        return self._filtered_records()

    def get_total(self) -> int:
        return len(self._filtered_records())

    def pagination_meta(self) -> dict[str, int]:
        """Page window metadata for chrome (clamps ``_page`` like :meth:`get_records`)."""
        total = self.get_total()
        if not self._paginated or self._per_page <= 0:
            return {
                "total": total,
                "page": 1,
                "per_page": total or 1,
                "last_page": 1,
                "from": 1 if total else 0,
                "to": total,
            }
        per_page = max(1, self._per_page)
        last_page = max(1, (total + per_page - 1) // per_page) if total else 1
        page = min(max(1, self._page), last_page)
        self._page = page
        start = (page - 1) * per_page
        end = min(start + per_page, total)
        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "last_page": last_page,
            "from": (start + 1) if total else 0,
            "to": end,
        }

    def has_searchable_columns(self) -> bool:
        return self._table_searchable or any(c.is_searchable() for c in self.flat_columns())

    def searchable(self, condition: bool = True) -> Self:
        """Show the search field even when no column is marked searchable."""
        self._table_searchable = condition
        return self

    def search_using(self, callback: Callable[..., Any]) -> Self:
        """Custom search: ``callback(records, search) -> records``."""
        self._search_using = callback
        return self

    def search(self, term: str) -> Self:
        self._search = term
        return self

    def sort(self, column: str, direction: str = "asc") -> Self:
        self._sort = column
        self._sort_direction = direction
        return self

    def default_sort(self, column: str, direction: str = "asc") -> Self:
        """Initial sort until the user picks another column."""
        self._default_sort = column
        self._default_sort_direction = direction
        if self._sort is None:
            self._sort = column
            self._sort_direction = direction
        return self

    def paginate(self, page: int = 1, per_page: int = 10) -> Self:
        self._page = page
        self._per_page = int(per_page) if per_page != "all" else 0
        self._paginated = True
        return self

    def paginated(self, options: bool | Sequence[int | str] = True) -> Self:
        """Enable/disable pagination, or set per-page select options (incl. ``"all"``)."""
        if options is False:
            self._paginated = False
            return self
        self._paginated = True
        if options is not True:
            self._pagination_page_options = list(options)
        return self

    def pagination_page_options(self, options: Sequence[int | str]) -> Self:
        self._pagination_page_options = list(options)
        return self

    def default_pagination_page_option(self, option: int | str) -> Self:
        if option == "all":
            self._per_page = 0
        else:
            self._per_page = int(option)
        return self

    def extreme_pagination_links(self, condition: bool = True) -> Self:
        self._extreme_pagination_links = condition
        return self

    def pagination_mode(self, mode: PaginationMode | str) -> Self:
        self._pagination_mode = PaginationMode(mode)
        return self

    def persist_records_per_page_in_session(self, condition: bool = True) -> Self:
        self._persist_records_per_page_in_session = condition
        return self

    def query_string_identifier(self, identifier: str) -> Self:
        self._query_string_identifier = identifier
        return self

    def persist_search_in_session(self, condition: bool = True) -> Self:
        self._persist_search_in_session = condition
        return self

    def persist_sort_in_session(self, condition: bool = True) -> Self:
        self._persist_sort_in_session = condition
        return self

    def persist_column_searches_in_session(self, condition: bool = True) -> Self:
        # Alias kept for Filament naming; Orbit uses column manager persist flag.
        self._persist_columns_in_session = condition
        return self

    def persist_in_session(self, condition: bool = True) -> Self:
        """Toggle filters/search/sort/columns/per-page session persistence together."""
        self.persist_filters_in_session(condition)
        self._persist_search_in_session = condition
        self._persist_sort_in_session = condition
        self._persist_columns_in_session = condition
        self._persist_records_per_page_in_session = condition
        return self

    def empty_state_heading(self, text: str) -> Self:
        self._empty_state_heading = text
        return self

    def empty_state_description(self, text: str) -> Self:
        self._empty_state_description = text
        return self

    def empty_state_actions(self, actions: Sequence[Action]) -> Self:
        self._empty_state_actions = list(actions)
        return self

    def empty_state_icon(self, icon: str) -> Self:
        self._empty_state_icon = icon
        return self

    def empty_state(self, view: Callable[..., str] | str) -> Self:
        """Replace the default empty-state markup with custom HTML or a callable."""
        self._empty_state_view = view
        return self

    def striped(self, condition: bool = True) -> Self:
        self._striped = condition
        return self

    def heading(self, text: str) -> Self:
        self._heading = text
        return self

    def description(self, text: str) -> Self:
        self._description = text
        return self

    def header(self, view: Callable[..., str] | str) -> Self:
        """Custom header HTML (callable receives ``**ctx``)."""
        self._header_html = view
        return self

    def poll(self, interval: str | None = "10s") -> Self:
        self._poll = interval
        return self

    def defer_loading(self, condition: bool = True) -> Self:
        self._defer_loading = condition
        return self

    def record_classes(
        self, classes: Callable[..., Any] | str | list[str] | None
    ) -> Self:
        self._record_classes = classes
        return self

    def reorderable(
        self,
        column: str | None = "sort",
        condition: bool = True,
        *,
        direction: str = "asc",
    ) -> Self:
        self._reorderable_column = column
        self._reorderable_enabled = bool(condition) and column is not None
        self._reorderable_direction = direction
        return self

    def paginated_while_reordering(self, condition: bool = True) -> Self:
        self._paginated_while_reordering = condition
        return self

    def before_reordering(self, callback: Callable[..., None]) -> Self:
        self._before_reordering = callback
        return self

    def after_reordering(self, callback: Callable[..., None]) -> Self:
        self._after_reordering = callback
        return self

    def reorder_records_trigger_action(self, callback: Callable[..., Any]) -> Self:
        self._reorder_records_trigger = callback
        return self

    def apply_reorder(self, order: Sequence[Any]) -> None:
        """Apply a new record order (keys/ids); runs before/after hooks."""
        keys = list(order)
        if self._before_reordering:
            self._before_reordering(keys)
        # Soft reorder of in-memory records when ids match.
        if self._records and keys:
            by_id: dict[str, Any] = {}
            for record in self._records:
                rid = str(self._record_value(record, "id") or id(record))
                by_id[rid] = record
            reordered = [by_id[str(k)] for k in keys if str(k) in by_id]
            leftovers = [r for r in self._records if r not in reordered]
            self._records = [*reordered, *leftovers]
        if self._after_reordering:
            self._after_reordering(keys)

    def _record_value(self, record: Any, key: str) -> Any:
        value = dot_get(record, key) if key else None
        return "" if value is None else value

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
        from almasix.orbit.actions.presets import ActionGroup

        resolved: list[Action] = list(actions)
        if (
            record is not None
            and self._actions_as_dropdown
            and resolved
            and not any(isinstance(a, ActionGroup) for a in resolved)
        ):
            group = (
                ActionGroup.make(resolved)
                .icon("heroicon-o-ellipsis-vertical")
                .label("Actions")
                .color("gray")
                .icon_button()
            )
            resolved = [group]
        parts: list[str] = []
        for action in resolved:
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
        from almasix.orbit.support.icons import icon as render_icon

        attrs = []
        if self._persist_filters_in_session:
            key = self._filters_session_key or (self.get_name() or "table")
            attrs.append(f'data-filters-session="{e(key)}"')
        if self._defer_filters:
            attrs.append('data-defer-filters="true"')
        active_count = sum(
            1
            for f in self._filters
            if (f.get_name() or "")
            and self._filter_state.get(f.get_name() or "") not in (None, "", [])
        )
        attrs.append(f'data-active-count="{active_count}"')
        attrs.append(f'data-pending="{e(json.dumps(dict(self._filter_state)))}"')
        attr_s = (" " + " ".join(attrs)) if attrs else ""
        parts: list[str] = []
        for f in self._filters:
            name = f.get_name() or ""
            name_e = e(name)
            label = e(f.get_label(**ctx) or name)
            opts = f.get_options(**ctx)
            current = self._filter_state.get(name)
            selected = "" if current in (None, "") else str(current)
            blank = '<option value="">All</option>' if "" not in {str(k) for k in opts} else ""
            options_html = blank + "".join(
                f'<option value="{e(k)}"'
                f'{" selected" if selected and str(k) == selected else ""}>{e(v)}</option>'
                for k, v in opts.items()
            )
            if self._defer_filters:
                change = (
                    ' @change="pending[\''
                    + name.replace("'", "\\'")
                    + '\'] = $event.target.value"'
                )
            else:
                change = _alpine_wire_call(
                    "setTableFilter('" + name.replace("'", "\\'") + "', $event.target.value)"
                )
            parts.append(
                f'<div class="or-table-filter" data-filter="{name_e}">'
                f'<label class="or-filter-label">{label}</label>'
                f'<select class="or-select or-filter-select" name="filters.{name_e}"'
                f' data-filter-name="{name_e}"{change}>{options_html}</select></div>'
            )
        qb_html = ""
        if self._query_builder is not None and hasattr(self._query_builder, "render"):
            qb_html = self._query_builder.render(**ctx)
        # Filament-style panel: Filters + Reset header; Apply filters when deferred.
        reset_btn = (
            f'<button type="button" class="or-link-btn or-link-danger or-filters-reset"'
            f'{_conduit_click("resetTableFilters")} @click="closeFilters()">Reset</button>'
        )
        if self._defer_filters:
            footer = (
                '<div class="or-filters-panel-footer">'
                '<button type="button" class="or-btn or-btn-primary or-btn-sm or-filter-apply"'
                ' @click="applyDeferred()">Apply filters</button></div>'
            )
        else:
            footer = ""
        funnel = render_icon("heroicon-o-funnel", size=20)
        return (
            f'<div class="or-table-filters" x-data="orbitTableFilters"{attr_s} '
            f'@click.outside="closeFilters()">'
            f'<button type="button" class="or-icon-btn or-filters-trigger" '
            f'@click="toggleFilters($event)" aria-haspopup="true" aria-label="Filter" '
            f':aria-expanded="filtersOpen.toString()">'
            f"{funnel}"
            f'<span class="or-filters-badge" x-text="activeCount" '
            f':class="activeCount > 0 ? \'or-filters-badge-active\' : \'\'"></span>'
            f"</button>"
            f'<div class="or-filters-panel" x-show="filtersOpen" x-cloak '
            f'role="dialog" aria-label="Filters">'
            f'<div class="or-filters-panel-header">'
            f'<h3 class="or-filters-panel-title">Filters</h3>{reset_btn}</div>'
            f'<div class="or-table-filters-row">{"".join(parts)}</div>'
            f"{qb_html}{footer}</div></div>"
        )

    def _render_filter_indicators(self, **ctx: Any) -> str:
        chips: list[str] = []
        for f in self._filters:
            if not getattr(f, "_indicate", True):
                continue
            name = f.get_name() or ""
            if not name:
                continue
            value = self._filter_state.get(name)
            if value in (None, "", []):
                continue
            opts = f.get_options(**ctx)
            display = opts.get(value, opts.get(str(value), value))
            label = f.get_label(**ctx) or name
            click = _conduit_click("removeTableFilter('" + name + "')")
            chips.append(
                f'<button type="button" class="or-filter-chip"'
                f"{click}"
                f' aria-label="Remove {e(label)} filter">'
                f'<span class="or-filter-chip-label">{e(label)}:</span> '
                f'<span class="or-filter-chip-value">{e(display)}</span>'
                f'<span class="or-filter-chip-x" aria-hidden="true">×</span></button>'
            )
        if not chips:
            return ""
        reset = (
            f'<button type="button" class="or-btn or-btn-ghost or-btn-sm or-filter-reset"'
            f'{_conduit_click("resetTableFilters")}>Reset filters</button>'
        )
        return (
            f'<div class="or-table-filter-indicators" role="list">'
            f'{"".join(chips)}{reset}</div>'
        )

    def _render_search_chrome(self, **ctx: Any) -> str:
        if not self.has_searchable_columns():
            return ""
        value = e(self._search)
        clear = ""
        if self._search:
            clear = (
                f'<button type="button" class="or-table-search-clear or-btn or-btn-ghost or-btn-sm"'
                f'{conduit_attr("click", "clearSearch")} aria-label="Clear search">Clear</button>'
            )
        attrs = ""
        if self._persist_search_in_session:
            attrs += ' data-persist-search="true"'
        return (
            f'<div class="or-table-search"{attrs}>'
            f'<label class="or-sr-only" for="or-table-search-input">Search</label>'
            f'<input id="or-table-search-input" type="search" class="or-input or-table-search-input" '
            f'placeholder="Search…" value="{value}" autocomplete="off"'
            f'{_alpine_wire_call("setTableSearch($event.target.value)", event="input.debounce.300ms")} />'
            f"{clear}</div>"
        )

    def _render_sort_header(self, col: Column, **ctx: Any) -> str:
        from almasix.orbit.support.icons import icon as render_icon

        label = e(col.get_label(**ctx) or self._header_label(col, **ctx))
        name = col.get_name() or ""
        align = col.get_alignment() if isinstance(col, Column) else "start"
        align_c = f" or-align-{align}" if align and align != "start" else ""
        bp = ""
        if col._visible_from:
            bp += f" or-visible-from-{col._visible_from}"
        if col._hidden_from:
            bp += f" or-hidden-from-{col._hidden_from}"
        if not col.is_sortable() or not name:
            return f'<th class="or-th{align_c}{bp}">{label}</th>'
        active = self._sort == name
        direction = str(self._sort_direction or "asc").lower()
        classes = f"or-th or-th-sortable{align_c}{bp}"
        aria_sort = "none"
        # Filament: idle + desc → chevron-down; active asc → chevron-up.
        if active and direction == "asc":
            caret = render_icon("heroicon-o-chevron-up", size=16, css_class="or-icon or-th-sort-icon")
        else:
            caret = render_icon("heroicon-o-chevron-down", size=16, css_class="or-icon or-th-sort-icon")
        icon_cls = "or-th-sort-icon-wrap"
        if active:
            classes += f" or-th-sorted or-th-sorted-{direction}"
            icon_cls += " or-th-sort-icon-active"
            aria_sort = "ascending" if direction != "desc" else "descending"
        click = _conduit_click(f"sortBy('{name}')")
        return (
            f'<th class="{classes}" data-sortable="true" data-sort-column="{e(name)}" '
            f'aria-sort="{aria_sort}">'
            f'<button type="button" class="or-th-sort-btn"{click}>'
            f'<span class="or-th-sort-label">{label}</span>'
            f'<span class="{icon_cls}" aria-hidden="true">{caret}</span></button></th>'
        )

    def _render_columns_chrome(self, **ctx: Any) -> str:
        toggleable = self._toggleable_columns()
        if not toggleable:
            return ""
        from almasix.orbit.support.icons import icon as render_icon

        items: list[str] = []
        for col in toggleable:
            name = col.get_name() or ""
            label = e(col.get_label(**ctx) or name)
            visible = self._column_is_visible(col)
            checked = " checked" if visible else ""
            # Use change (once) — wire:click + conduit:click both fired and double-toggled.
            change = _alpine_wire_call(
                f"toggleColumn('{name}', $event.target.checked)"
            )
            items.append(
                f'<label class="or-columns-item">'
                f'<input type="checkbox" class="or-columns-check"{checked}{change} />'
                f"<span>{label}</span></label>"
            )
        reset = (
            f'<button type="button" class="or-link-btn or-link-danger"'
            f'{_conduit_click("resetToggledColumns")} @click="closeMenu()">Reset</button>'
        )
        view_cols = render_icon("heroicon-o-view-columns", size=20)
        return (
            f'<div class="or-table-columns" x-data="orbitDropdown" @click.outside="closeMenu()">'
            f'<button type="button" class="or-icon-btn or-columns-trigger" '
            f'@click="toggleMenu($event)" aria-haspopup="true" aria-label="Columns" '
            f':aria-expanded="menuOpen.toString()">{view_cols}</button>'
            f'<div class="or-columns-panel or-dropdown-menu or-dropdown-menu-end" '
            f'role="dialog" aria-label="Toggle columns" x-show="menuOpen" x-cloak>'
            f'<div class="or-columns-panel-header">'
            f'<h3 class="or-columns-panel-title">Columns</h3>{reset}</div>'
            f'<div class="or-columns-list">{"".join(items)}</div></div></div>'
        )

    def _render_pagination_chrome(self, **ctx: Any) -> str:
        if not self._paginated:
            return ""
        meta = self.pagination_meta()
        total = meta["total"]
        if total == 0:
            return ""
        page = meta["page"]
        last = meta["last_page"]
        per_page = self._per_page
        from_n = meta["from"]
        to_n = meta["to"]
        summary = f"Showing {from_n} to {to_n} of {total:,} results"
        mode = self._pagination_mode
        attrs: list[str] = [f'data-pagination-mode="{e(mode.value)}"']
        if self._query_string_identifier:
            attrs.append(f'data-query-string-id="{e(self._query_string_identifier)}"')
        if self._persist_records_per_page_in_session:
            attrs.append('data-persist-per-page="true"')
        attr_s = (" " + " ".join(attrs)) if attrs else ""

        prev_disabled = ' disabled aria-disabled="true"' if page <= 1 else ""
        next_disabled = ' disabled aria-disabled="true"' if page >= last else ""
        prev_click = "" if page <= 1 else _conduit_click(f"gotoPage({page - 1})")
        next_click = "" if page >= last else _conduit_click(f"gotoPage({page + 1})")

        options_src = list(self._pagination_page_options) or [5, 10, 25, 50]
        if per_page > 0 and per_page not in options_src and "all" not in options_src:
            options_src = sorted(
                [*options_src, per_page],
                key=lambda x: (isinstance(x, str), x),
            )
        option_html: list[str] = []
        for n in options_src:
            if n == "all":
                selected = " selected" if per_page <= 0 else ""
                option_html.append(f'<option value="all"{selected}>All</option>')
            else:
                selected = " selected" if n == per_page else ""
                option_html.append(f'<option value="{n}"{selected}>{n}</option>')
        options = "".join(option_html)

        nav_parts: list[str] = []
        if self._extreme_pagination_links and mode == PaginationMode.DEFAULT:
            first_dis = ' disabled aria-disabled="true"' if page <= 1 else ""
            last_dis = ' disabled aria-disabled="true"' if page >= last else ""
            first_click = "" if page <= 1 else _conduit_click("gotoPage(1)")
            last_click = "" if page >= last else _conduit_click(f"gotoPage({last})")
            nav_parts.append(
                f'<button type="button" class="or-table-pagination-nav"'
                f'{first_click}{first_dis} aria-label="First">'
                f'<span aria-hidden="true">«</span></button>'
            )
        nav_parts.append(
            f'<button type="button" class="or-table-pagination-nav"'
            f'{prev_click}{prev_disabled} aria-label="Previous">'
            f'<span aria-hidden="true">‹</span></button>'
        )
        if mode == PaginationMode.DEFAULT:
            for item in _pagination_pages(page, last):
                if item is None:
                    nav_parts.append(
                        '<span class="or-table-pagination-ellipsis" aria-hidden="true">…</span>'
                    )
                    continue
                if item == page:
                    nav_parts.append(
                        f'<button type="button" class="or-table-pagination-page is-active" '
                        f'aria-current="page">{item}</button>'
                    )
                else:
                    nav_parts.append(
                        f'<button type="button" class="or-table-pagination-page"'
                        f'{_conduit_click(f"gotoPage({item})")}>{item}</button>'
                    )
        nav_parts.append(
            f'<button type="button" class="or-table-pagination-nav"'
            f'{next_click}{next_disabled} aria-label="Next">'
            f'<span aria-hidden="true">›</span></button>'
        )
        if self._extreme_pagination_links and mode == PaginationMode.DEFAULT:
            last_dis = ' disabled aria-disabled="true"' if page >= last else ""
            last_click = "" if page >= last else _conduit_click(f"gotoPage({last})")
            nav_parts.append(
                f'<button type="button" class="or-table-pagination-nav"'
                f'{last_click}{last_dis} aria-label="Last">'
                f'<span aria-hidden="true">»</span></button>'
            )

        return (
            f'<nav class="or-table-pagination" aria-label="Pagination navigation"{attr_s}>'
            f'<span class="or-table-pagination-summary">{e(summary)}</span>'
            f'<label class="or-table-per-page or-per-page-split">'
            f'<span class="or-per-page-label">Per page</span>'
            f'<select class="or-per-page-select" aria-label="Records per page"'
            f'{_alpine_wire_call("setPerPage($event.target.value)")}>{options}</select>'
            f"</label>"
            f'<div class="or-table-pagination-pages">{"".join(nav_parts)}</div></nav>'
        )

    def _render_summary_cells(
        self,
        display: list[Column | LayoutComponent],
        records: Sequence[Any],
        *,
        scope: str,
        has_actions: bool,
        has_bulk: bool = False,
        **ctx: Any,
    ) -> str:
        cells: list[str] = []
        any_summary = False
        scope_label = ""
        if scope in {"page", "all"}:
            scope_label = f'<span class="or-summary-scope">{e(scope.title())}</span>'

        def _align_class(col: Column | None) -> str:
            if col is None:
                return ""
            align = col.get_alignment()
            # Numeric / money totals sit under figures — default end-aligned.
            if (align == "start" or not align) and (
                col._money_currency is not None or col._numeric
            ):
                return " or-align-end"
            if align and align != "start":
                return f" or-align-{align}"
            return ""

        def _breakpoint_class(col: Column | None) -> str:
            if col is None:
                return ""
            bp = ""
            if col._visible_from:
                bp += f" or-visible-from-{col._visible_from}"
            if col._hidden_from:
                bp += f" or-hidden-from-{col._hidden_from}"
            return bp

        if has_bulk:
            cells.append(
                f'<td class="or-td or-td-summary or-td-summary-scope">'
                f"{scope_label}</td>"
            )
            scope_label = ""

        for index, col in enumerate(display):
            column = col if isinstance(col, Column) else None
            align_c = _align_class(column)
            bp_c = _breakpoint_class(column)
            if column is not None and column.get_summarizers():
                any_summary = True
                inner = "".join(
                    s.render(
                        records=records,
                        attribute=column.get_name(),
                        column=column,
                        **ctx,
                    )
                    for s in column.get_summarizers()
                )
                prefix = scope_label
                scope_label = ""
                cells.append(
                    f'<td class="or-td or-td-summary{align_c}{bp_c}">'
                    f'<div class="or-summary-cell">{prefix}{inner}</div></td>'
                )
            else:
                # Put scope in the first empty data column when there is no bulk checkbox.
                prefix = ""
                if scope_label and index == 0:
                    prefix = scope_label
                    scope_label = ""
                inner = f'<div class="or-summary-cell">{prefix}</div>' if prefix else ""
                cells.append(f'<td class="or-td or-td-summary{align_c}{bp_c}">{inner}</td>')
        if not any_summary:
            return ""
        if has_actions:
            cells.append('<td class="or-td or-td-summary or-td-summary-actions"></td>')
        return (
            f'<tr class="or-tr or-summary-row" data-summary-scope="{e(scope)}">'
            f'{"".join(cells)}</tr>'
        )
    def _resolve_record_url(self, record: Any, **ctx: Any) -> str | None:
        url = self._record_url
        if url is None:
            return None
        if callable(url):
            try:
                resolved = url(record, **ctx)
            except TypeError:
                resolved = url(record)
            return str(resolved) if resolved else None
        return str(url)

    def _render_row(
        self,
        record: Any,
        display: list[Column | LayoutComponent],
        **ctx: Any,
    ) -> str:
        select = ""
        selected_ids = {str(x) for x in (ctx.get("selected") or [])}
        select_all = bool(ctx.get("select_all"))
        rid = str(self._record_value(record, "id") or id(record))
        if ctx.get("has_bulk"):
            checked = " checked" if select_all or rid in selected_ids else ""
            select = (
                f'<td class="or-td or-td-select">'
                f'<input type="checkbox" class="or-row-check" data-record-id="{e(rid)}"{checked} '
                f'@click.stop '
                f'@change="toggle(\'{e(rid)}\', $event.target.checked)" '
                f'aria-label="Select row" /></td>'
            )
        cells = select + "".join(c.render_cell(record, **ctx) for c in display)
        if self._actions:
            acts = self._render_actions(self._actions, record, **ctx)
            cells += f'<td class="or-td or-td-actions"><div class="or-row-actions">{acts}</div></td>'
        href = self._resolve_record_url(record, **ctx)
        row_class = "or-tr or-list-row"
        row_attrs = ""
        group_key = ctx.get("group_key")
        if group_key is not None:
            row_class += " or-group-member"
            row_attrs += f' data-group-key="{e(group_key)}"'
        extra_classes = self._resolve_record_classes(record, **ctx)
        if extra_classes:
            row_class += f" {extra_classes}"
        if href:
            row_class += " or-tr-clickable"
            target_js = (
                f"window.open('{e(href)}','_blank')"
                if self._open_record_url_in_new_tab
                else f"location.href='{e(href)}'"
            )
            row_attrs += (
                f' data-record-url="{e(href)}" tabindex="0" '
                f"onclick=\"if(!event.target.closest('a,button,input,label'))"
                f" {target_js}\""
            )
            if self._open_record_url_in_new_tab:
                row_attrs += ' data-record-url-new-tab="true"'
        return f'<tr class="{row_class}"{row_attrs}>{cells}</tr>'

    def _resolve_record_classes(self, record: Any, **ctx: Any) -> str:
        classes = self._record_classes
        if classes is None:
            return ""
        if callable(classes):
            classes = evaluate(classes, record, record=record)
        if classes is None or callable(classes):
            return ""
        if isinstance(classes, (list, tuple, set)):
            return " ".join(str(c) for c in classes if c)
        return str(classes)

    def _render_record_card(self, record: Any, display: list[Column | LayoutComponent], **ctx: Any) -> str:
        fields: list[str] = []
        title_html = ""
        for index, col in enumerate(display):
            label = e(self._header_label(col, **ctx))
            if isinstance(col, Column):
                cell = col.render_cell(record, **ctx)
                if cell.startswith("<td"):
                    inner = cell[cell.find(">") + 1 : cell.rfind("</td>")]
                else:
                    inner = cell
            else:
                inner = col.render_cell(record, **ctx) if hasattr(col, "render_cell") else ""
            if index == 0 and not title_html:
                title_html = f'<h3 class="or-table-record-card-title">{inner}</h3>'
                continue
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
        href = self._resolve_record_url(record, **ctx)
        link_open = f'<a class="or-table-record-card-link" href="{e(href)}">' if href else ""
        link_close = "</a>" if href else ""
        return (
            f'<article class="or-table-record-card or-card">'
            f"{link_open}{title_html}{link_close}"
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
        toggled = ctx.get("toggled_columns")
        if isinstance(toggled, dict):
            self.toggled_columns(toggled)
        table_group = ctx.get("table_group")
        if table_group is not None:
            self.active_group(str(table_group) if table_group else None)
        page_records = self.get_records()
        all_records = self.get_all_filtered_records()
        display = self.display_columns()
        flat = self.flat_columns()
        has_actions = bool(self._actions)
        has_bulk = bool(self._bulk_actions)
        colspan = len(display) + (1 if has_actions else 0) + (1 if has_bulk else 0)
        row_ctx = {**ctx, "has_bulk": has_bulk}

        header_cells: list[str] = []
        sub_header_cells: list[str] = []
        has_column_groups = any(isinstance(c, ColumnGroup) for c in self._columns)
        if has_bulk:
            bulk_th = (
                '<th class="or-th or-th-select"'
                + (' rowspan="2"' if has_column_groups else "")
                + ">"
                '<input type="checkbox" class="or-row-check or-select-all" '
                'aria-label="Select all on page" /></th>'
            )
            header_cells.append(bulk_th)
        for col in self._columns:
            if isinstance(col, ColumnGroup):
                visible_children = [c for c in col.get_columns() if self._column_is_visible(c)]
                if not visible_children:
                    continue
                span = len(visible_children)
                header_cells.append(
                    f'<th class="or-th or-th-group" colspan="{span}">'
                    f"{e(col.get_label(**ctx))}</th>"
                )
                for child in visible_children:
                    sub_header_cells.append(self._render_sort_header(child, **ctx))
            elif isinstance(col, LayoutComponent):
                rowspan = ' rowspan="2"' if has_column_groups else ""
                header_cells.append(
                    f'<th class="or-th or-th-layout"{rowspan}>'
                    f"{e(self._header_label(col, **ctx))}</th>"
                )
            else:
                if isinstance(col, Column):
                    if not self._column_is_visible(col):
                        continue
                    if has_column_groups:
                        header_cells.append(
                            f'<th class="or-th" rowspan="2">{e(self._header_label(col, **ctx))}</th>'
                        )
                        # Still need sort control — put full sort header in row 1 spanning 2
                        header_cells[-1] = self._render_sort_header(col, **ctx).replace(
                            "<th ", '<th rowspan="2" ', 1
                        )
                    else:
                        header_cells.append(self._render_sort_header(col, **ctx))
                else:
                    rowspan = ' rowspan="2"' if has_column_groups else ""
                    header_cells.append(
                        f'<th class="or-th"{rowspan}>{e(self._header_label(col, **ctx))}</th>'
                    )
        if has_actions:
            rowspan = ' rowspan="2"' if has_column_groups else ""
            header_cells.append(
                f'<th class="or-th or-th-actions or-align-end"{rowspan}>'
                '<span class="or-sr-only">Actions</span></th>'
            )
        if has_column_groups and sub_header_cells:
            headers = (
                f'<tr class="or-tr or-tr-group-headers">{"".join(header_cells)}</tr>'
                f'<tr class="or-tr or-tr-column-headers">{"".join(sub_header_cells)}</tr>'
            )
        else:
            headers = f'<tr class="or-tr">{"".join(header_cells)}</tr>'
        # Legacy single-row path expected bare <th> joined; wrap was done later — adjust below.

        active_group = self._default_group
        if self._active_group_name and self._groups:
            for g in self._groups:
                if (g.get_name() or "") == self._active_group_name:
                    active_group = g
                    break
        elif active_group is None and self._groups:
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
                        rows.append(
                            self._render_row(
                                record, display, group_key=bucket.key, **row_ctx
                            )
                        )
                group_summary = self._render_summary_cells(
                    display,
                    bucket.records,
                    scope="group",
                    has_actions=has_actions,
                    has_bulk=has_bulk,
                )
                if group_summary:
                    group_summary = group_summary.replace(
                        'class="or-tr or-summary-row"',
                        f'class="or-tr or-summary-row or-group-member" '
                        f'data-group-key="{e(bucket.key)}"',
                        1,
                    )
                    rows.append(group_summary)
        else:
            for record in page_records:
                rows.append(self._render_row(record, display, **row_ctx))

        body = "".join(rows)
        if not body:
            if self._empty_state_view is not None:
                view = self._empty_state_view
                empty_inner = str(evaluate(view, **ctx) if callable(view) else view)
            else:
                empty_actions = self._empty_state_actions or (
                    list(self._header_actions) if not skip_header_actions else []
                )
                if not empty_actions and self._header_actions:
                    empty_actions = list(self._header_actions)
                actions_html = ""
                if empty_actions:
                    actions_html = (
                        f'<div class="or-empty-state-actions">'
                        f"{self._render_actions(empty_actions, None, **ctx)}</div>"
                    )
                desc = (
                    f"<p>{e(self._empty_state_description)}</p>"
                    if self._empty_state_description
                    else ""
                )
                icon_html = ""
                if self._empty_state_icon:
                    from almasix.orbit.support.icons import icon as render_icon

                    icon_html = (
                        f'<div class="or-empty-state-icon">'
                        f"{render_icon(self._empty_state_icon, size=40)}</div>"
                    )
                empty_inner = (
                    f'<div class="or-empty-state">{icon_html}'
                    f"<h3>{e(self._empty_state_heading)}</h3>"
                    f"{desc}{actions_html}</div>"
                )
            body = (
                f'<tr class="or-tr"><td class="or-td or-empty" colspan="{colspan}">'
                f"{empty_inner}</td></tr>"
            )

        footer_parts: list[str] = []
        page_foot = (
            self._render_summary_cells(
                display,
                page_records,
                scope="page",
                has_actions=has_actions,
                has_bulk=has_bulk,
            )
            if self._summaries_page
            else ""
        )
        all_foot = (
            self._render_summary_cells(
                display,
                all_records,
                scope="all",
                has_actions=has_actions,
                has_bulk=has_bulk,
            )
            if self._summaries_all
            else ""
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
        if self._reorderable_enabled:
            is_reordering = bool(ctx.get("reordering") or getattr(self, "_is_reordering", False))
            if self._reorder_records_trigger is not None:
                from almasix.orbit.actions.action import Action as _Action

                trigger = self._reorder_records_trigger(
                    _Action.make("reorder").label("Reorder"),
                    is_reordering,
                )
                reorder_btn = trigger.render(**ctx) if hasattr(trigger, "render") else ""
            else:
                label = "Disable reordering" if is_reordering else "Enable reordering"
                reorder_btn = (
                    f'<button type="button" class="or-btn or-btn-gray or-btn-sm"'
                    f'{_conduit_click("toggleReordering")}>{e(label)}</button>'
                )
            toolbar_end += f'<div class="or-table-reorder-trigger">{reorder_btn}</div>'
        groups_chooser = ""
        if self._groups:
            active_name = self._active_group_name or (
                (active_group.get_name() if active_group else None)
                or (self._groups[0].get_name() if self._groups else "")
            )
            opts = "".join(
                f'<option value="{e(g.get_name() or "")}"'
                f'{" selected" if (g.get_name() or "") == active_name else ""}>'
                f'{e(g.get_label(**ctx) or g.get_name())}</option>'
                for g in self._groups
            )
            groups_chooser = (
                f'<div class="or-table-groups-chooser">'
                f'<label class="or-filter-label">Group</label>'
                f'<select class="or-select or-select-sm"'
                f'{_alpine_wire_call("setTableGroup($event.target.value)")}>'
                f"{opts}</select></div>"
            )

        filters = self._render_filter_chrome(**ctx)
        filter_indicators = self._render_filter_indicators(**ctx)
        columns_mgr = self._render_columns_chrome(**ctx)
        search = self._render_search_chrome(**ctx)

        selection_indicator = ""
        if self._bulk_actions:
            from almasix.orbit.actions.presets import ActionGroup, BulkActionGroup

            grouped: list[Action] = []
            flat_bulk: list[Action] = []
            for action in self._bulk_actions:
                if isinstance(action, ActionGroup):
                    grouped.append(action)
                else:
                    flat_bulk.append(action)
            if flat_bulk and not grouped:
                grouped = [BulkActionGroup.make(flat_bulk)]
                flat_bulk = []
            bulk_inner = self._render_actions([*grouped, *flat_bulk], None, **ctx)
            # Filament: Bulk actions only when rows are selected (with the selection bar).
            selection_indicator = (
                '<div class="or-ta-selection-indicator" wire:ignore conduit:ignore '
                'role="status" aria-live="polite" x-show="selectionCount > 0" x-cloak>'
                '<div class="or-ta-selection-start">'
                f'<div class="or-list-bulk or-table-bulk-trigger">{bulk_inner}</div>'
                '<span class="or-ta-selection-label" '
                "x-text=\"selectionCount === 1 "
                "? '1 record selected' "
                ": (selectionCount.toLocaleString() + ' records selected')\"></span>"
                "</div>"
                '<div class="or-ta-selection-actions">'
                '<button type="button" class="or-link-btn or-link-primary" '
                'x-show="showSelectAllResults" x-cloak @click="selectAllResults()">'
                "Select all "
                '<span x-text="Number(total).toLocaleString()"></span></button>'
                '<button type="button" class="or-link-btn or-link-danger" @click="clear()">'
                "Deselect all</button></div></div>"
            )

        toolbar = ""
        start_chrome = f"{groups_chooser}{toolbar_end}"
        tools_end = f"{filters}{columns_mgr}"
        tools = ""
        if filter_indicators or tools_end.strip():
            start = (
                f'<div class="or-list-toolbar-tools-start">{filter_indicators}</div>'
                if filter_indicators
                else ""
            )
            end = (
                f'<div class="or-list-toolbar-tools-end">{tools_end}</div>'
                if tools_end.strip()
                else ""
            )
            tools = f'<div class="or-list-toolbar-tools">{start}{end}</div>'
        end_stack = ""
        if tools.strip() or search:
            tools_row = tools if tools.strip() else ""
            divider = (
                '<div class="or-list-toolbar-divider" role="separator"></div>'
                if tools.strip() and search
                else ""
            )
            end_stack = (
                f'<div class="or-list-toolbar-end-stack">{tools_row}{divider}{search}</div>'
            )
        if start_chrome.strip() or end_stack.strip():
            toolbar = (
                f'<div class="or-list-toolbar">'
                f'<div class="or-list-toolbar-start">{start_chrome}</div>'
                f'<div class="or-list-toolbar-end">{end_stack}</div>'
                f"</div>"
            )

        _ = flat
        stacked = self._render_stacked_cards(page_records, display, **ctx)
        stacked_cls = " or-table-has-stacked" if stacked else ""
        selection_attr = ' x-data="orbitTableSelection"' if has_bulk else ""
        if has_bulk:
            selected_json = e(json.dumps([str(x) for x in (ctx.get("selected") or [])]))
            selection_attr += f' data-selected="{selected_json}"'
            selection_attr += f' data-total="{int(self.get_total())}"'
            if ctx.get("select_all"):
                selection_attr += ' data-select-all="true"'
        pagination = self._render_pagination_chrome(**ctx)

        heading_html = self._render_table_heading(
            skip_header_actions=skip_header_actions,
            **ctx,
        )
        wrap_attrs = grid_attr + selection_attr
        if self._poll:
            wrap_attrs += f' data-poll="{e(self._poll)}"'
        if self._defer_loading:
            wrap_attrs += ' data-defer-loading="true"'
        if self._query_string_identifier:
            wrap_attrs += f' data-query-string-id="{e(self._query_string_identifier)}"'
        if self._persist_sort_in_session:
            wrap_attrs += ' data-persist-sort="true"'
        if self._persist_columns_in_session:
            wrap_attrs += ' data-persist-columns="true"'
        if self._reorderable_enabled:
            wrap_attrs += f' data-reorderable="{e(self._reorderable_column or "")}"'
            wrap_attrs += f' data-reorder-direction="{e(self._reorderable_direction)}"'
            if ctx.get("reordering") or getattr(self, "_is_reordering", False):
                wrap_attrs += ' data-reordering="true"'

        if self._layout == "kanban":
            return (
                f'<div class="or-table-wrap or-list-card or-table-kanban"{wrap_attrs}>'
                f"{heading_html}{toolbar}{selection_indicator}"
                f"{self._render_kanban(page_records, display, **ctx)}{pagination}</div>"
            )

        return (
            f'<div class="or-table-wrap or-list-card{wrap_extra}{stacked_cls}"'
            f"{wrap_attrs}>"
            f"{heading_html}{toolbar}{selection_indicator}"
            f'<div class="or-list-table-scroll or-table-desktop">'
            f'<table class="or-table{striped}">'
            f'<thead class="or-thead">{headers}</thead>'
            f'<tbody class="or-tbody">{body}</tbody>'
            f"{tfoot}</table></div>"
            f"{stacked}{pagination}</div>"
        )

    def _render_table_heading(self, **ctx: Any) -> str:
        if self._header_html is not None:
            view = self._header_html
            return str(evaluate(view, **ctx) if callable(view) else view)
        skip_header_actions = bool(ctx.get("skip_header_actions", False))
        text_parts: list[str] = []
        if self._heading:
            text_parts.append(f'<h2 class="or-table-heading">{e(self._heading)}</h2>')
        if self._description:
            text_parts.append(
                f'<p class="or-table-description">{e(self._description)}</p>'
            )
        actions_html = ""
        if self._header_actions and not skip_header_actions:
            actions_html = (
                f'<div class="or-table-header-actions">'
                f"{self._render_actions(self._header_actions, None, **ctx)}</div>"
            )
        if not text_parts and not actions_html:
            return ""
        text_html = (
            f'<div class="or-table-header-text">{"".join(text_parts)}</div>'
            if text_parts
            else ""
        )
        return f'<div class="or-table-header">{text_html}{actions_html}</div>'
