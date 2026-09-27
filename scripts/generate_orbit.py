#!/usr/bin/env python3
"""Generate almasix-orbit package sources (run once during bootstrap)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def w(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    text = content if content.endswith("\n") else content + "\n"
    path.write_text(text)


def pkg_toml(
    name: str,
    desc: str,
    deps: list[str],
    package_dir: str,
    entry: str | None = None,
) -> str:
    deps_s = ",\n    ".join(f'"{d}"' for d in deps)
    ep = ""
    if entry:
        ep = f'''
[project.entry-points."almasix.providers"]
orbit = "{entry}"
'''
    return f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
description = "{desc}"
requires-python = ">=3.11"
license = "MIT"
authors = [{{ name = "Almasix Contributors" }}]
dependencies = [
    {deps_s},
]
{ep}
[project.urls]
Homepage = "https://github.com/almasix-dev/almasix-orbit"
Documentation = "https://orbit.almasix.com/"
Repository = "https://github.com/almasix-dev/almasix-orbit"

[tool.hatch.build.targets.wheel]
packages = ["src/almasix"]

[tool.hatch.build.targets.sdist]
include = ["/src/almasix", "/README.md"]
'''


# ---------------------------------------------------------------------------
# support
# ---------------------------------------------------------------------------

w(
    "packages/support/pyproject.toml",
    pkg_toml(
        "almasix-orbit-support",
        "Shared Orbit UI utilities, icons, colors, and components",
        ["almasix>=0.6.0"],
        "support",
    ),
)

w(
    "packages/support/src/almasix/__init__.py",
    '"""Namespace package for Almasix."""\n__path__ = __import__("pkgutil").extend_path(__path__, __name__)\n',
)

w(
    "packages/support/src/almasix/orbit/__init__.py",
    '''"""Orbit — Filament-power for Almasix."""

__all__ = ["__version__"]
__version__ = "0.5.0"
''',
)

w(
    "packages/support/src/almasix/orbit/support/__init__.py",
    '''"""Orbit support — fluent components, icons, colors, HTML helpers."""

from almasix.orbit.support.colors import Color, Colors
from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e, tag
from almasix.orbit.support.icons import Heroicon, icon

__all__ = [
    "Color",
    "Colors",
    "Component",
    "Heroicon",
    "e",
    "icon",
    "tag",
]
''',
)

w(
    "packages/support/src/almasix/orbit/support/component.py",
    '''"""Fluent SDUI component base (Filament-style ``make`` + chained configurators)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self, TypeVar

T = TypeVar("T", bound="Component")


class Component:
    """Base configuration object for Orbit schemas, fields, columns, and entries."""

    def __init__(self, name: str | None = None) -> None:
        self._name = name
        self._label: str | None = None
        self._hidden = False
        self._visible: bool | Callable[..., bool] = True
        self._disabled: bool | Callable[..., bool] = False
        self._extra_attributes: dict[str, Any] = {}
        self._view: str | None = None
        self._column_span: int | str | None = None
        self._live = False
        self._dehydrated = True
        self._state_path: str | None = None
        self._default: Any = None
        self._helper_text: str | None = None
        self._hint: str | None = None
        self._hint_icon: str | None = None

    @classmethod
    def make(cls, name: str | None = None) -> Self:
        return cls(name)

    def get_name(self) -> str | None:
        return self._name

    def label(self, label: str | None) -> Self:
        self._label = label
        return self

    def get_label(self) -> str:
        if self._label is not None:
            return self._label
        if not self._name:
            return ""
        return self._name.replace("_", " ").replace(".", " ").title()

    def hidden(self, condition: bool = True) -> Self:
        self._hidden = condition
        return self

    def visible(self, condition: bool | Callable[..., bool] = True) -> Self:
        self._visible = condition
        return self

    def disabled(self, condition: bool | Callable[..., bool] = True) -> Self:
        self._disabled = condition
        return self

    def is_hidden(self) -> bool:
        return self._hidden

    def is_visible(self, **ctx: Any) -> bool:
        if self._hidden:
            return False
        v = self._visible
        return bool(v(**ctx) if callable(v) else v)

    def is_disabled(self, **ctx: Any) -> bool:
        d = self._disabled
        return bool(d(**ctx) if callable(d) else d)

    def extra_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_attributes.update(attrs)
        return self

    def get_extra_attributes(self) -> dict[str, Any]:
        return dict(self._extra_attributes)

    def view(self, view: str) -> Self:
        self._view = view
        return self

    def get_view(self) -> str | None:
        return self._view

    def column_span(self, span: int | str) -> Self:
        self._column_span = span
        return self

    def live(self, condition: bool = True) -> Self:
        self._live = condition
        return self

    def dehydrated(self, condition: bool = True) -> Self:
        self._dehydrated = condition
        return self

    def is_dehydrated(self) -> bool:
        return self._dehydrated

    def state_path(self, path: str) -> Self:
        self._state_path = path
        return self

    def get_state_path(self) -> str | None:
        return self._state_path or self._name

    def default(self, value: Any) -> Self:
        self._default = value
        return self

    def get_default(self) -> Any:
        return self._default

    def helper_text(self, text: str) -> Self:
        self._helper_text = text
        return self

    def hint(self, text: str) -> Self:
        self._hint = text
        return self

    def hint_icon(self, icon_name: str) -> Self:
        self._hint_icon = icon_name
        return self

    def configure(self, callback: Callable[[Self], Any]) -> Self:
        callback(self)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": type(self).__name__,
            "name": self._name,
            "label": self.get_label(),
            "hidden": self._hidden,
            "live": self._live,
            "dehydrated": self._dehydrated,
            "state_path": self.get_state_path(),
            "default": self._default,
            "helper_text": self._helper_text,
            "hint": self._hint,
            "column_span": self._column_span,
            "extra_attributes": self._extra_attributes,
        }

    def render(self, state: Any = None, **ctx: Any) -> str:
        """Default HTML render — subclasses override for richer markup."""
        from almasix.orbit.support.html import e, tag

        if not self.is_visible(**ctx):
            return ""
        label = e(self.get_label())
        name = e(self.get_state_path() or "")
        value = "" if state is None else e(str(state))
        disabled = " disabled" if self.is_disabled(**ctx) else ""
        return (
            f'<div class="or-field" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<input class="or-input" id="or-{name}" name="{name}" '
            f'value="{value}"{disabled} />'
            f"</div>"
        )


