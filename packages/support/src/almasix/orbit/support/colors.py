"""Orbit color tokens (Filament-style named colors)."""

from __future__ import annotations

from enum import StrEnum


class Color(StrEnum):
    DANGER = "danger"
    GRAY = "gray"
    INFO = "info"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"


class Colors:
    """Resolve semantic color → CSS variable / class fragment."""

    MAP = {
        Color.DANGER: "#ef4444",
        Color.GRAY: "#6b7280",
        Color.INFO: "#3b82f6",
        Color.PRIMARY: "#f1511b",
        Color.SUCCESS: "#22c55e",
        Color.WARNING: "#f59e0b",
    }

    @classmethod
    def hex(cls, color: Color | str) -> str:
        if isinstance(color, Color):
            return cls.MAP[color]
        try:
            return cls.MAP[Color(color)]
        except ValueError:
            return str(color)

    @classmethod
    def css_class(cls, color: Color | str) -> str:
        name = color.value if isinstance(color, Color) else str(color)
        return f"or-color-{name}"
