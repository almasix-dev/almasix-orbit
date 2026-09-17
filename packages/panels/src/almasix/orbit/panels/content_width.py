"""Resolve panel/resource content max-width (Shamar-compatible tokens)."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_CONTENT_MAX_WIDTH = "screen-2xl"

# Tailwind-ish tokens → CSS max-width
_TOKEN_CSS: dict[str, str] = {
    "xs": "20rem",
    "sm": "24rem",
    "md": "28rem",
    "lg": "32rem",
    "xl": "36rem",
    "2xl": "42rem",
    "3xl": "48rem",
    "4xl": "56rem",
    "5xl": "64rem",
    "6xl": "72rem",
    "7xl": "80rem",
    "prose": "65ch",
    "full": "100%",
    "none": "none",
    "screen-sm": "40rem",
    "screen-md": "48rem",
    "screen-lg": "64rem",
    "screen-xl": "80rem",
    "screen-2xl": "96rem",
    "screen": "80rem",
}


@dataclass(frozen=True)
class ContentMaxWidthResolved:
    """Resolved content width for shell injection."""

    css_value: str
    token: str


def resolve_content_max_width(value: str | None = None) -> ContentMaxWidthResolved:
    """Accept Shamar-style tokens, ``max-w-*`` classes, or raw CSS lengths."""
    raw = (value or DEFAULT_CONTENT_MAX_WIDTH).strip()
    if not raw:
        raw = DEFAULT_CONTENT_MAX_WIDTH

    if raw.startswith("max-w-"):
        token = raw.removeprefix("max-w-")
        if token in _TOKEN_CSS:
            return ContentMaxWidthResolved(css_value=_TOKEN_CSS[token], token=token)
        return ContentMaxWidthResolved(css_value="none", token=raw)

    if raw in _TOKEN_CSS:
        return ContentMaxWidthResolved(css_value=_TOKEN_CSS[raw], token=raw)

    # CSS length (80rem, 1200px, 90%, …)
    return ContentMaxWidthResolved(css_value=raw, token="custom")