def schema_components(components: Sequence[Component]) -> list[dict[str, Any]]:
    return [c.to_dict() for c in components]
''',
)

w(
    "packages/support/src/almasix/orbit/support/html.py",
    '''"""Minimal HTML helpers for Orbit renders."""

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
''',
)

w(
    "packages/support/src/almasix/orbit/support/colors.py",
    '''"""Orbit color tokens (Filament-style named colors)."""

from __future__ import annotations

from enum import Enum


class Color(str, Enum):
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
''',
)

w(
    "packages/support/src/almasix/orbit/support/icons.py",
    '''"""Heroicons (outline) shipped as inline SVG for Orbit."""

from __future__ import annotations

from almasix.orbit.support.html import e

# Minimal curated set; extend as needed. Paths from Heroicons v2 MIT.
_ICONS: dict[str, str] = {
    "heroicon-o-users": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 '
        "4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113"
        "-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 "
        "21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 "
        "11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 "
        '6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z"/>'
    ),
    "heroicon-o-home": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m2.25 12 8.954-8.955a1.126 1.126 0 0 1 1.591 0L21.75 12M4.5 '
        "9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504"
        "-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c"
        '.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>'
    ),
    "heroicon-o-cog-6-tooth": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 '
        "1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22"
        ".127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 "
        "1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c"
        "-.293.24-.438.613-.431.992a7.723 7.723 0 0 1 0 .255c-.007.378"
        ".138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 "
        "2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75"
        "-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495"
        "-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 "
        "0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644"
        "-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124"
        "l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 "
        "1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6"
        ".932 6.932 0 0 1 0-.255c.007-.378-.138-.75-.43-.99l-1.004"
        "-.828a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 "
        "1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044"
        ".146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281Z"/>'
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>'
    ),
    "heroicon-o-bell": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 '
        "0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 "
        "6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 "
        "0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0"/>'
    ),
    "heroicon-o-plus": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M12 4.5v15m7.5-7.5h-15"/>'
    ),
    "heroicon-o-pencil-square": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 '
        "19.82a4.5 4.5 0 0 1-1.897 1.13l-10.976.274 2.652-2.652L16.862 "
        '4.487Zm0 0L19.5 7.125"/>'
    ),
    "heroicon-o-trash": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 '
        "1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084"
        "a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 "
        "0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 "
        "0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 "
        "51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 "
        '48.667 0 0 0-7.5 0"/>'
    ),
    "heroicon-o-magnifying-glass": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 '
        '10.607 10.607Z"/>'
    ),
    "heroicon-o-x-mark": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M6 18 18 6M6 6l12 12"/>'
    ),
    "heroicon-o-check": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m4.5 12.75 6 6 9-13.5"/>'
    ),
    "heroicon-o-information-circle": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 '
        "0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9"
        '-3.75h.008v.008H12V8.25Z"/>'
    ),
}


def icon(name: str, *, size: int = 20, css_class: str = "or-icon") -> str:
    path = _ICONS.get(name)
    if path is None:
        return f'<span class="{e(css_class)}" data-missing-icon="{e(name)}"></span>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" '
        f'stroke-width="1.5" stroke="currentColor" width="{size}" height="{size}" '
        f'class="{e(css_class)}" aria-hidden="true">{path}</svg>'
    )


class Heroicon:
    """Filament-style icon name helper."""

    @staticmethod
    def outline(name: str) -> str:
        key = name if name.startswith("heroicon-") else f"heroicon-o-{name}"
        return key

    @staticmethod
    def render(name: str, **kwargs: int | str) -> str:
        key = Heroicon.outline(name)
        size = int(kwargs.get("size", 20))
        css = str(kwargs.get("css_class", "or-icon"))
        return icon(key, size=size, css_class=css)

    @staticmethod
    def available() -> list[str]:
        return sorted(_ICONS)
''',
)

print("support written")
