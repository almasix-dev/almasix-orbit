"""Panel — admin shell registration (Filament Panel analogue)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon


class Panel:
    def __init__(self, panel_id: str = "admin") -> None:
        self.id = panel_id
        self._path = f"/{panel_id}"
        self._brand = "Orbit"
        self._brand_logo: str | None = None
        self._font = "Outfit"
        self._colors: dict[str, str] = {"primary": "#f1511b"}
        self._resources: list[type[Any]] = []
        self._pages: list[type[Any]] = []
        self._widgets: list[type[Any]] = []
        self._middleware: list[Any] = ["auth", "permission"]
        self._login: bool = True
        self._auth_guard: str | None = None
        self._plugin_callbacks: list[Callable[[Panel], Any]] = []
        self._dark_mode = True
        self._sidebar_collapsible = True
        self._discover_resources_in: list[str] = []
        self._discover_pages_in: list[str] = []
        self._discover_widgets_in: list[str] = []

    @classmethod
    def make(cls, panel_id: str = "admin") -> Panel:
        return cls(panel_id)

    def path(self, path: str) -> Self:
        self._path = path if path.startswith("/") else f"/{path}"
        return self

    def brand_name(self, name: str) -> Self:
        self._brand = name
        return self

    def brand_logo(self, url: str) -> Self:
        self._brand_logo = url
        return self

    def font(self, family: str) -> Self:
        self._font = family
        return self

    def colors(self, **colors: str) -> Self:
        self._colors.update(colors)
        return self

    def resources(self, resources: Sequence[type[Any]]) -> Self:
        self._resources = list(resources)
        return self

    def pages(self, pages: Sequence[type[Any]]) -> Self:
        self._pages = list(pages)
        return self

    def widgets(self, widgets: Sequence[type[Any]]) -> Self:
        self._widgets = list(widgets)
        return self

    def middleware(self, middleware: Sequence[Any]) -> Self:
        self._middleware = list(middleware)
        return self

    def login(self, condition: bool = True) -> Self:
        self._login = condition
        return self

    def auth_guard(self, guard: str) -> Self:
        self._auth_guard = guard
        return self

    def dark_mode(self, condition: bool = True) -> Self:
        self._dark_mode = condition
        return self

    def sidebar_collapsible(self, condition: bool = True) -> Self:
        self._sidebar_collapsible = condition
        return self

    def discover_resources(self, *paths: str) -> Self:
        self._discover_resources_in.extend(paths)
        return self

    def discover_pages(self, *paths: str) -> Self:
        self._discover_pages_in.extend(paths)
        return self

    def discover_widgets(self, *paths: str) -> Self:
        self._discover_widgets_in.extend(paths)
        return self

    def plugin(self, callback: Callable[[Panel], Any]) -> Self:
        self._plugin_callbacks.append(callback)
        return self

    def get_path(self) -> str:
        return self._path

    def get_resources(self) -> list[type[Any]]:
        return list(self._resources)

    def get_pages(self) -> list[type[Any]]:
        return list(self._pages)

    def get_middleware(self) -> list[Any]:
        return list(self._middleware)

    def navigation_items(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for res in self._resources:
            items.append(
                {
                    "label": getattr(
                        res, "get_navigation_label", lambda r=res: r.__name__
                    )(),
                    "icon": getattr(res, "navigation_icon", "heroicon-o-users"),
                    "group": getattr(res, "navigation_group", None),
                    "url": (
                        f"{self._path}/"
                        f"{getattr(res, 'get_slug', lambda r=res: r.__name__.lower())()}"
                    ),
                    "sort": getattr(res, "navigation_sort", 0),
                }
            )
        for page in self._pages:
            items.append(
                {
                    "label": getattr(
                        page, "get_navigation_label", lambda p=page: p.__name__
                    )(),
                    "icon": getattr(page, "navigation_icon", "heroicon-o-home"),
                    "group": getattr(page, "navigation_group", None),
                    "url": (
                        f"{self._path}/"
                        f"{getattr(page, 'get_slug', lambda p=page: p.__name__.lower())()}"
                    ),
                    "sort": getattr(page, "navigation_sort", 0),
                }
            )
        items.sort(key=lambda i: i.get("sort") or 0)
        return items

    def render_shell(self, content: str, *, user: Any = None) -> str:
        nav = []
        for item in self.navigation_items():
            ic = render_icon(item["icon"]) if item.get("icon") else ""
            nav.append(
                f'<a class="or-nav-link" href="{e(item["url"])}">{ic}'
                f'<span>{e(item["label"])}</span></a>'
            )
        brand = e(self._brand)
        primary = e(self._colors.get("primary", "#f1511b"))
        font = e(self._font)
        nav_html = "".join(nav)
        return (
            "<!DOCTYPE html>\n"
            f'<html lang="en" data-orbit-panel="{e(self.id)}">\n'
            "<head>\n"
            '  <meta charset="utf-8" />\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            f"  <title>{brand}</title>\n"
            '  <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
            '  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet" />\n'
            '  <link rel="stylesheet" href="/vendor/orbit/orbit.css" />\n'
            f"  <style>:root {{ --or-font: '{font}', ui-sans-serif, system-ui, sans-serif; "
            f"--or-primary: {primary}; }}</style>\n"
            "</head>\n"
            '<body class="or-body">\n'
            '  <div class="or-app" x-data="{ sidebar: true }">\n'
            '    <aside class="or-sidebar">\n'
            f'      <div class="or-brand">{brand}</div>\n'
            f'      <nav class="or-nav">{nav_html}</nav>\n'
            "    </aside>\n"
            '    <div class="or-main">\n'
            '      <header class="or-topbar"><div class="or-topbar-end"></div></header>\n'
            f'      <main class="or-content">{content}</main>\n'
            "    </div>\n"
            "  </div>\n"
            '  <script src="/vendor/orbit/orbit.js"></script>\n'
            "</body>\n"
            "</html>"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "path": self._path,
            "brand": self._brand,
            "font": self._font,
            "colors": self._colors,
            "resources": [r.__name__ for r in self._resources],
            "pages": [p.__name__ for p in self._pages],
            "middleware": [str(m) for m in self._middleware],
        }


class PanelRegistry:
    def __init__(self) -> None:
        self._panels: dict[str, Panel] = {}

    def register(self, panel: Panel) -> Panel:
        self._panels[panel.id] = panel
        return panel

    def get(self, panel_id: str) -> Panel | None:
        return self._panels.get(panel_id)

    def all(self) -> list[Panel]:
        return list(self._panels.values())
