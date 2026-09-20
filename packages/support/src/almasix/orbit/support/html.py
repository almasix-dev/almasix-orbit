"""Minimal HTML helpers for Orbit renders."""

from __future__ import annotations

import html
from typing import Any


class HtmlString(str):
    """Trusted HTML fragment that ``e()`` will not escape.

    Use for helper text, hints, or labels that already contain markup. Anything
    that implements ``__html__`` is treated the same way.
    """

    def __html__(self) -> str:
        return str.__str__(self)


def e(value: Any) -> str:
    if value is None:
        return ""
    html_fn = getattr(value, "__html__", None)
    if callable(html_fn):
        return str(html_fn())
    return html.escape(str(value), quote=True)


def classes(*parts: Any) -> str:
    """Join CSS class tokens, skipping falsy entries.

    Dicts are treated as ``{class_name: include?}`` maps.
    """
    bits: list[str] = []
    for part in parts:
        if part is True or not part:
            continue
        if isinstance(part, dict):
            bits.extend(str(name) for name, on in part.items() if on)
            continue
        token = str(part).strip()
        if token:
            bits.append(token)
    return " ".join(bits)


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
