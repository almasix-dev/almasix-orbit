"""Render hooks and panel plugin protocol."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

HookCallback = Callable[..., str]

_HOOKS: dict[str, list[tuple[str | None, HookCallback]]] = {}

# Common panel positions (Filament-inspired)
PANEL_HOOKS = (
    "panels::head.start",
    "panels::head.end",
    "panels::body.start",
    "panels::body.end",
    "panels::sidebar.nav.start",
    "panels::sidebar.nav.end",
    "panels::topbar.start",
    "panels::topbar.end",
    "panels::content.start",
    "panels::content.end",
    "panels::global-search.before",
    "panels::global-search.after",
    "panels::user-menu.before",
    "panels::user-menu.after",
    "panels::scripts.after",
    "panels::styles.after",
)


def register_render_hook(
    name: str,
    callback: HookCallback,
    *,
    scopes: list[str] | None = None,
) -> None:
    """Register HTML injected at ``name``. Optional scopes limit to page/resource ids."""
    bucket = _HOOKS.setdefault(name, [])
    if scopes:
        for scope in scopes:
            bucket.append((scope, callback))
    else:
        bucket.append((None, callback))


def clear_render_hooks() -> None:
    _HOOKS.clear()


def render_hook(name: str, *, scope: str | None = None, **ctx: Any) -> str:
    parts: list[str] = []
    for hook_scope, callback in _HOOKS.get(name, []):
        if hook_scope is not None and hook_scope != scope:
            continue
        parts.append(str(callback(**ctx) or ""))
    return "".join(parts)


class PanelPlugin(Protocol):
    def get_id(self) -> str: ...

    def register(self, panel: Any) -> None: ...

    def boot(self, panel: Any) -> None: ...


class Plugin:
    """Base plugin with no-op register/boot."""

    def __init__(self, plugin_id: str) -> None:
        self._id = plugin_id

    def get_id(self) -> str:
        return self._id

    def register(self, panel: Any) -> None:
        return None

    def boot(self, panel: Any) -> None:
        return None
