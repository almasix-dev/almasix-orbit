"""Conduit page hosts for Orbit resource CRUD.

Orbit SDUI (Form / Table / Schema) paints HTML; these hosts own Conduit public
state and ``wire:*`` actions — the Filament↔Livewire relationship for Orbit.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, ClassVar

from almasix.conduit import Component, Conduit
from almasix.orbit.support.conduit_attrs import conduit_attr


class _DotDataPublic(set[str]):
    """Public property names that also accept ``data`` / ``data.*`` form bindings."""

    def __contains__(self, item: object) -> bool:
        if isinstance(item, str) and (item == "data" or item.startswith("data.")):
            return True
        return super().__contains__(item)


def _resource_records(resource: type[Any]) -> list[Any]:
    getter = getattr(resource, "get_records", None)
    if callable(getter):
        return list(getter())
    stored = getattr(resource, "records", None)
    if isinstance(stored, list):
        return list(stored)
    return []


def _save_resource_records(resource: type[Any], records: list[Any]) -> None:
    if isinstance(getattr(resource, "records", None), list):
        resource.records = list(records)


def _record_key(record: Any) -> str:
    if isinstance(record, dict):
        return str(record.get("id", ""))
    return str(getattr(record, "id", "") or "")


def _find_record(records: Iterable[Any], record_id: str) -> Any | None:
    rid = str(record_id or "")
    if not rid:
        return None
    for record in records:
        if _record_key(record) == rid:
            return record
    return None


def _next_record_id(records: Iterable[Any]) -> int:
    next_id = 1
    for record in records:
        try:
            next_id = max(next_id, int(_record_key(record) or 0) + 1)
        except (TypeError, ValueError):
            pass
    return next_id


def _jsonable_value(value: Any) -> Any:
    """Coerce ORM values so Conduit snapshots stay JSON-serializable."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable_value(v) for v in value]
    # datetime / date / time
    iso = getattr(value, "isoformat", None)
    if callable(iso):
        try:
            return iso()
        except Exception:
            pass
    # Decimal, UUID, Path, enums, etc.
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    try:
        from decimal import Decimal

        if isinstance(value, Decimal):
            return float(value) if value % 1 else int(value)
    except Exception:
        pass
    try:
        from enum import Enum

        if isinstance(value, Enum):
            return _jsonable_value(value.value)
    except Exception:
        pass
    return str(value)


def _as_record_dict(record: Any) -> dict[str, Any]:
    if isinstance(record, dict):
        return {str(k): _jsonable_value(v) for k, v in record.items()}
    if record is None:
        return {}
    out: dict[str, Any] = {}
    attrs = getattr(record, "get_attributes", None)
    if callable(attrs):
        try:
            raw = attrs()
            if isinstance(raw, dict):
                return {str(k): _jsonable_value(v) for k, v in raw.items()}
        except Exception:
            pass
    for key in getattr(record, "__dict__", {}):
        if not str(key).startswith("_"):
            out[str(key)] = _jsonable_value(getattr(record, key, None))
    rid = getattr(record, "id", None)
    if rid is not None:
        out.setdefault("id", _jsonable_value(rid))
    return out


_ORM_WRITE_SKIP = frozenset(
    {
        "id",
        "created_at",
        "updated_at",
        "deleted_at",
        "createdAt",
        "updatedAt",
        "deletedAt",
    }
)


def _orm_write_payload(data: dict[str, Any], model: type[Any] | None = None) -> dict[str, Any]:
    """Strip ids/timestamps and non-fillable keys before create/update."""
    payload = {
        k: v
        for k, v in dict(data or {}).items()
        if k not in _ORM_WRITE_SKIP and not str(k).startswith("_")
    }
    fillable = getattr(model, "fillable", None) if model is not None else None
    if fillable:
        allowed = {str(k) for k in fillable}
        payload = {k: v for k, v in payload.items() if k in allowed}
    return payload


def _is_orm_model(model: Any) -> bool:
    if model is None or not isinstance(model, type):
        return False
    # Fake demo models are empty types: type("Post", (), {}).
    if model.__module__ == "builtins" or model.__name__ in {"type", "object"}:
        return False
    try:
        from almasix.orm import Model

        return issubclass(model, Model) and model is not Model
    except Exception:
        return False


def _resource_model(resource: type[Any]) -> type[Any] | None:
    model = getattr(resource, "model", None)
    return model if _is_orm_model(model) else None


def _resource_mutable(resource: type[Any]) -> bool:
    """ORM models are mutable; in-memory seed lists are read-only unless opted in."""
    fn = getattr(resource, "records_are_mutable", None)
    if callable(fn):
        return bool(fn())
    flag = getattr(resource, "records_mutable", None)
    if flag is True:
        return True
    if flag is False:
        return False
    return _resource_model(resource) is not None


