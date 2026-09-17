"""Global search configuration helpers for resources and panels."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e


def search_records(
    records: Sequence[Any],
    term: str,
    *,
    attributes: Sequence[str],
) -> list[Any]:
    needle = term.casefold().strip()
    if not needle:
        return list(records)
    out = []
    for record in records:
        for attr in attributes:
            value = record.get(attr) if isinstance(record, dict) else getattr(record, attr, None)
            if value is not None and needle in str(value).casefold():
                out.append(record)
                break
    return out


def render_global_search_results(
    results: Sequence[dict[str, Any]],
    *,
    limit: int = 10,
) -> str:
    items = []
    for row in list(results)[:limit]:
        title = e(row.get("title", ""))
        url = e(row.get("url", "#"))
        details = row.get("details") or {}
        detail_html = "".join(
            f'<span class="or-gs-detail"><strong>{e(k)}</strong> {e(v)}</span>'
            for k, v in details.items()
        )
        items.append(
            f'<a class="or-gs-result" href="{url}"><span class="or-gs-title">{title}</span>'
            f'<span class="or-gs-details">{detail_html}</span></a>'
        )
    body = "".join(items) or '<p class="or-gs-empty">No results</p>'
    return f'<div class="or-global-search-results">{body}</div>'


def render_global_search_input(*, debounce_ms: int = 300) -> str:
    return (
        '<div class="or-global-search" x-data="{ q: \'\' }">'
        f'<input class="or-input or-global-search-input" type="search" placeholder="Search…" '
        f'wire:model.live.debounce.{debounce_ms}ms="globalSearch" x-model="q" />'
        '<div class="or-global-search-panel" wire:ignore.self></div></div>'
    )


def build_result(
    *,
    title: str | Callable[..., str],
    url: str | Callable[..., str],
    details: dict[str, Any] | Callable[..., dict[str, Any]] | None = None,
    **ctx: Any,
) -> dict[str, Any]:
    return {
        "title": evaluate(title, **ctx),
        "url": evaluate(url, **ctx),
        "details": evaluate(details, **ctx) if details is not None else {},
    }
