"""Panel — admin shell registration (Filament Panel analogue)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.panels.navigation import (
    NavLayout,
    NavigationGroup,
    NavigationItem,
    build_menu_layout,
)
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
        self._custom_nav_items: list[NavigationItem] = []
        self._nav_groups: dict[str, NavigationGroup] = {}
        self._navigation_layout: NavLayout = "sidebar_topbar"

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

    def navigation_layout(self, layout: NavLayout) -> Self:
        self._navigation_layout = layout
        return self

    def navigation_items(self, items: Sequence[NavigationItem] | None = None) -> Any:
        """Register custom items when passed; otherwise return computed nav dicts."""
        if items is not None:
            self._custom_nav_items = list(items)
            return self
        return self._collect_navigation_items()

    def navigation_groups(self, groups: Sequence[NavigationGroup]) -> Self:
        for group in groups:
            name = group.get_name() or group.get_label()
            if name:
                self._nav_groups[name] = group
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

    def _collect_navigation_items(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for res in self._resources:
            items.append(
                {
                    "slug": getattr(res, "get_slug", lambda r=res: r.__name__.lower())(),
                    "label": getattr(
                        res, "get_navigation_label", lambda r=res: r.__name__
                    )(),
                    "icon": getattr(res, "navigation_icon", "heroicon-o-users"),
                    "group": getattr(res, "navigation_group", None),
                    "subgroup": getattr(res, "navigation_subgroup", None),
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
                    "slug": getattr(page, "get_slug", lambda p=page: p.__name__.lower())(),
                    "label": getattr(
                        page, "get_navigation_label", lambda p=page: p.__name__
                    )(),
                    "icon": getattr(page, "navigation_icon", "heroicon-o-home"),
                    "group": getattr(page, "navigation_group", None),
                    "subgroup": getattr(page, "navigation_subgroup", None),
                    "url": (
                        f"{self._path}/"
                        f"{getattr(page, 'get_slug', lambda p=page: p.__name__.lower())()}"
                    ),
                    "sort": getattr(page, "navigation_sort", 0),
                }
            )
        for item in self._custom_nav_items:
            items.append(item.to_nav_dict())
        items.sort(key=lambda i: (i.get("sort") or 0, i.get("label") or ""))
        return items

    def menu_layout_context(self, active_path: str | None = None) -> Any:
        return build_menu_layout(
            self._collect_navigation_items(),
            group_meta=self._nav_groups,
            active_path=active_path,
            layout=self._navigation_layout,
            panel_path=self._path,
        )

    def render_shell(
        self,
        content: str,
        *,
        user: Any = None,
        active_path: str | None = None,
    ) -> str:
        ctx = self.menu_layout_context(active_path=active_path)
        brand = e(self._brand)
        primary = e(self._colors.get("primary", "#f1511b"))
        font = e(self._font)
        collapsible = self._sidebar_collapsible

        sidebar_html = self._render_sidebar(ctx, collapsible)
        topbar_html = self._render_topbar(ctx)
        modal_html = _action_modal_html()
        app_class = "or-app"
        if ctx.layout == "sidebar_topbar":
            app_class += " or-app-split"
        if ctx.layout == "top":
            app_class += " or-app-top"

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
            f'  <div class="{app_class}" x-data="{{ sidebarOpen: true }}">\n'
            f"{sidebar_html}"
            '    <div class="or-main">\n'
            f"{topbar_html}"
            f'      <main class="or-content">{content}</main>\n'
            "    </div>\n"
            "  </div>\n"
            f"{modal_html}"
            '  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>\n'
            '  <script src="/vendor/orbit/orbit.js"></script>\n'
            "</body>\n"
            "</html>"
        )

    def _render_sidebar(self, ctx: Any, collapsible: bool) -> str:
        if ctx.layout == "top":
            return ""
        toggle = ""
        if collapsible:
            toggle = (
                '<button type="button" class="or-sidebar-toggle" @click="sidebarOpen = !sidebarOpen" '
                'aria-label="Toggle sidebar">☰</button>'
            )
        if ctx.layout == "sidebar_topbar" and ctx.menu_roots:
            links = []
            for root in ctx.menu_roots:
                ic = render_icon(root.icon) if root.icon else ""
                active = " is-active" if root.active else ""
                links.append(
                    f'<a class="or-nav-link{active}" href="{e(root.href)}">{ic}'
                    f'<span>{e(root.label)}</span></a>'
                )
            nav = "".join(links)
        else:
            # Grouped flat sidebar
            links = []
            current_group = object()
            for item in ctx.flat_items:
                group = item.get("group")
                if group != current_group:
                    current_group = group
                    if group:
                        links.append(f'<div class="or-nav-group">{e(group)}</div>')
                ic = render_icon(item["icon"]) if item.get("icon") else ""
                links.append(
                    f'<a class="or-nav-link" href="{e(item["url"])}">{ic}'
                    f'<span>{e(item["label"])}</span></a>'
                )
            nav = "".join(links)
        hidden = ' :class="{ \'is-collapsed\': !sidebarOpen }"' if collapsible else ""
        return (
            f'    <aside class="or-sidebar"{hidden}>\n'
            f"{toggle}"
            f'      <div class="or-brand">{e(self._brand)}</div>\n'
            f'      <nav class="or-nav">{nav}</nav>\n'
            "    </aside>\n"
        )

    def _render_topbar(self, ctx: Any) -> str:
        secondary = []
        for item in ctx.menu_secondary:
            if item.children:
                children = "".join(
                    f'<a class="or-topnav-child{" is-active" if c.active else ""}" '
                    f'href="{e(c.href)}">{e(c.label)}</a>'
                    for c in item.children
                )
                secondary.append(
                    f'<div class="or-topnav-dropdown{" is-active" if item.active else ""}">'
                    f'<button type="button" class="or-topnav-link">{e(item.label)}</button>'
                    f'<div class="or-topnav-menu">{children}</div></div>'
                )
            else:
                active = " is-active" if item.active else ""
                href = e(item.href or "#")
                secondary.append(
                    f'<a class="or-topnav-link{active}" href="{href}">{e(item.label)}</a>'
                )
        return (
            '      <header class="or-topbar">\n'
            f'        <nav class="or-topnav">{"".join(secondary)}</nav>\n'
            '        <div class="or-topbar-end"></div>\n'
            "      </header>\n"
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
            "navigation_layout": self._navigation_layout,
        }


def _action_modal_html() -> str:
    return (
        '  <div class="or-action-modal-host" x-data="orbitActionModal" x-cloak>\n'
        '    <div class="or-modal-backdrop" x-show="open" @click="close()"></div>\n'
        '    <div class="or-modal" x-show="open" role="dialog" aria-modal="true">\n'
        '      <h2 class="or-modal-title" x-text="heading"></h2>\n'
        '      <p class="or-modal-body" x-text="description" x-show="description"></p>\n'
        '      <div class="or-modal-actions">\n'
        '        <button type="button" class="or-btn or-btn-gray" @click="close()">Cancel</button>\n'
        '        <button type="button" class="or-btn or-btn-primary" @click="confirm()">Confirm</button>\n'
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
    )


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
