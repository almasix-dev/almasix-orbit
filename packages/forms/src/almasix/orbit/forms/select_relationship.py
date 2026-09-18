"""Resolve Select ``relationship()`` options from Almasix ORM models.

Mirrors Filament Select semantics:

- Static / non-searchable relationship → load up to ``options_limit`` (default 50).
- ``searchable()`` without ``preload()`` → AJAX search; initial options are only
  the currently selected value(s).
- ``searchable()`` + ``preload()`` → load capped options eagerly; client may
  still filter / refine via search.

Option labels may be:

- a single ``title_attribute`` column (default),
- a format string such as ``\"{name} - {bio}\"``,
- or a ``get_option_label_from_record_using`` callback.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import Any

DEFAULT_OPTIONS_LIMIT = 50
_FORMAT_TOKEN = re.compile(r"\{(\w+)\}")


def option_label_placeholders(template: str) -> list[str]:
    """Column names referenced by an ``option_label`` format string."""
    return _FORMAT_TOKEN.findall(str(template or ""))


def format_record_option_label(record: Any, template: str) -> str:
    """Render ``{column}`` placeholders from a model instance or dict."""

    def _value(key: str) -> str:
        if isinstance(record, dict):
            raw = record.get(key)
        else:
            raw = getattr(record, key, None)
        return "" if raw is None else str(raw)

    return _FORMAT_TOKEN.sub(lambda m: _value(m.group(1)), str(template or ""))


def resolve_related_model(
    *,
    relationship_name: str | None,
    related_model: type[Any] | None,
    owner_model: type[Any] | None,
) -> type[Any] | None:
    """Return the related ORM model class for a Select relationship."""
    if related_model is not None and isinstance(related_model, type):
        return related_model
    if owner_model is None or not relationship_name:
        return None
    try:
        parent = owner_model()
    except Exception:
        return None
    method = getattr(parent, relationship_name, None)
    if not callable(method):
        return None
    try:
        relation = method()
    except TypeError:
        try:
            relation = method(parent)
        except Exception:
            return None
    except Exception:
        return None
    related = getattr(relation, "related", None)
    return related if isinstance(related, type) else None


def _record_key(record: Any) -> str | None:
    rid = getattr(record, "id", None)
    if rid is None and isinstance(record, dict):
        rid = record.get("id")
    if rid is None:
        return None
    return str(rid)


def _record_label(
    record: Any,
    title_attribute: str,
    get_option_label: Callable[..., Any] | None = None,
    option_label: str | None = None,
) -> str:
    if get_option_label is not None:
        try:
            return str(get_option_label(record) or "")
        except Exception:
            pass
    if option_label:
        return format_record_option_label(record, option_label)
    if isinstance(record, dict):
        return str(record.get(title_attribute) or record.get("id") or "")
    return str(getattr(record, title_attribute, None) or getattr(record, "id", "") or "")


def _run_coro(coro: Any) -> Any:
    """Run an async ORM query from sync Select render / AJAX handlers."""
    import asyncio
    import concurrent.futures

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


async def _fetch_rows(
    model: type[Any],
    *,
    title_attribute: str,
    search: str | None,
    search_columns: Sequence[str] | None,
    limit: int,
    modify_query: Callable[..., Any] | None,
    keys: Sequence[Any] | None = None,
) -> list[Any]:
    query = model.query()
    if modify_query is not None:
        modified = (
            modify_query(query, search) if _accepts_search(modify_query) else modify_query(query)
        )
        if modified is not None:
            query = modified
    if keys is not None:
        key_list = [k for k in keys if k not in (None, "")]
        if not key_list:
            return []
        pk = getattr(model, "primary_key", "id") or "id"
        query = query.where_in(pk, key_list)
    elif search:
        cols = list(search_columns) if search_columns else [title_attribute]
        pattern = f"%{search}%"
        first, *rest = cols
        query = query.where_like(first, pattern)
        for col in rest:
            query = query.or_where_like(col, pattern)
    try:
        query = query.order_by(title_attribute)
    except Exception:
        pass
    try:
        query = query.limit(limit)
    except Exception:
        pass
    rows = await query.get()
    if rows is None:
        return []
    if hasattr(rows, "all"):
        return list(rows.all())
    return list(rows)


def _accepts_search(fn: Callable[..., Any]) -> bool:
    try:
        import inspect

        params = list(inspect.signature(fn).parameters.values())
        return len(params) >= 2
    except Exception:
        return False


def load_relationship_options(
    *,
    model: type[Any],
    title_attribute: str,
    search: str | None = None,
    search_columns: Sequence[str] | None = None,
    limit: int = DEFAULT_OPTIONS_LIMIT,
    modify_query: Callable[..., Any] | None = None,
    get_option_label: Callable[..., Any] | None = None,
    option_label: str | None = None,
    keys: Sequence[Any] | None = None,
) -> dict[str, str]:
    """Synchronously load ``{id: label}`` options."""
    try:
        rows = _run_coro(
            _fetch_rows(
                model,
                title_attribute=title_attribute,
                search=search,
                search_columns=search_columns,
                limit=limit,
                modify_query=modify_query,
                keys=keys,
            )
        )
    except Exception:
        return {}
    out: dict[str, str] = {}
    for record in rows or []:
        key = _record_key(record)
        if key is None:
            continue
        out[key] = _record_label(
            record,
            title_attribute,
            get_option_label=get_option_label,
            option_label=option_label,
        )
    return out


def relationship_should_ajax(rel: dict[str, Any], *, searchable: bool) -> bool:
    """Searchable relationship without preload → server search (Filament default)."""
    return bool(searchable and not rel.get("preload"))