async def _await_maybe(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def _orm_fetch_all(model: type[Any]) -> list[dict[str, Any]]:
    rows = await _await_maybe(model.all())
    return [_as_record_dict(r) for r in (rows or [])]


async def _orm_find(model: type[Any], record_id: str) -> Any | None:
    found = await _await_maybe(model.find(record_id))
    if found is None and str(record_id).isdigit():
        found = await _await_maybe(model.find(int(record_id)))
    return found


async def _orm_create(model: type[Any], data: dict[str, Any]) -> dict[str, Any]:
    payload = _orm_write_payload(data, model)
    row = await _await_maybe(model.create(payload))
    return _as_record_dict(row)


async def _orm_update(model: type[Any], record_id: str, data: dict[str, Any]) -> dict[str, Any]:
    instance = await _orm_find(model, record_id)
    if instance is None:
        return await _orm_create(model, data)
    payload = _orm_write_payload(data, model)
    for key, val in payload.items():
        try:
            setattr(instance, key, val)
        except Exception:
            pass
    await _await_maybe(instance.save())
    return _as_record_dict(instance)


async def _orm_delete_ids(model: type[Any], ids: set[str]) -> None:
    for rid in ids:
        if not rid:
            continue
        instance = await _orm_find(model, rid)
        if instance is not None:
            await _await_maybe(instance.delete())


def _mount_action_args(
    name: str,
    record_id: Any = None,
    payload: Any = None,
    **kwargs: Any,
) -> tuple[str, str, dict[str, Any]]:
    """Normalize Conduit ``mountAction`` params from JS / Python callers.

    Client confirm calls ``mountAction(name, recordId, { data })`` with a third
    positional dict (not ``**kwargs``), so the third arg must be accepted positionally.
    """
    action_name = str(name or "")
    extra = payload if isinstance(payload, dict) else {}
    rid = str(
        record_id
        if record_id is not None
        else kwargs.get("recordId")
        if kwargs.get("recordId") is not None
        else extra.get("recordId")
        if extra.get("recordId") is not None
        else ""
    )
    data = kwargs.get("data") if isinstance(kwargs.get("data"), dict) else None
    if data is None and isinstance(extra.get("data"), dict):
        data = extra["data"]
    if data is None:
        data = {}
    return action_name, rid, data


class ConduitHost(Component):
    """Conduit host with redirect that works on PyPI Conduit (no ``Component.redirect``)."""

    def redirect(self, url: str, *, navigate: bool = False) -> None:
        """Queue a redirect after the response."""
        try:
            return super().redirect(url, navigate=navigate)  # type: ignore[misc]
        except AttributeError:
            pass
        except TypeError:
            try:
                return super().redirect(url)  # type: ignore[misc]
            except AttributeError:
                pass
        self._orbit_redirect = {"url": str(url), "navigate": bool(navigate)}

    def take_redirect(self) -> dict[str, Any] | None:
        """Pop the queued redirect, if any."""
        try:
            got = super().take_redirect()  # type: ignore[misc]
        except AttributeError:
            got = None
        if got is not None:
            return got
        target = getattr(self, "_orbit_redirect", None)
        self._orbit_redirect = None
        return target


class OrbitPageHost(ConduitHost):
    """Base host: panel + resource binding via ClassVars set by factories."""

    panel_id: ClassVar[str] = "admin"
    resource_slug: ClassVar[str] = ""
    _resource: ClassVar[type[Any] | None] = None
    _panel: ClassVar[Any] = None

    @classmethod
    def bind(cls, *, panel: Any, resource: type[Any] | None = None) -> type[OrbitPageHost]:
        name = f"{cls.__name__}_{getattr(resource, '__name__', 'page')}_{panel.id}"
        host = type(
            name,
            (cls,),
            {
                "panel_id": panel.id,
                "resource_slug": resource.get_slug() if resource is not None else "",
                "_resource": resource,
                "_panel": panel,
            },
        )
        if resource is not None:
            # So Resource.page_url / get_pages include the panel path prefix.
            resource._panel_path = panel.get_path()
        reg = f"orbit.{panel.id}.{getattr(resource, '__name__', 'page')}.{cls.__name__}"
        Conduit.register(reg, host)
        return host

    def get_resource(self) -> type[Any]:
        if type(self)._resource is None:
            raise RuntimeError(f"{type(self).__name__} has no bound resource")
        return type(self)._resource

    def get_panel(self) -> Any:
        return type(self)._panel


class ListRecordsHost(OrbitPageHost):
    """Index page host — table search/sort/tabs live on Conduit state."""

    records: list[dict[str, Any]] = []
    active_tab: str = ""
    table_search: str = ""
    table_sort: str = ""
    table_sort_direction: str = "asc"
    page: int = 1
    per_page: int = 10
    selected: list[str] = []
    select_all: bool = False
    table_filters: dict[str, Any] = {}
    table_group: str = ""
    toggled_columns: dict[str, bool] = {}
    column_order: list[str] = []
    reordering: bool = False

    def mount(self, **kwargs: Any) -> Any:
        resource = self.get_resource()
        if "records" in kwargs and kwargs["records"] is not None:
            self.records = list(kwargs["records"])
        elif not self.records:
            model = _resource_model(resource)
            if model is not None:
                return self._mount_orm(model, resource=resource)
            getter = getattr(resource, "get_records", None)
            if callable(getter):
                self.records = list(getter())
            else:
                stored = getattr(resource, "records", None)
                if isinstance(stored, list):
                    self.records = list(stored)
        self._mount_list_page(resource)
        return None

    async def _mount_orm(self, model: type[Any], *, resource: type[Any] | None = None) -> None:
        self.records = await _orm_fetch_all(model)
        self._mount_list_page(resource or self.get_resource())

    def _mount_list_page(self, resource: type[Any]) -> None:
        from almasix.orbit.panels.pages.resource_pages import ListRecords

        page = getattr(resource, "get_pages", lambda: {})()
        list_page = None
        if isinstance(page, dict):
            list_page = page.get("index")
        if list_page is None or isinstance(list_page, str):
            list_page = getattr(resource, "list_page", None)
        if list_page is None or list_page is ListRecords or isinstance(list_page, str):
            class _DefaultList(ListRecords):
                pass

            list_page = _DefaultList
        self._list_page = list_page
        self._list_page.resource = resource  # type: ignore[attr-defined]
        tabs = []
        if callable(getattr(resource, "get_tabs", None)):
            try:
                tabs = resource.get_tabs()
            except Exception:  # pragma: no cover
                tabs = []
        elif hasattr(self._list_page, "get_tabs"):
            try:
                bound_resource = resource

                class _Bound(self._list_page):  # type: ignore[misc, valid-type]
                    resource = bound_resource

                tabs = _Bound.get_tabs()
            except Exception:  # pragma: no cover - get_tabs implementations may raise
                tabs = []
        if tabs and not self.active_tab:
            self.active_tab = tabs[0].id

    def setTab(self, tab_id: str) -> None:
        self.active_tab = str(tab_id)
        self.page = 1
        self.select_all = False

    def sortBy(self, column: str) -> None:
        col = str(column or "")
        if not col:
            return
        if self.table_sort == col:
            self.table_sort_direction = (
                "desc" if str(self.table_sort_direction).lower() != "desc" else "asc"
            )
        else:
            self.table_sort = col
            self.table_sort_direction = "asc"
        self.page = 1
        self.select_all = False

    def gotoPage(self, page: int | str) -> None:
        try:
            self.page = max(1, int(page))
        except (TypeError, ValueError):
            self.page = 1

    def setPerPage(self, n: int | str) -> None:
        if str(n).lower() == "all":
            self.per_page = 0
        else:
            try:
                self.per_page = max(1, int(n))
            except (TypeError, ValueError):
                self.per_page = 10
        self.page = 1
        self.select_all = False

    def toggleReordering(self) -> None:
        self.reordering = not bool(getattr(self, "reordering", False))
        if self.reordering:
            self.select_all = False

    def clearSearch(self) -> None:
        self.table_search = ""
        self.page = 1
        self.select_all = False

    def setTableSearch(self, value: Any = "") -> None:
        """Set search query and reset to page 1 (Conduit has no nested/live side effects)."""
        self.table_search = "" if value is None else str(value)
        self.page = 1
        self.select_all = False

    def setTableFilter(self, name: str, value: Any = None) -> None:
        """Set one filter value. Conduit cannot bind nested ``table_filters.*`` paths."""
        key = str(name or "")
        if not key:
            return
        current = dict(self.table_filters or {})
        if value in (None, "", False):
            current.pop(key, None)
        elif isinstance(value, list) and not value:
            current.pop(key, None)
        else:
            current[key] = value
        self.table_filters = current
        self.page = 1
        if self._should_deselect_on_filter():
            self.select_all = False
            self.selected = []

    def applyTableFilters(self, filters: Any = None) -> None:
        """Commit deferred filter selections (optional full dict) and reset page."""
        if isinstance(filters, dict):
            cleaned: dict[str, Any] = {}
            for key, value in filters.items():
                if value in (None, "", False):
                    continue
                if isinstance(value, list) and not value:
                    continue
                cleaned[str(key)] = value
            self.table_filters = cleaned
        self.page = 1
        if self._should_deselect_on_filter():
            self.select_all = False
            self.selected = []

    def resetTableFilters(self) -> None:
        table = self.get_resource().get_table()
        self.table_filters = dict(table.get_default_filter_state())
        self.page = 1
        if self._should_deselect_on_filter():
            self.select_all = False
            self.selected = []

    def removeTableFilter(self, name: str) -> None:
        key = str(name or "")
        if not key:
            return
        current = dict(self.table_filters or {})
        current.pop(key, None)
        self.table_filters = current
        self.page = 1
        if self._should_deselect_on_filter():
            self.select_all = False
            self.selected = []

    def _should_deselect_on_filter(self) -> bool:
        try:
            table = self.get_resource().get_table()
            return table.should_deselect_all_records_when_filtered()
        except Exception:
            return True

    def setTableGroup(self, name: str = "") -> None:
        self.table_group = str(name or "")
        self.page = 1
        self.select_all = False

    def _column_visibility_state(self) -> dict[str, bool]:
        table = self.get_resource().get_table()
        state: dict[str, bool] = {}
        current = dict(self.toggled_columns or {})
        for col in table.flat_columns():
            if not col.is_toggleable():
                continue
            name = col.get_name() or ""
            if not name:
                continue
            if name in current:
                state[name] = bool(current[name])
            else:
                state[name] = not col.is_toggled_hidden_by_default()
        return state

    def toggleColumn(self, name: str, visible: Any = None) -> None:
        key = str(name or "")
        if not key:
            return
        state = self._column_visibility_state()
        if visible is None:
            state[key] = not bool(state.get(key, True))
        elif isinstance(visible, str):
            state[key] = visible.strip().lower() in {"1", "true", "yes", "on"}
        else:
            state[key] = bool(visible)
        self.toggled_columns = state

    def resetToggledColumns(self) -> None:
        self.toggled_columns = {}

    def reorderColumns(self, order: Any = None) -> None:
        """Persist column manager order (list of column names)."""
        if order is None:
            self.column_order = []
            return
        if isinstance(order, str):
            import json

            try:
                order = json.loads(order)
            except json.JSONDecodeError:
                order = [p.strip() for p in order.split(",") if p.strip()]
        if isinstance(order, (list, tuple)):
            self.column_order = [str(n) for n in order if str(n)]
        else:
            self.column_order = []

    def resetColumnOrder(self) -> None:
        self.column_order = []

    def _filtered_table(self) -> Any:
        """Build the resource table with the same search/sort/filters as the index."""
        resource = self.get_resource()
        table = resource.get_table()
        records = list(self.records or [])
        # Apply active tab query the same way ListRecords.render does.
        list_page = getattr(self, "_list_page", None)
        resource = self.get_resource()
        tabs = []
        if callable(getattr(resource, "get_tabs", None)):
            try:
                tabs = resource.get_tabs()
            except Exception:  # pragma: no cover
                tabs = []
        elif list_page is not None and hasattr(list_page, "get_tabs"):
            try:
                tabs = list_page.get_tabs()
            except Exception:  # pragma: no cover
                tabs = []
        active = self.active_tab or (tabs[0].id if tabs else "")
        for tab in tabs:
            if tab.id == active:
                records = tab.apply_query(records)
                break
        table.records(records)
        search = str(self.table_search or "").strip()
        if search:
            table.search(search)
        sort = str(self.table_sort or "").strip()
        if sort:
            table.sort(sort, str(self.table_sort_direction or "asc"))
        filters = dict(self.table_filters or {})
        defaults = table.get_default_filter_state()
        if defaults:
            merged = dict(defaults)
            merged.update(filters)
            filters = merged
            if not self.table_filters:
                self.table_filters = dict(defaults)
        if filters:
            table.filter_state(filters)
        return table

    def get_selected_ids(self) -> list[str]:
        """IDs for bulk actions — expands to all filtered rows when ``select_all``."""
        if self.select_all:
            table = self._filtered_table()
            ids: list[str] = []
            for record in table.get_all_filtered_records():
                rid = table._record_value(record, "id")
                if not rid:
                    rid = id(record)
                ids.append(str(rid))
            return ids
        return [str(x) for x in (self.selected or [])]

    def _record_key(self, record: Any) -> str:
        if isinstance(record, dict):
            return str(record.get("id", ""))
        return str(getattr(record, "id", "") or "")

    def _sync_resource_records(self) -> None:
        resource = self.get_resource()
        if isinstance(getattr(resource, "records", None), list):
            resource.records = list(self.records)

    def _table_column_for(self, name: str) -> Any:
        """Find ``name`` among the resource table's flat columns, or ``None``."""
        try:
            table = self.get_resource().get_table()
        except Exception:  # pragma: no cover - defensive, unbound/misconfigured host
            return None
        for candidate in table.flat_columns():
            if (candidate.get_name() or "") == name:
                return candidate
        return None

    def update_column_state(self, record_id: str, column: str, value: Any = None) -> None:
        """Persist an inline editable column value, running before/after hooks."""
        rid = str(record_id or "")
        col = str(column or "")
        if not rid or not col:
            return
        table_column = self._table_column_for(col)
        before = table_column.get_before_state_updated() if table_column is not None else None
        after = table_column.get_after_state_updated() if table_column is not None else None
        out: list[Any] = []
        for r in self.records:
            if self._record_key(r) != rid:
                out.append(r)
                continue
            old_value = r.get(col) if isinstance(r, dict) else getattr(r, col, None)
            if before is not None:
                from almasix.orbit.support.evaluate import evaluate

                evaluate(before, record=r, state=value, old=old_value, column=table_column)
            if isinstance(r, dict):
                row = dict(r)
                row[col] = value
                out.append(row)
                new_record: Any = row
            else:
                try:
                    setattr(r, col, value)
                except Exception:
                    pass
                out.append(r)
                new_record = r
            if after is not None:
                from almasix.orbit.support.evaluate import evaluate

                evaluate(after, record=new_record, state=value, old=old_value, column=table_column)
        self.records = out
        self._sync_resource_records()

    def updateColumnState(self, record_id: str, column: str, value: Any = None) -> None:
        self.update_column_state(record_id, column, value)

    def mountAction(
        self,
        name: str,
        record_id: str | None = None,
        payload: Any = None,
        **kwargs: Any,
    ) -> Any:
        action_name, rid, data = _mount_action_args(name, record_id, payload, **kwargs)
        resource = self.get_resource()
        mutable = _resource_mutable(resource)
        if action_name in {"delete", "force_delete", "delete_bulk", "create", "edit"} and not mutable:
            self.dispatch(
                "orbit-records-readonly",
                name=action_name,
                message="This demo resource uses a fixed seed list and cannot be changed.",
            )
            return None
        model = _resource_model(resource)
        if model is not None and action_name in {
            "delete",
            "force_delete",
            "delete_bulk",
            "create",
            "edit",
        }:
            return self._mount_action_orm(model, action_name, rid, data)
        if action_name in {"delete", "force_delete"} and rid:
            self.records = [r for r in self.records if self._record_key(r) != rid]
            self._sync_resource_records()
            self.selected = [s for s in (self.selected or []) if s != rid]
            return None
        if action_name == "delete_bulk":
            ids = set(self.get_selected_ids())
            self.records = [r for r in self.records if self._record_key(r) not in ids]
            self._sync_resource_records()
            self.selected = []
            self.select_all = False
            return None
        if action_name == "create" and data:
            next_id = 1
            for r in self.records:
                try:
                    next_id = max(next_id, int(self._record_key(r) or 0) + 1)
                except (TypeError, ValueError):
                    pass
            self.records = [*self.records, {"id": next_id, **dict(data)}]
            self._sync_resource_records()
            return None
        if action_name == "edit" and rid and data:
            out: list[Any] = []
            for r in self.records:
                if self._record_key(r) != rid:
                    out.append(r)
                    continue
                if isinstance(r, dict):
                    out.append({**r, **data, "id": r.get("id", rid)})
                else:
                    for key, val in data.items():
                        try:
                            setattr(r, key, val)
                        except Exception:
                            pass
                    out.append(r)
            self.records = out
            self._sync_resource_records()
            return None
        self.dispatch("orbit-mount-action", name=action_name, record_id=rid, **kwargs)
        return None

    async def _mount_action_orm(
        self,
        model: type[Any],
        action_name: str,
        rid: str,
        data: dict[str, Any],
    ) -> None:
        if action_name in {"delete", "force_delete"} and rid:
            await _orm_delete_ids(model, {rid})
            self.records = [r for r in self.records if self._record_key(r) != rid]
            self.selected = [s for s in (self.selected or []) if s != rid]
            return
        if action_name == "delete_bulk":
            ids = set(self.get_selected_ids())
            await _orm_delete_ids(model, ids)
            self.records = [r for r in self.records if self._record_key(r) not in ids]
            self.selected = []
            self.select_all = False
            return
        if action_name == "create" and data:
            row = await _orm_create(model, dict(data))
            self.records = [*self.records, row]
            return
        if action_name == "edit" and rid and data:
            row = await _orm_update(model, rid, dict(data))
            out: list[Any] = []
            replaced = False
            for r in self.records:
                if self._record_key(r) != rid:
                    out.append(r)
                    continue
                out.append(row)
                replaced = True
            if not replaced:
                out.append(row)
            self.records = out
            return
        self.dispatch("orbit-mount-action", name=action_name, record_id=rid)

    def render(self) -> str:
        resource = self.get_resource()

        from almasix.orbit.panels.pages.resource_pages import ListRecords

        class BoundList(ListRecords):
            @classmethod
            def get_tabs(cls):
                getter = getattr(resource, "get_tabs", None)
                if callable(getter):
                    return getter()
                return []

        BoundList.resource = resource  # type: ignore[misc]
        return BoundList.render(
            records=list(self.records),
            active_tab=self.active_tab or None,
            table_search=self.table_search,
            table_sort=self.table_sort,
            table_sort_direction=self.table_sort_direction,
            page=self.page,
            per_page=self.per_page,
            table_filters=dict(self.table_filters or {}),
            selected=list(self.selected or []),
            select_all=bool(self.select_all),
            table_group=self.table_group or None,
            toggled_columns=self._column_visibility_state(),
            column_order=list(self.column_order or []),
            reordering=bool(self.reordering),
        )


class FormDataMutations:
    """Shared Conduit handlers for nested form fields (repeater / builder / key-value)."""

    data: dict[str, Any]
    select_search: dict[str, str] = {}

    @classmethod
    def _public_property_names(cls) -> set[str]:
        return _DotDataPublic(super()._public_property_names())

    def set_property(self, name: str, value: Any) -> None:
        if name == "data":
            self.data = dict(value) if isinstance(value, dict) else {}
            return
        if name.startswith("data."):
            self._form_path_set(name[5:], value)
            self.data = dict(self.data or {})
            return
        super().set_property(name, value)

    def _form_path_get(self, path: str) -> Any:
        cur: Any = self.data
        for part in str(path or "").split("."):
            if not part:
                continue
            if isinstance(cur, dict):
                cur = cur.get(part)
            elif isinstance(cur, list) and part.isdigit():
                idx = int(part)
                cur = cur[idx] if 0 <= idx < len(cur) else None
            else:
                return None
        return cur

    def _form_path_set(self, path: str, value: Any) -> None:
        parts = [p for p in str(path or "").split(".") if p]
        if not parts:
            return
        if not isinstance(self.data, dict):
            self.data = {}
        cur: Any = self.data
        for i, part in enumerate(parts[:-1]):
            nxt_key = parts[i + 1]
            want_list = nxt_key.isdigit()
            if part.isdigit():
                idx = int(part)
                if not isinstance(cur, list):  # pragma: no cover - defensive
                    return
                while len(cur) <= idx:
                    cur.append([] if want_list else {})
                if want_list and not isinstance(cur[idx], list):
                    cur[idx] = []
                if not want_list and not isinstance(cur[idx], dict):
                    cur[idx] = {}
                cur = cur[idx]
                continue
            if not isinstance(cur, dict):  # pragma: no cover - defensive
                return
            nxt = cur.get(part)
            if want_list:
                if not isinstance(nxt, list):
                    nxt = []
                    cur[part] = nxt
            elif not isinstance(nxt, dict):
                nxt = {}
                cur[part] = nxt
            cur = nxt
        last = parts[-1]
        if last.isdigit() and isinstance(cur, list):
            idx = int(last)
            while len(cur) <= idx:
                cur.append(None)
            cur[idx] = value
        elif isinstance(cur, dict):
            cur[last] = value
        else:  # pragma: no cover - walk always leaves dict or list+digit last
            return

    def addRepeaterItem(self, name: str) -> None:
        key = str(name or "")
        items = self._form_path_get(key)
        if not isinstance(items, list):
            items = []
        items = [*items, {}]
        self._form_path_set(key, items)

    def removeRepeaterItem(self, name: str, index: int | str = 0) -> None:
        key = str(name or "")
        items = self._form_path_get(key)
        if not isinstance(items, list):
            return
        try:
            i = int(index)
        except (TypeError, ValueError):
            return
        if 0 <= i < len(items):
            items = list(items)
            items.pop(i)
            self._form_path_set(key, items)

    def moveRepeaterItem(self, name: str, index: int | str = 0, delta: int | str = 0) -> None:
        key = str(name or "")
        items = self._form_path_get(key)
        if not isinstance(items, list):
            return
        try:
            i = int(index)
            d = int(delta)
        except (TypeError, ValueError):
            return
        j = i + d
        if i < 0 or j < 0 or i >= len(items) or j >= len(items):
            return
        items = list(items)
        items[i], items[j] = items[j], items[i]
        self._form_path_set(key, items)

    def cloneRepeaterItem(self, name: str, index: int | str = 0) -> None:
        key = str(name or "")
        items = self._form_path_get(key)
        if not isinstance(items, list):
            return
        try:
            i = int(index)
        except (TypeError, ValueError):
            return
        if not (0 <= i < len(items)):
            return
        items = list(items)
        clone = dict(items[i]) if isinstance(items[i], dict) else items[i]
        items.insert(i + 1, clone)
        self._form_path_set(key, items)

    def addBuilderBlock(self, name: str, block_type: str = "") -> None:
        key = str(name or "")
        items = self._form_path_get(key)
        if not isinstance(items, list):
            items = []
        items = [*items, {"type": str(block_type or "")}]
        self._form_path_set(key, items)

    def addKeyValueRow(self, name: str) -> None:
        key = str(name or "")
        data = self._form_path_get(key)
        if not isinstance(data, dict):
            data = {}
        n = 1
        while f"key{n}" in data:
            n += 1
        data = {**data, f"key{n}": ""}
        self._form_path_set(key, data)

    def mountTableSelect(self, name: str, **kwargs: Any) -> None:
        self.dispatch("orbit-mount-table-select", name=str(name or ""), **kwargs)

    def mountCreateOption(self, name: str, **kwargs: Any) -> None:
        self.dispatch("orbit-mount-create-option", name=str(name or ""), **kwargs)

    def mountEditOption(self, name: str, **kwargs: Any) -> None:
        self.dispatch("orbit-mount-edit-option", name=str(name or ""), **kwargs)

    def searchSelectOptions(self, name: str, search: str = "") -> None:
        """AJAX option search for relationship / custom searchable Selects (Filament parity)."""
        field_name = str(name or "")
        current = dict(getattr(self, "select_search", None) or {})
        current[field_name] = str(search or "")
        self.select_search = current


class CreateRecordHost(FormDataMutations, OrbitPageHost):
    data: dict[str, Any] = {}
    select_search: dict[str, str] = {}
    created_id: str | None = None

    def mount(self, **kwargs: Any) -> None:
        if isinstance(kwargs.get("data"), dict):
            self.data = dict(kwargs["data"])

    def create(self) -> Any:
        resource = self.get_resource()
        if not _resource_mutable(resource):
            self.dispatch(
                "orbit-records-readonly",
                message="This demo resource uses a fixed seed list and cannot be changed.",
            )
            return None
        model = _resource_model(resource)
        if model is not None:
            return self._create_orm(model, resource)
        records = _resource_records(resource)
        next_id = _next_record_id(records)
        payload = dict(self.data or {})
        payload.pop("id", None)
        row = {"id": next_id, **payload}
        records = [*records, row]
        _save_resource_records(resource, records)
        self.created_id = str(next_id)
        self.data = dict(row)
        self.dispatch("orbit-record-created", data=dict(row))
        self.redirect(resource.page_url("view", row))
        return None

    async def _create_orm(self, model: type[Any], resource: type[Any]) -> None:
        row = await _orm_create(model, dict(self.data or {}))
        self.created_id = str(row.get("id") or "")
        self.data = dict(row)
        self.dispatch("orbit-record-created", data=dict(row))
        self.redirect(resource.page_url("view", row))

    def mountAction(
        self,
        name: str,
        record_id: Any = None,
        payload: Any = None,
        **kwargs: Any,
    ) -> None:
        action_name, rid, _ = _mount_action_args(name, record_id, payload, **kwargs)
        self.dispatch("orbit-mount-action", name=action_name, record_id=rid, **kwargs)

    def render(self) -> str:
        from almasix.orbit.panels.pages.resource_pages import CreateRecord

        class Bound(CreateRecord):
            pass

        resource = self.get_resource()
        Bound.resource = resource  # type: ignore[misc]
        model = None
        try:
            model = resource.get_model()
        except Exception:
            model = getattr(resource, "model", None)
        return Bound.render(
            state=dict(self.data),
            select_search=dict(self.select_search or {}),
            model=model,
            resource=resource,
        )


class EditRecordHost(FormDataMutations, OrbitPageHost):
    record_id: str = ""
    data: dict[str, Any] = {}
    select_search: dict[str, str] = {}

    def mount(self, **kwargs: Any) -> Any:
        if kwargs.get("record_id") is not None:
            self.record_id = str(kwargs["record_id"])
        if isinstance(kwargs.get("data"), dict):
            self.data = dict(kwargs["data"])
        elif isinstance(kwargs.get("record"), dict):
            self.data = dict(kwargs["record"])
            self.record_id = str(self.data.get("id") or self.record_id)
        elif self.record_id and not self.data:
            model = _resource_model(self.get_resource())
            if model is not None:
                return self._mount_orm(model)
            found = _find_record(_resource_records(self.get_resource()), self.record_id)
            if found is not None:
                self.data = _as_record_dict(found)
        return None

    async def _mount_orm(self, model: type[Any]) -> None:
        found = await _orm_find(model, self.record_id)
        if found is not None:
            self.data = _as_record_dict(found)

    def save(self) -> Any:
        resource = self.get_resource()
        if not _resource_mutable(resource):
            self.dispatch(
                "orbit-records-readonly",
                message="This demo resource uses a fixed seed list and cannot be changed.",
            )
            return None
        model = _resource_model(resource)
        if model is not None:
            return self._save_orm(model, resource)
        rid = str(self.record_id or self.data.get("id") or "")
        records = _resource_records(resource)
        payload = dict(self.data or {})
        if rid:
            existing = _find_record(records, rid)
            if isinstance(existing, dict) and "id" in existing:
                payload["id"] = existing["id"]
            else:
                payload["id"] = int(rid) if rid.isdigit() else rid
            out: list[Any] = []
            replaced = False
            for record in records:
                if _record_key(record) != rid:
                    out.append(record)
                    continue
                if isinstance(record, dict):
                    out.append({**record, **payload, "id": record.get("id", payload.get("id"))})
                else:
                    for key, val in payload.items():
                        if key == "id":
                            continue
                        try:
                            setattr(record, key, val)
                        except Exception:
                            pass
                    out.append(record)
                replaced = True
            if not replaced:
                out.append(payload)
            records = out
        else:
            next_id = _next_record_id(records)
            payload["id"] = next_id
            rid = str(next_id)
            records = [*records, payload]
        _save_resource_records(resource, records)
        self.record_id = rid
        self.data = dict(payload)
        self.dispatch("orbit-record-saved", record_id=self.record_id, data=dict(self.data))
        self.redirect(resource.page_url("view", self.data))
        return None

    async def _save_orm(self, model: type[Any], resource: type[Any]) -> None:
        rid = str(self.record_id or self.data.get("id") or "")
        row = await _orm_update(model, rid, dict(self.data or {}))
        self.record_id = str(row.get("id") or rid)
        self.data = dict(row)
        self.dispatch("orbit-record-saved", record_id=self.record_id, data=dict(self.data))
        self.redirect(resource.page_url("view", self.data))

    def mountAction(
        self,
        name: str,
        record_id: str | None = None,
        payload: Any = None,
        **kwargs: Any,
    ) -> Any:
        action_name, rid, _ = _mount_action_args(name, record_id, payload, **kwargs)
        if not rid:
            rid = str(self.record_id or "")
        if action_name in {"delete", "force_delete"} and rid:
            resource = self.get_resource()
            if not _resource_mutable(resource):
                self.dispatch(
                    "orbit-records-readonly",
                    message="This demo resource uses a fixed seed list and cannot be changed.",
                )
                return None
            model = _resource_model(resource)
            if model is not None:
                return self._delete_orm(model, resource, rid)
            records = [r for r in _resource_records(resource) if _record_key(r) != rid]
            _save_resource_records(resource, records)
            self.dispatch("orbit-record-deleted", record_id=rid)
            self.redirect(resource.page_url("index"))
            return None
        self.dispatch("orbit-mount-action", name=action_name, record_id=rid, **kwargs)
        return None

    async def _delete_orm(self, model: type[Any], resource: type[Any], rid: str) -> None:
        await _orm_delete_ids(model, {rid})
        self.dispatch("orbit-record-deleted", record_id=rid)
        self.redirect(resource.page_url("index"))

    def render(self) -> str:
        from almasix.orbit.panels.pages.resource_pages import EditRecord

        class Bound(EditRecord):
            pass

        Bound.resource = self.get_resource()  # type: ignore[misc]
        record = dict(self.data)
        if self.record_id and "id" not in record:
            record["id"] = self.record_id
        resource = self.get_resource()
        model = None
        try:
            model = resource.get_model()
        except Exception:
            model = getattr(resource, "model", None)
        return Bound.render(
            record=record,
            state=dict(self.data) if self.data else None,
            select_search=dict(self.select_search or {}),
            model=model,
            resource=resource,
        )


class ViewRecordHost(OrbitPageHost):
    record_id: str = ""
    record: dict[str, Any] = {}

    def mount(self, **kwargs: Any) -> Any:
        if kwargs.get("record_id") is not None:
            self.record_id = str(kwargs["record_id"])
        if isinstance(kwargs.get("record"), dict):
            self.record = dict(kwargs["record"])
            self.record_id = str(self.record.get("id") or self.record_id)
        elif self.record_id and not self.record:
            model = _resource_model(self.get_resource())
            if model is not None:
                return self._mount_orm(model)
            found = _find_record(_resource_records(self.get_resource()), self.record_id)
            if found is not None:
                self.record = _as_record_dict(found)
        return None

    async def _mount_orm(self, model: type[Any]) -> None:
        found = await _orm_find(model, self.record_id)
        if found is not None:
            self.record = _as_record_dict(found)

    def mountAction(
        self,
        name: str,
        record_id: str | None = None,
        payload: Any = None,
        **kwargs: Any,
    ) -> Any:
        action_name, rid, _ = _mount_action_args(name, record_id, payload, **kwargs)
        if not rid:
            rid = str(self.record_id or "")
        if action_name in {"delete", "force_delete"} and rid:
            resource = self.get_resource()
            if not _resource_mutable(resource):
                self.dispatch(
                    "orbit-records-readonly",
                    message="This demo resource uses a fixed seed list and cannot be changed.",
                )
                return None
            model = _resource_model(resource)
            if model is not None:
                return self._delete_orm(model, resource, rid)
            records = [r for r in _resource_records(resource) if _record_key(r) != rid]
            _save_resource_records(resource, records)
            self.dispatch("orbit-record-deleted", record_id=rid)
            self.redirect(resource.page_url("index"))
            return None
        self.dispatch("orbit-mount-action", name=action_name, record_id=rid, **kwargs)
        return None

    async def _delete_orm(self, model: type[Any], resource: type[Any], rid: str) -> None:
        await _orm_delete_ids(model, {rid})
        self.dispatch("orbit-record-deleted", record_id=rid)
        self.redirect(resource.page_url("index"))

    def render(self) -> str:
        from almasix.orbit.panels.pages.resource_pages import ViewRecord

        class Bound(ViewRecord):
            pass

        Bound.resource = self.get_resource()  # type: ignore[misc]
        data = dict(self.record)
        if self.record_id and "id" not in data:
            data["id"] = self.record_id
        return Bound.render(record=data)


class FormHost(FormDataMutations, ConduitHost):
    """Standalone form host for custom pages."""

    data: dict[str, Any] = {}
    select_search: dict[str, str] = {}
    _form_factory: ClassVar[Any] = None
    _title: ClassVar[str] = "Form"

    def mount(self, **kwargs: Any) -> None:
        if isinstance(kwargs.get("data"), dict):
            self.data = dict(kwargs["data"])

    def save(self) -> None:
        self.dispatch("orbit-form-saved", data=dict(self.data))

    def mountAction(
        self,
        name: str,
        record_id: Any = None,
        payload: Any = None,
        **kwargs: Any,
    ) -> None:
        action_name, rid, _ = _mount_action_args(name, record_id, payload, **kwargs)
        self.dispatch("orbit-mount-action", name=action_name, record_id=rid, **kwargs)

    def render(self) -> str:
        factory = type(self)._form_factory
        if factory is None:
            return '<div class="or-page"><p class="or-muted">No form configured.</p></div>'
        form = factory()
        form.fill(self.data)
        title = type(self)._title
        return (
            f'<div class="or-page or-page-form"><h1 class="or-page-title">{title}</h1>'
            f'<form class="or-form"{conduit_attr("submit", "save")}>{form.render(self.data, select_search=dict(self.select_search or {}))}'
            f'<div class="or-form-actions">'
            f'<button type="submit" class="or-btn or-btn-primary">Save</button>'
            f"</div></form></div>"
        )


class TableHost(ConduitHost):
    """Standalone table host for custom pages."""

    records: list[dict[str, Any]] = []
    table_search: str = ""
    _table_factory: ClassVar[Any] = None
    _title: ClassVar[str] = "Table"

    def mount(self, **kwargs: Any) -> None:
        if kwargs.get("records") is not None:
            self.records = list(kwargs["records"])

    def render(self) -> str:
        factory = type(self)._table_factory
        if factory is None:
            return '<div class="or-page"><p class="or-muted">No table configured.</p></div>'
        table = factory()
        table.records(self.records)
        if self.table_search:
            table.search(self.table_search)
        title = type(self)._title
        return (
            f'<div class="or-page or-page-table"><h1 class="or-page-title">{title}</h1>'
            f"{table.render()}</div>"
        )


class LoginHost(FormDataMutations, ConduitHost):
    """Auth login Conduit host (guest-accessible route).

    Form fields bind as ``data.email`` / ``data.password`` (see Field._wire_binding).
    """

    data: dict[str, Any] = {}
    error: str = ""
    panel_id: ClassVar[str] = "admin"
    _panel: ClassVar[Any] = None
    _page_cls: ClassVar[Any] = None

    def __init__(self, **kwargs: Any) -> None:
        data = dict(kwargs.pop("data", None) or {})
        # Compat: callers may still pass top-level email/password/remember.
        for key in ("email", "password", "remember"):
            if key in kwargs and key not in data:
                data[key] = kwargs.pop(key)
        super().__init__(**kwargs)
        self.data = dict(data)

    async def authenticate(self) -> None:
        self.error = ""
        payload = dict(self.data or {})
        email = str(payload.get("email") or "").strip()
        password = str(payload.get("password") or "")
        if not email or not password:
            self.error = "Email and password are required."
            return

        remember = bool(payload.get("remember"))
        try:
            from almasix.auth import auth

            ok = await auth().attempt(
                {"email": email, "password": password},
                remember=remember,
            )
        except Exception as exc:  # pragma: no cover - provider/config failures
            self.error = str(exc) or "Sign in failed."
            return

        if not ok:
            self.error = "These credentials do not match our records."
            return

        try:
            from almasix.session.store import get_session

            if get_session() is None:
                self.error = (
                    "Signed in, but no session is available. "
                    "Add StartSession to the web middleware group."
                )
                return
        except Exception:
            pass

        panel = type(self)._panel
        home = "/"
        if panel is not None:
            home = panel.url() if hasattr(panel, "url") else str(panel.get_path() or "/")
            if not str(home).startswith("/"):
                home = f"/{home}"
        self.data = {**payload, "password": ""}
        self.redirect(home)

    def render(self) -> str:
        from almasix.orbit.panels.auth import Login

        panel = type(self)._panel
        page_cls = type(self)._page_cls or Login
        brand = "Orbit"
        brand_logo = None
        brand_logo_dark = None
        brand_logo_only = False
        show_signup = False
        signup_url = None
        if panel is not None:
            brand = str(getattr(panel, "_brand", None) or brand)
            getter = getattr(panel, "get_brand_logo_url", None)
            if callable(getter):
                brand_logo = getter(dark=False)
                brand_logo_dark = getter(dark=True)
            else:
                brand_logo = getattr(panel, "_brand_logo", None)
                brand_logo_dark = getattr(panel, "_brand_logo_dark", None) or brand_logo
            brand_logo_only = bool(getattr(panel, "_brand_logo_only", False))
            if callable(getattr(panel, "signup_enabled", None)) and panel.signup_enabled():
                show_signup = True
                signup_url = panel.url("register")
        return page_cls.render(
            data=dict(self.data or {}),
            brand=brand,
            brand_logo=brand_logo,
            brand_logo_dark=brand_logo_dark,
            brand_logo_only=brand_logo_only,
            error=self._display_error(),
            show_signup=show_signup,
            signup_url=signup_url,
        )

    def _display_error(self) -> str | None:
        if self.error:
            return self.error
        bag = getattr(self, "errors", None) or {}
        for key in (
            "email",
            "password",
            "name",
            "password_confirmation",
            "data.email",
            "data.password",
            "_method",
        ):
            msgs = bag.get(key)
            if msgs:
                return str(msgs[0])
        return None


class RegisterHost(FormDataMutations, ConduitHost):
    """Auth registration Conduit host (guest-accessible when signup is enabled)."""

    data: dict[str, Any] = {}
    error: str = ""
    panel_id: ClassVar[str] = "admin"
    _panel: ClassVar[Any] = None
    _page_cls: ClassVar[Any] = None

    def __init__(self, **kwargs: Any) -> None:
        data = dict(kwargs.pop("data", None) or {})
        for key in ("name", "email", "password", "password_confirmation"):
            if key in kwargs and key not in data:
                data[key] = kwargs.pop(key)
        super().__init__(**kwargs)
        self.data = dict(data)

    async def register(self) -> None:
        self.error = ""
        payload = dict(self.data or {})
        name = str(payload.get("name") or "").strip()
        email = str(payload.get("email") or "").strip()
        password = str(payload.get("password") or "")
        confirm = str(payload.get("password_confirmation") or "")
        if not name or not email or not password:
            self.error = "Name, email, and password are required."
            return
        if password != confirm:
            self.error = "Passwords do not match."
            return

        try:
            user_model = self._user_model()
            from almasix.hashing import Hash

            if await self._email_taken(user_model, email):
                self.error = "An account with this email already exists."
                return

            create = getattr(user_model, "create", None)
            if create is None:
                self.error = "User model cannot create accounts."
                return
            result = create(
                {
                    "name": name,
                    "email": email,
                    "password": Hash.make(password),
                }
            )
            if hasattr(result, "__await__"):
                user = await result
            else:
                user = result
        except Exception as exc:
            from almasix.orbit.panels.db_errors import map_db_error

            self.error = map_db_error(exc)
            return

        try:
            from almasix.auth import auth

            await auth().login(user)
        except Exception as exc:
            self.error = str(exc) or "Account created, but sign-in failed."
            return

        panel = type(self)._panel
        home = "/"
        if panel is not None:
            home = panel.url() if hasattr(panel, "url") else str(panel.get_path() or "/")
            if not str(home).startswith("/"):
                home = f"/{home}"
        self.data = {**payload, "password": "", "password_confirmation": ""}
        self.redirect(home)

    def _user_model(self) -> type[Any]:
        import importlib

        path = "app.models.user.User"
        try:
            from almasix.config import config

            path = str(
                config("auth.providers.users.model", "app.models.user.User")
                or "app.models.user.User"
            )
        except Exception:
            pass
        module_name, _, class_name = path.rpartition(".")
        module = importlib.import_module(module_name)
        model = getattr(module, class_name, None)
        if model is None:
            raise AttributeError(f"{class_name} not found in {module_name}")
        return model

    @staticmethod
    async def _email_taken(user_model: type[Any], email: str) -> bool:
        """Best-effort existence check before INSERT (IntegrityError remains the race fallback).

        Almasix ORM ``QueryBuilder.first()`` is async — awaiting is required. Treating the
        bare coroutine as a row made every signup look like a duplicate email.
        """
        email_l = email.lower()

        async def _resolve(row: Any) -> Any:
            if hasattr(row, "__await__"):
                return await row
            return row

        try:
            where = getattr(user_model, "where", None)
            if callable(where):
                row = await _resolve(where("email", email).first())
                if row is not None:
                    return True
            query = getattr(user_model, "query", None)
            if callable(query):
                builder = query()
                where_b = getattr(builder, "where", None)
                if callable(where_b):
                    row = await _resolve(where_b("email", email).first())
                    if row is not None:
                        return True
            # In-memory / test models with a class-level records list
            records = getattr(user_model, "records", None)
            if isinstance(records, list):
                return any(
                    str(
                        getattr(r, "email", None)
                        or (r.get("email") if isinstance(r, dict) else "")
                        or ""
                    ).lower()
                    == email_l
                    for r in records
                )
        except Exception:
            return False
        return False

    def render(self) -> str:
        from almasix.orbit.panels.auth import Register

        panel = type(self)._panel
        page_cls = type(self)._page_cls or Register
        brand = "Orbit"
        brand_logo = None
        brand_logo_dark = None
        brand_logo_only = False
        login_url = "/login"
        if panel is not None:
            brand = str(getattr(panel, "_brand", None) or brand)
            getter = getattr(panel, "get_brand_logo_url", None)
            if callable(getter):
                brand_logo = getter(dark=False)
                brand_logo_dark = getter(dark=True)
            else:
                brand_logo = getattr(panel, "_brand_logo", None)
                brand_logo_dark = getattr(panel, "_brand_logo_dark", None) or brand_logo
            brand_logo_only = bool(getattr(panel, "_brand_logo_only", False))
            login_url = panel.url("login")
        return page_cls.render(
            data=dict(self.data or {}),
            brand=brand,
            brand_logo=brand_logo,
            brand_logo_dark=brand_logo_dark,
            brand_logo_only=brand_logo_only,
            error=self._display_error(),
            login_url=login_url,
        )

    def _display_error(self) -> str | None:
        if self.error:
            return self.error
        bag = getattr(self, "errors", None) or {}
        for key in (
            "email",
            "password",
            "name",
            "password_confirmation",
            "data.email",
            "data.password",
            "data.name",
            "_method",
        ):
            msgs = bag.get(key)
            if msgs:
                return str(msgs[0])
        return None
