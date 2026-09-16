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
