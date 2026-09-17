"""Resolve panel brand/semantic colors for shell CSS injection."""

from __future__ import annotations

from collections.abc import Mapping

from almasix.orbit.support.colors import Color, Colors

# Keys that map 1:1 to ``--or-{key}`` CSS variables.
PANEL_COLOR_KEYS: frozenset[str] = frozenset(c.value for c in Color)

DEFAULT_PRIMARY = Colors.MAP[Color.PRIMARY]


def normalize_panel_color(value: Color | str) -> str:
    """Accept a ``Color``, semantic name, or raw CSS color string."""
    return Colors.hex(value)


def resolve_panel_color_vars(
    colors: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build ``--or-*`` CSS custom properties from a panel color map.

    Always includes ``--or-primary`` (default Orbit orange when unset).
    Other semantic keys (``danger``, ``success``, …) are emitted only when set.
    """
    raw = dict(colors or {})
    primary = normalize_panel_color(raw.get("primary") or DEFAULT_PRIMARY)
    vars_: dict[str, str] = {"--or-primary": primary}

    for key, value in raw.items():
        name = key.value if isinstance(key, Color) else str(key)
        if name == "primary" or name not in PANEL_COLOR_KEYS:
            continue
        vars_[f"--or-{name}"] = normalize_panel_color(value)
    return vars_
