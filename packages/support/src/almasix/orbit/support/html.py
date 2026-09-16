"""Minimal HTML helpers for Orbit renders."""

from __future__ import annotations

import html
from typing import Any


def e(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def tag(
    name: str,
    content: str = "",
    *,
    attrs: dict[str, Any] | None = None,
    void: bool = False,
) -> str:
    parts: list[str] = []
    for key, val in (attrs or {}).items():
        if val is False or val is None:
            continue
        if val is True:
            parts.append(e(key))
        else:
            parts.append(f'{e(key)}="{e(val)}"')
    attr_s = (" " + " ".join(parts)) if parts else ""
    if void:
        return f"<{name}{attr_s} />"
    return f"<{name}{attr_s}>{content}</{name}>"
