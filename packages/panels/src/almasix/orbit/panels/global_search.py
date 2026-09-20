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


def render_global_search_groups(groups: Sequence[dict[str, Any]]) -> str:
    """Results grouped per resource — ``[{"label": …, "results": [...]}, …]``."""
    sections: list[str] = []
    for group in groups:
        results = list(group.get("results") or [])
        if not results:
            continue
        sections.append(
            f'<div class="or-gs-group"><p class="or-gs-group-label">{e(group.get("label", ""))}</p>'
            f"{render_global_search_results(results, limit=len(results))}</div>"
        )
    if not sections:
        return '<div class="or-global-search-results"><p class="or-gs-empty">No results</p></div>'
    return "".join(sections)


def collect_global_search_results(
    panel: Any,
    term: str,
    *,
    user: Any = None,
    records_by_resource: dict[Any, Sequence[Any]] | None = None,
) -> list[dict[str, Any]]:
    """Search every globally searchable resource on ``panel``.

    ``records_by_resource`` supplies the rows to search (the panel route loads
    them from the ORM or from a resource's seed list before calling this).
    """
    needle = str(term or "").strip()
    if not needle:
        return []
    groups: list[dict[str, Any]] = []
    for resource in panel.get_resources():
        searchable = getattr(resource, "is_globally_searchable", None)
        if not callable(searchable) or not searchable():
            continue
        if user is not None and not resource.can_view_any(user):
            continue
        records = (records_by_resource or {}).get(resource)
        if records is None:
            getter = getattr(resource, "get_records", None)
            records = list(getter()) if callable(getter) else []
        results = resource.get_global_search_results(needle, records)
        if results:
            groups.append(
                {
                    "resource": resource,
                    "label": resource.get_plural_model_label(),
                    "results": results,
                }
            )
    return groups


def render_global_search_input(
    *,
    debounce_ms: int = 300,
    endpoint: str | None = None,
    placeholder: str = "Search…",
) -> str:
    """Topbar search box.

    With ``endpoint`` the box fetches server-rendered results from the panel's
    global-search route; without one it binds to a ``globalSearch`` host property.
    """
    if endpoint is None:
        return (
            '<div class="or-global-search" x-data="{ q: \'\' }">'
            f'<input class="or-input or-global-search-input" type="search" placeholder="{e(placeholder)}" '
            f'wire:model.live.debounce.{debounce_ms}ms="globalSearch" x-model="q" />'
            '<div class="or-global-search-panel" wire:ignore.self></div></div>'
        )
    state = (
        "{ q: '', open: false, html: '', timer: null, "
        "search() { clearTimeout(this.timer); "
        "if (this.q.trim().length < 2) { this.open = false; this.html = ''; return; } "
        f"this.timer = setTimeout(() => fetch('{endpoint}?search=' + encodeURIComponent(this.q))"
        ".then(r => r.text()).then(html => { this.html = html; this.open = true; })"
        f", {int(debounce_ms)}); }} }}"
    )
    return (
        f'<div class="or-global-search" data-orbit-global-search x-data="{e(state)}" '
        '@click.outside="open = false" @keydown.escape.window="open = false">'
        f'<input class="or-input or-global-search-input" type="search" placeholder="{e(placeholder)}" '
        'x-model="q" @input="search()" @focus="q.trim().length > 1 && (open = true)" />'
        '<div class="or-global-search-panel" x-show="open" x-cloak x-html="html"></div>'
        "</div>"
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
