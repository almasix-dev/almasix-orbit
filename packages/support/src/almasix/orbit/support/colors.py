"""Orbit semantic color tokens and generated shade palettes."""

from __future__ import annotations

from enum import StrEnum

_LIGHT_MIX = {50: 0.95, 100: 0.9, 200: 0.75, 300: 0.55, 400: 0.3}
_DARK_MIX = {600: 0.15, 700: 0.35, 800: 0.5, 900: 0.65, 950: 0.82}


def _parse_hex(value: str) -> tuple[int, int, int]:
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise ValueError(value)
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def _mix(rgb: tuple[int, int, int], toward: tuple[int, int, int], amount: float) -> str:
    mixed = tuple(int(rgb[i] + (toward[i] - rgb[i]) * amount) for i in range(3))
    return "#{:02x}{:02x}{:02x}".format(*mixed)


class Color(StrEnum):
    DANGER = "danger"
    GRAY = "gray"
    INFO = "info"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"


class Colors:
    """Resolve semantic color → hex, CSS class, CSS variable, or 50–950 palette."""

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

    @classmethod
    def css_var(cls, color: Color | str, shade: int = 500) -> str:
        name = color.value if isinstance(color, Color) else str(color)
        return f"var(--or-{name}-{int(shade)})"

    @classmethod
    def palette(cls, color: Color | str) -> dict[int, str]:
        """Return 50–950 shades. ``500`` is the source hex; lighter shades mix
        toward white, darker toward black."""
        hex_value = cls.hex(color)
        try:
            rgb = _parse_hex(hex_value)
        except ValueError:
            return {500: str(hex_value)}
        shades: dict[int, str] = {500: f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"}
        for shade, amount in _LIGHT_MIX.items():
            shades[shade] = _mix(rgb, (255, 255, 255), amount)
        for shade, amount in _DARK_MIX.items():
            shades[shade] = _mix(rgb, (0, 0, 0), amount)
        return dict(sorted(shades.items()))
