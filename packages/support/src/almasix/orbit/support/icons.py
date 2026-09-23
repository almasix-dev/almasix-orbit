"""Heroicons (outline) shipped as inline SVG for Orbit."""

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
    "heroicon-o-document-text": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 '
        "1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 "
        "12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 "
        "1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 "
        '1.125-1.125V11.25a9 9 0 0 0-9-9Z"/>'
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
        '.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281Z"/>'
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>'
    ),
    "heroicon-o-bell": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 '
        "0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 "
        "6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 "
        '0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0"/>'
    ),
    "heroicon-o-sun": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591'
        "-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 "
        '5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z"/>'
    ),
    "heroicon-o-moon": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75'
        "-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 "
        '7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z"/>'
    ),
    "heroicon-o-computer-desktop": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M9 17.25v1.007a1.5 1.5 0 0 1-.4 1.027l-.44.46A.75.75 0 0 0 '
        "9.25 21h5.5a.75.75 0 0 0 .59-1.256l-.44-.46a1.5 1.5 0 0 1-.4-1.027V17.25"
        "m6.75-12v9.75A2.25 2.25 0 0 1 18.75 17.25H5.25A2.25 2.25 0 0 1 3 "
        "15V5.25m18 0A2.25 2.25 0 0 0 18.75 3H5.25A2.25 2.25 0 0 0 3 5.25m18 "
        '0V12a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 12V5.25"/>'
    ),
    "heroicon-o-bars-3": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"/>'
    ),
    "heroicon-o-chevron-down": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m19.5 8.25-7.5 7.5-7.5-7.5"/>'
    ),
    "heroicon-o-chevron-up": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m4.5 15.75 7.5-7.5 7.5 7.5"/>'
    ),
    "heroicon-o-chevron-left": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M15.75 19.5 8.25 12l7.5-7.5"/>'
    ),
    "heroicon-o-chevron-right": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m8.25 4.5 7.5 7.5-7.5 7.5"/>'
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
    "heroicon-o-check-circle": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>'
    ),
    "heroicon-o-exclamation-triangle": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 '
        "0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 "
        '0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"/>'
    ),
    "heroicon-o-x-circle": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 '
        '18 0Z"/>'
    ),
    "heroicon-o-information-circle": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 '
        "0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9"
        '-3.75h.008v.008H12V8.25Z"/>'
    ),
    "heroicon-o-funnel": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044'
        "a2.25 2.25 0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 "
        "1.591v2.927a2.25 2.25 0 0 1-1.244 2.03l-2.25 1.125a.75.75 0 0 "
        "1-1.072-.71v-4.372a2.25 2.25 0 0 0-.659-1.591L2.659 6.41A2.25 "
        "2.25 0 0 1 2 4.819V3.774c0-.54.384-1.006.917-1.096A48.32 48.32 "
        '0 0 1 12 3Z"/>'
    ),
    "heroicon-o-view-columns": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M9 4.5v15m6-15v15m-10.875 0h15.75c.621 0 1.125-.504 '
        "1.125-1.125V5.625c0-.621-.504-1.125-1.125-1.125H4.125C3.504 "
        '4.5 3 5.004 3 5.625v12.75c0 .621.504 1.125 1.125 1.125Z"/>'
    ),
    "heroicon-o-rectangle-stack": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M6 6.878V6a2.25 2.25 0 0 1 2.25-2.25h7.5A2.25 2.25 0 0 1 '
        "18 6v.878m-12 0c.235-.083.487-.128.75-.128h10.5c.263 0 .515.045"
        ".75.128m-12 0A2.25 2.25 0 0 0 4.5 9v.878m13.5-3A2.25 2.25 0 0 1 "
        "19.5 9v.878m0 0a2.246 2.246 0 0 0-.75-.128H5.25c-.263 0-.515.045"
        "-.75.128m15 0A2.25 2.25 0 0 1 21 12v6a2.25 2.25 0 0 1-2.25 "
        "2.25H5.25A2.25 2.25 0 0 1 3 18v-6c0-.98.626-1.813 1.5-2.122\"/>"
    ),
    "heroicon-o-user-group": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m'
        ".94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 "
        "12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 "
        "18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 "
        "12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 "
        "2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 "
        "3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 "
        "1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 "
        '2.25 2.25 0 0 1 4.5 0Z"/>'
    ),
    "heroicon-o-musical-note": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="m9 9 10.5-3m0 6.553v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32'
        ".377a1.803 1.803 0 1 1-.99-3.467l2.31-.66a2.25 2.25 0 0 0 "
        "1.632-2.163Zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 0 "
        "1-1.632 2.163l-1.32.377a1.803 1.803 0 0 1-.99-3.467l2.31-.66A"
        '2.25 2.25 0 0 0 9 15.553Z"/>'
    ),
    "heroicon-o-chart-bar": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 '
        "1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 "
        "1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 "
        "1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621"
        "-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125"
        "V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 "
        "3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 "
        "1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z\"/>"
    ),
    "heroicon-o-arrow-up-tray": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75'
        "V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5\"/>"
    ),
    "heroicon-o-arrow-down-tray": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75'
        "V16.5M12 3v12.75m0 0-4.5-4.5M12 15.75l4.5-4.5\"/>"
    ),
    "heroicon-o-ellipsis-vertical": (
        '<path stroke-linecap="round" stroke-linejoin="round" '
        'd="M12 6.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 12.75a.75.75 '
        "0 1 1 0-1.5.75.75 0 0 1 0 1.5ZM12 18.75a.75.75 0 1 1 0-1.5.75.75 "
        '0 0 1 0 1.5Z"/>'
    ),
}


_ALIASES: dict[str, str] = {}


def register_icon(alias: str, name: str) -> None:
    """Map a semantic alias (``actions::delete``) to a Heroicon name."""
    _ALIASES[alias] = name


def reset_icon_aliases() -> None:
    _ALIASES.clear()


def resolve_icon_name(name: str) -> str:
    return _ALIASES.get(name, name)


def has_icon(name: str | None) -> bool:
    """True when ``name`` resolves to a shipped outline Heroicon path."""
    if not name:
        return False
    return resolve_icon_name(str(name)) in _ICONS


def icon(name: str, *, size: int = 20, css_class: str = "or-icon") -> str:
    name = resolve_icon_name(name)
    path = _ICONS.get(name)
    if path is None:
        return f'<span class="{e(css_class)}" data-missing-icon="{e(name)}"></span>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" '
        f'stroke-width="1.5" stroke="currentColor" width="{size}" height="{size}" '
        f'class="{e(css_class)}" aria-hidden="true">{path}</svg>'
    )


class Heroicon:
    """Name helper for outline Heroicons shipped with Orbit."""

    @staticmethod
    def outline(name: str) -> str:
        name = resolve_icon_name(name)
        if name.startswith("heroicon-"):
            return name
        return f"heroicon-o-{name}"

    @staticmethod
    def alias(name: str, target: str) -> None:
        register_icon(name, target)

    @staticmethod
    def reset_aliases() -> None:
        reset_icon_aliases()

    @staticmethod
    def render(name: str, **kwargs: int | str) -> str:
        key = Heroicon.outline(name)
        size = int(kwargs.get("size", 20))
        css = str(kwargs.get("css_class", "or-icon"))
        return icon(key, size=size, css_class=css)

    @staticmethod
    def available() -> list[str]:
        return sorted(_ICONS)
