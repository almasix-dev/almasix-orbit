"""Panel — admin shell registration (Filament Panel analogue)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Literal, Self

from almasix.orbit.panels.content_width import (
    DEFAULT_CONTENT_MAX_WIDTH,
    resolve_content_max_width,
)
from almasix.orbit.panels.discover import load_theme_css
from almasix.orbit.panels.hooks import register_render_hook, render_hook
from almasix.orbit.panels.navigation import (
    NavigationGroup,
    NavigationItem,
    NavLayout,
    build_menu_layout,
    normalize_nav_layout,
)
from almasix.orbit.panels.page import Page
from almasix.orbit.panels.theme_colors import (
    DEFAULT_PRIMARY,
    normalize_panel_color,
    resolve_panel_color_vars,
)
from almasix.orbit.panels.users import OrbitUser, PanelNotification, UserMenuItem
from almasix.orbit.support.colors import Color
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon

_TOPBAR_ICON = 20
DEFAULT_BRAND_NAME_FONT_SIZE = "1.05rem"
DEFAULT_BRAND_LOGO_HEIGHT = "2rem"
DEFAULT_SIMPLE_PAGE_MAX_CONTENT_WIDTH = "lg"

PageOption = bool | type[Page]
ThemeMode = Literal["light", "dark", "system"]
PluginLike = Any  # ``Plugin`` / ``PanelPlugin`` or ``Callable[[Panel], Any]``


def _resolve_page_option(value: PageOption, *, default_cls: type[Page]) -> type[Page] | None:
    """``False`` → disabled; ``True`` → default class; page class → that class."""
    if value is False:
        return None
    if value is True:
        return default_cls
    if isinstance(value, type) and issubclass(value, Page):
        return value
    return default_cls


class Panel:
    def __init__(self, panel_id: str = "admin") -> None:
        self.id = panel_id
        self._path = f"/{panel_id}"
        self._is_default = False
        self._domain: str | None = None
        self._home_url: str | None = None
        self._favicon: str | None = None
        self._brand = "Orbit"
        self._brand_logo: str | None = None
        self._brand_logo_dark: str | None = None
        self._brand_logo_only: bool = False
        self._brand_name_font_size: str = DEFAULT_BRAND_NAME_FONT_SIZE
        self._brand_logo_height: str = DEFAULT_BRAND_LOGO_HEIGHT
        self._font = "Outfit"
        self._colors: dict[str, str] = {"primary": DEFAULT_PRIMARY}
        self._resources: list[type[Any]] = []
        self._pages: list[type[Any]] = []
        self._widgets: list[type[Any]] = []
        self._middleware: list[Any] = ["web"]
        self._auth_middleware: list[Any] = []
        self._login: PageOption = True
        self._signup: PageOption = False
        self._dashboard: PageOption = True
        self._auth_guard: str | None = None
        self._plugin_callbacks: list[Callable[[Panel], Any]] = []
        self._plugins: list[Any] = []
        self._boot_callbacks: list[Callable[[Panel], Any]] = []
        self._dark_mode = True
        self._theme_switcher = True
        self._default_theme_mode: ThemeMode = "system"
        self._sidebar_collapsible = False
        self._breadcrumbs_enabled = True
        self._discover_resources_in: list[str] = []
        self._discover_pages_in: list[str] = []
        self._discover_widgets_in: list[str] = []
        self._theme_packages: list[str] = []
        self._theme_stylesheets: list[str] = []
        self._custom_nav_items: list[NavigationItem] = []
        self._nav_groups: dict[str, NavigationGroup] = {}
        self._navigation_layout: NavLayout = "apps"
        self._user_menu_items: list[dict[str, str]] = []
        self._notifications_enabled = True
        self._database_notifications: list[dict[str, Any]] = []
        self._panel_user: Any = None
        self._content_max_width: str = DEFAULT_CONTENT_MAX_WIDTH
        self._simple_page_max_content_width: str = DEFAULT_SIMPLE_PAGE_MAX_CONTENT_WIDTH
        # Back-compat alias used by older callers / routing.
        self._demo_user: Any = None

    @classmethod
    def make(cls, panel_id: str = "admin") -> Self:
        return cls(panel_id)

    def default(self, condition: bool = True) -> Self:
        """Mark this panel as the application default (see :meth:`PanelRegistry.get_default`)."""
        self._is_default = bool(condition)
        return self

    def is_default(self) -> bool:
        return self._is_default

    def path(self, path: str) -> Self:
        # Filament allows ``path('')`` for a root panel; treat empty as ``/``.
        cleaned = (path or "").strip()
        if cleaned in ("", "/"):
            self._path = "/"
            return self
        self._path = cleaned if cleaned.startswith("/") else f"/{cleaned}"
        return self

    def domain(self, domain: str | None) -> Self:
        """Bind panel routes to a host (passed to Almasix ``Router.add(domain=…)``)."""
        self._domain = (domain or "").strip() or None
        return self

    def get_domain(self) -> str | None:
        return self._domain

    def home_url(self, url: str | None) -> Self:
        """Override the brand / breadcrumb home URL (defaults to the panel root)."""
        self._home_url = (url or "").strip() or None
        return self

    def get_home_url(self) -> str:
        if self._home_url:
            return self._home_url
        return self.url()

    def favicon(self, url: str | None) -> Self:
        """Set ``<link rel=\"icon\">`` in the panel shell head."""
        self._favicon = (url or "").strip() or None
        return self

    def get_favicon_url(self) -> str | None:
        from almasix.orbit.support.urls import resolve_public_url

        return resolve_public_url(self._favicon) if self._favicon else None

    def brand_name(self, name: str) -> Self:
        self._brand = name
        return self

    def brand_logo(self, url: str, *, dark: str | None = None) -> Self:
        """Set the light-mode brand image (optional dark-mode variant).

        Accepts:

        - ``asset("images/logo.svg")`` — already-resolved public asset URL
        - Absolute / protocol-relative URLs (``https://…``, ``//cdn/…``)
        - Bare relatives (``images/logo.svg`` or ``/images/logo.svg``) — resolved
          with Almasix ``url()`` at render time

        When ``dark`` is omitted, the light logo is reused in dark mode. Prefer
        :meth:`brand_logo_dark` to set the dark asset separately.
        """
        self._brand_logo = url
        if dark is not None:
            self._brand_logo_dark = dark
        return self

    def brand_logo_dark(self, url: str) -> Self:
        """Set the dark-mode brand image. Falls back to the light logo when unset."""
        self._brand_logo_dark = url
        return self

    def brand_logo_only(self, condition: bool = True) -> Self:
        """When a logo is set, hide the brand name next to it (shell + login).

        The name from :meth:`brand_name` is still used for ``<title>`` and image ``alt``.
        """
        self._brand_logo_only = bool(condition)
        return self

    def brand_name_font_size(self, size: str) -> Self:
        """Font size for the visible brand name (shell + login). CSS length, e.g. ``1.25rem``."""
        self._brand_name_font_size = (size or DEFAULT_BRAND_NAME_FONT_SIZE).strip() or (
            DEFAULT_BRAND_NAME_FONT_SIZE
        )
        return self

    def brand_logo_height(self, height: str) -> Self:
        """CSS height for brand logos (default ``2rem``)."""
        self._brand_logo_height = (height or DEFAULT_BRAND_LOGO_HEIGHT).strip() or (
            DEFAULT_BRAND_LOGO_HEIGHT
        )
        return self

    def get_brand_logo_url(self, *, dark: bool = False) -> str | None:
        """Resolved logo URL for the active theme (see :meth:`brand_logo`).

        Dark mode falls back to the light logo when no dark asset is configured.
        """
        from almasix.orbit.support.urls import resolve_public_url

        if dark:
            raw = self._brand_logo_dark or self._brand_logo
        else:
            raw = self._brand_logo
        return resolve_public_url(raw)

    def font(self, family: str) -> Self:
        self._font = family
        return self

    def primary(self, color: Color | str) -> Self:
        """Set the panel brand primary color (hex or semantic token)."""
        self._colors["primary"] = normalize_panel_color(color)
        return self

    def colors(self, **colors: Color | str) -> Self:
        """Merge semantic colors (``primary``, ``danger``, …). Values may be hex or tokens."""
        for key, value in colors.items():
            self._colors[str(key)] = normalize_panel_color(value)
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

    def middleware(
        self,
        middleware: Sequence[Any],
        *,
        replace: bool = False,
    ) -> Self:
        """Append middleware after the default ``web`` group (deduped).

        Pass ``replace=True`` to set the stack explicitly (e.g. clear defaults in tests).
        """
        if replace:
            self._middleware = list(middleware)
            return self
        for item in middleware:
            if item not in self._middleware:
                self._middleware.append(item)
        return self

    def auth_middleware(
        self,
        middleware: Sequence[Any],
        *,
        replace: bool = False,
    ) -> Self:
        """Middleware applied only to authenticated panel routes (not login/register)."""
        if replace:
            self._auth_middleware = list(middleware)
            return self
        for item in middleware:
            if item not in self._auth_middleware:
                self._auth_middleware.append(item)
        return self

    def get_auth_middleware(self) -> list[Any]:
        return list(self._auth_middleware)

    def login(self, page: PageOption = True) -> Self:
        """Enable login (default), disable with ``False``, or pass a custom ``Login`` page class."""
        self._login = page
        return self

    def signup(self, page: PageOption = True) -> Self:
        """Opt-in user registration. Pass ``False`` to disable, or a custom ``Register`` page."""
        self._signup = page
        return self

    def dashboard(self, page: PageOption = True) -> Self:
        """Panel home page (on by default). Pass ``False`` to disable, or a custom ``Dashboard``."""
        self._dashboard = page
        return self

    def login_enabled(self) -> bool:
        return self._login is not False

    def signup_enabled(self) -> bool:
        return self._signup is not False

    def dashboard_enabled(self) -> bool:
        return self._dashboard is not False

    def login_page(self) -> type[Page] | None:
        from almasix.orbit.panels.auth import Login

        return _resolve_page_option(self._login, default_cls=Login)

    def signup_page(self) -> type[Page] | None:
        from almasix.orbit.panels.auth import Register

        return _resolve_page_option(self._signup, default_cls=Register)

    def dashboard_page(self) -> type[Page] | None:
        from almasix.orbit.panels.pages.dashboard import Dashboard

        return _resolve_page_option(self._dashboard, default_cls=Dashboard)

    def auth_guard(self, guard: str) -> Self:
        self._auth_guard = guard
        return self

    def dark_mode(self, condition: bool = True) -> Self:
        """Enable dark-mode CSS / preference boot. Use :meth:`theme_switcher` for the toggle."""
        self._dark_mode = bool(condition)
        return self

    def theme_switcher(self, condition: bool = True) -> Self:
        """Show the light/dark/system toggle (requires :meth:`dark_mode`)."""
        self._theme_switcher = bool(condition)
        return self

    def default_theme_mode(self, mode: ThemeMode = "system") -> Self:
        """Default theme preference when the user has no stored choice (``light``/``dark``/``system``)."""
        normalized = str(mode or "system").strip().lower()
        if normalized not in ("light", "dark", "system"):
            normalized = "system"
        self._default_theme_mode = normalized  # type: ignore[assignment]
        return self

    def sidebar_collapsible(self, condition: bool = True) -> Self:
        self._sidebar_collapsible = bool(condition)
        return self

    def breadcrumbs_enabled(self, condition: bool = True) -> Self:
        """Toggle the shell breadcrumb trail (on by default)."""
        self._breadcrumbs_enabled = bool(condition)
        return self

    def navigation_layout(self, layout: NavLayout) -> Self:
        """Set navigation chrome: ``apps`` (sidebar+topbar), ``sidebar``, or ``top``."""
        self._navigation_layout = layout
        return self

    def apps_navigation(self) -> Self:
        """Split layout: group roots in the sidebar, secondary links in the topbar."""
        return self.navigation_layout("apps")

    def sidebar_navigation(self) -> Self:
        """Full navigation tree in the sidebar only."""
        return self.navigation_layout("sidebar")

    def top_navigation(self) -> Self:
        """Top-bar navigation only (no sidebar)."""
        return self.navigation_layout("top")

    def user_menu_items(self, items: Sequence[UserMenuItem | dict[str, str]]) -> Self:
        for item in items:
            self.user_menu_item(item)
        return self

    def user_menu_item(self, item: UserMenuItem | dict[str, str]) -> Self:
        if isinstance(item, UserMenuItem):
            self._user_menu_items.append(item.to_dict())
        else:
            self._user_menu_items.append(dict(item))
        return self

    def database_notifications(
        self,
        items: Sequence[PanelNotification | dict[str, Any]],
    ) -> Self:
        for item in items:
            self.notification(item)
        return self

    def notification(self, item: PanelNotification | dict[str, Any]) -> Self:
        if isinstance(item, PanelNotification):
            self._database_notifications.append(item.to_dict())
        else:
            self._database_notifications.append(dict(item))
        return self

    def notifications(self, condition: bool = True) -> Self:
        self._notifications_enabled = bool(condition)
        return self

    def user(self, user: OrbitUser | Any | None) -> Self:
        """Panel principal used when Almasix Auth has no session user."""
        self._panel_user = user
        self._demo_user = user  # back-compat
        return self

    def demo_user(self, user: Any) -> Self:
        """Deprecated alias for :meth:`user` (local demos)."""
        return self.user(user)

    def default_user(self) -> Self:
        """Use :meth:`OrbitUser.default` as the panel principal."""
        return self.user(OrbitUser.default())

    def get_panel_user(self) -> Any:
        return self._panel_user

    def content_max_width(self, value: str) -> Self:
        """Cap centered page content (Shamar tokens: ``screen-2xl``, ``7xl``, ``full``, …)."""
        self._content_max_width = value
        return self

    def get_content_max_width(self) -> str:
        return self._content_max_width

    def simple_page_max_content_width(self, value: str) -> Self:
        """Max content width for bare/auth pages (login, register). Default ``lg``."""
        self._simple_page_max_content_width = value
        return self

    def get_simple_page_max_content_width(self) -> str:
        return self._simple_page_max_content_width

    def navigation_items(self, items: Sequence[NavigationItem] | None = None) -> Any:
        """Register custom items when passed; otherwise return computed nav dicts."""
        if items is not None:
            for item in items:
                self.navigation_item(item)
            return self
        return self._collect_navigation_items()

    def navigation_item(self, item: NavigationItem) -> Self:
        self._custom_nav_items.append(item)
        return self

    def navigation_groups(self, groups: Sequence[NavigationGroup]) -> Self:
        for group in groups:
            self.navigation_group(group)
        return self

    def navigation_group(self, group: NavigationGroup) -> Self:
        """Optional group metadata (icon/sort). Group names still come from resources/pages."""
        name = group.get_name() or group.get_label()
        if name:
            self._nav_groups[name] = group
        # Nested fluent items on the group also register as panel nav items.
        for item in getattr(group, "_items", []) or []:
            if not item._group:
                item.group(str(name) if name else None)
            self._custom_nav_items.append(item)
        return self

    def discover_resources(self, *paths: str) -> Self:
        self._discover_resources_in.extend(str(p) for p in paths)
        return self

    def discover_pages(self, *paths: str) -> Self:
        self._discover_pages_in.extend(str(p) for p in paths)
        return self

    def discover_widgets(self, *paths: str) -> Self:
        self._discover_widgets_in.extend(str(p) for p in paths)
        return self

    def discover_panel_dirs(self, package: str | None = None) -> Self:
        """Discover resources/pages/widgets and load theme CSS under a panel package.

        Defaults to ``app.orbit.{panel_id}`` (v0.3 layout)::

            app/orbit/admin/resources|pages|widgets|themes

        Does **not** auto-discover ``plugins/`` — register with :meth:`plugin`.
        Shared modules under ``app/orbit/shared/`` are never auto-discovered;
        register them explicitly (e.g. ``.resources([SharedPostResource])``).
        """
        pkg = (package or f"app.orbit.{self.id}").strip()
        return (
            self.discover_resources(f"{pkg}.resources")
            .discover_pages(f"{pkg}.pages")
            .discover_widgets(f"{pkg}.widgets")
            .theme_package(f"{pkg}.themes")
        )

    def theme_package(self, *packages: str) -> Self:
        """Load ``*.css`` files from dotted theme packages into the shell head."""
        self._theme_packages.extend(str(p).strip() for p in packages if str(p).strip())
        return self

    def theme_stylesheet(self, *urls: str) -> Self:
        """Link extra stylesheets (absolute or app-relative URLs) in the shell head."""
        self._theme_stylesheets.extend(str(u).strip() for u in urls if str(u).strip())
        return self

    def load_discovered(self) -> Self:
        """Import discovered modules and register resources, pages, and widgets."""
        from almasix.orbit.panels.discover import class_key, discover_classes
        from almasix.orbit.panels.page import Page
        from almasix.orbit.panels.resource import Resource

        seen_resources = {class_key(r) for r in self._resources}
        seen_pages = {class_key(p) for p in self._pages}
        seen_widgets = {class_key(w) for w in self._widgets}

        for path in self._discover_resources_in:
            for cls in discover_classes(path, base_class=Resource):
                key = class_key(cls)
                if key not in seen_resources:
                    self._resources.append(cls)
                    seen_resources.add(key)

        for path in self._discover_pages_in:
            for cls in discover_classes(path, base_class=Page):
                key = class_key(cls)
                if key not in seen_pages:
                    self._pages.append(cls)
                    seen_pages.add(key)

        for path in self._discover_widgets_in:
            from almasix.orbit.widgets.widget import Widget

            for cls in discover_classes(path, base_class=Widget):
                key = class_key(cls)
                if key not in seen_widgets:
                    self._widgets.append(cls)
                    seen_widgets.add(key)

        return self

    def plugin(self, plugin: PluginLike) -> Self:
        """Register a mount-time plugin.

        Accepts a ``Callable[[Panel], Any]`` (legacy) or a ``Plugin`` / ``PanelPlugin``
        instance (``register`` then ``boot`` at mount).
        """
        if callable(plugin) and not hasattr(plugin, "get_id"):
            self._plugin_callbacks.append(plugin)
            return self
        self._plugins.append(plugin)
        return self

    def plugins(self, plugins: Sequence[PluginLike]) -> Self:
        for item in plugins:
            self.plugin(item)
        return self

    def boot_using(self, callback: Callable[[Panel], Any]) -> Self:
        """Run ``callback(panel)`` after plugins when the panel is mounted."""
        self._boot_callbacks.append(callback)
        return self

    def render_hook(
        self,
        name: str,
        callback: Callable[..., str],
        *,
        scopes: list[str] | None = None,
    ) -> Self:
        """Register a panel-scoped render hook (defaults to this panel's id)."""
        register_render_hook(name, callback, scopes=scopes if scopes is not None else [self.id])
        return self

    def run_plugins(self) -> Self:
        """Invoke plugin ``register`` / callbacks / ``boot`` / ``boot_using`` (also called at mount)."""
        for plugin in self._plugins:
            register = getattr(plugin, "register", None)
            if callable(register):
                register(self)
        for callback in self._plugin_callbacks:
            callback(self)
        for plugin in self._plugins:
            boot = getattr(plugin, "boot", None)
            if callable(boot):
                boot(self)
        for callback in self._boot_callbacks:
            callback(self)
        return self

    def get_path(self) -> str:
        return self._path

    def url(self, *segments: str) -> str:
        """Join ``segments`` under the panel path (safe when the panel is mounted at ``/``)."""
        base = (self._path or "/").rstrip("/")
        parts = [str(s).strip("/") for s in segments if s is not None and str(s).strip("/")]
        if not parts:
            return base or "/"
        suffix = "/".join(parts)
        return f"{base}/{suffix}" if base else f"/{suffix}"

    def get_resources(self) -> list[type[Any]]:
        return list(self._resources)

    def get_pages(self) -> list[type[Any]]:
        return list(self._pages)

    def get_widgets(self) -> list[type[Any]]:
        return list(self._widgets)

    def get_middleware(self) -> list[Any]:
        return list(self._middleware)

    def _collect_navigation_items(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        dash = self.dashboard_page() if self.dashboard_enabled() else None
        if dash is not None and dash not in self._pages:
            items.append(
                {
                    "slug": dash.get_slug(),
                    "label": dash.get_navigation_label(),
                    "icon": getattr(dash, "navigation_icon", "heroicon-o-home"),
                    "group": getattr(dash, "navigation_group", None),
                    "subgroup": getattr(dash, "navigation_subgroup", None),
                    "url": self.url(),
                    "sort": getattr(dash, "navigation_sort", -100),
                }
            )
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
                    "url": self.url(
                        getattr(res, "get_slug", lambda r=res: r.__name__.lower())()
                    ),
                    "sort": getattr(res, "navigation_sort", 0),
                }
            )
        for page in self._pages:
            # Home dashboard is mounted at ``/`` — avoid a duplicate ``/dashboard`` nav entry.
            if dash is not None and page is dash:
                items.append(
                    {
                        "slug": page.get_slug(),
                        "label": page.get_navigation_label(),
                        "icon": getattr(page, "navigation_icon", "heroicon-o-home"),
                        "group": getattr(page, "navigation_group", None),
                        "subgroup": getattr(page, "navigation_subgroup", None),
                        "url": self.url(),
                        "sort": getattr(page, "navigation_sort", -100),
                    }
                )
                continue
            items.append(
                {
                    "slug": getattr(page, "get_slug", lambda p=page: p.__name__.lower())(),
                    "label": getattr(
                        page, "get_navigation_label", lambda p=page: p.__name__
                    )(),
                    "icon": getattr(page, "navigation_icon", "heroicon-o-home"),
                    "group": getattr(page, "navigation_group", None),
                    "subgroup": getattr(page, "navigation_subgroup", None),
                    "url": self.url(
                        getattr(page, "get_slug", lambda p=page: p.__name__.lower())()
                    ),
                    "sort": getattr(page, "navigation_sort", 0),
                }
            )
        for item in self._custom_nav_items:
            items.append(item.to_nav_dict())
        items.sort(key=lambda i: (i.get("sort") or 0, i.get("label") or ""))
        return items

    def menu_layout_context(self, active_path: str | None = None) -> Any:
        meta = dict(self._nav_groups)
        # Ensure the Dashboard group sorts first when the built-in home page is on.
        if self.dashboard_enabled():
            dash = self.dashboard_page()
            if dash is not None:
                group_name = getattr(dash, "navigation_group", None) or dash.get_navigation_label()
                if group_name and group_name not in meta:
                    meta[str(group_name)] = (
                        NavigationGroup.make(str(group_name))
                        .icon(getattr(dash, "navigation_icon", "heroicon-o-home"))
                        .sort(getattr(dash, "navigation_sort", -100))
                    )
        return build_menu_layout(
            self._collect_navigation_items(),
            group_meta=meta,
            active_path=active_path,
            layout=normalize_nav_layout(self._navigation_layout),
            panel_path=self._path,
        )

    def _render_theme_styles(self) -> str:
        """Inline theme package CSS + linked stylesheets for the shell head."""
        parts: list[str] = []
        for url in self._theme_stylesheets:
            parts.append(f'  <link rel="stylesheet" href="{e(url)}" />\n')
        for source_id, css in load_theme_css(*self._theme_packages):
            parts.append(f'  <style data-orbit-theme="{e(source_id)}">\n{css}\n  </style>\n')
        return "".join(parts)

    def render_shell(
        self,
        content: str,
        *,
        user: Any = None,
        active_path: str | None = None,
        extra_head: str = "",
        bare: bool = False,
    ) -> str:
        """Render the admin document shell around page ``content``.

        ``bare=True`` skips sidebar/topbar (auth pages). ``extra_head`` injects
        Conduit/Alpine asset tags when mounting live hosts.
        """
        layout = normalize_nav_layout(self._navigation_layout)
        ctx = self.menu_layout_context(active_path=active_path)
        brand = e(self._brand)
        font = e(self._font)
        collapsible = self._sidebar_collapsible
        scope = self.id
        width_token = (
            self._simple_page_max_content_width if bare else self._content_max_width
        )
        width = resolve_content_max_width(width_token)
        width_css = e(width.css_value)
        color_vars = "".join(
            f"{e(name)}: {e(value)}; "
            for name, value in resolve_panel_color_vars(self._colors).items()
        )
        brand_name_size = e(self._brand_name_font_size or DEFAULT_BRAND_NAME_FONT_SIZE)
        brand_logo_height = e(self._brand_logo_height or DEFAULT_BRAND_LOGO_HEIGHT)
        show_theme_toggle = self._dark_mode and self._theme_switcher
        default_theme = e(self._default_theme_mode or "system")

        if bare:
            sun = render_icon("heroicon-o-sun", size=20)
            moon = render_icon("heroicon-o-moon", size=20)
            system = render_icon("heroicon-o-computer-desktop", size=20)
            theme_btn = ""
            if show_theme_toggle:
                theme_btn = (
                    '<button type="button" class="or-icon-btn or-theme-toggle or-auth-theme" '
                    '@click="cycleTheme()" :aria-label="\'Theme: \' + theme">'
                    '<span class="or-theme-icons" aria-hidden="true">'
                    f'<span class="or-theme-icon-sun">{sun}</span>'
                    f'<span class="or-theme-icon-moon">{moon}</span>'
                    f'<span class="or-theme-icon-system">{system}</span>'
                    "</span></button>"
                )
            body_inner = (
                f'{render_hook("panels::body.start", scope=scope, user=user)}'
                f'<div class="or-auth-shell" x-data="orbitShell">'
                f"{theme_btn}"
                f'<div class="or-card or-auth-card">{content}</div></div>'
                f'{render_hook("panels::body.end", scope=scope, user=user)}'
                f"{_action_modal_html()}"
            )
            app_wrap = body_inner
        else:
            sidebar_html = self._render_sidebar(ctx, collapsible, user=user)
            topbar_html = self._render_topbar(ctx, user=user, collapsible=collapsible)
            modal_html = _action_modal_html()
            app_class = "or-app"
            if layout == "sidebar_topbar":
                app_class += " or-app-split or-app-apps"
            if layout == "top":
                app_class += " or-app-top"
            if layout == "sidebar":
                app_class += " or-app-sidebar"
            collapse_bind = (
                ", 'is-collapsed': collapsed" if collapsible and layout != "top" else ""
            )
            app_wrap = (
                f'{render_hook("panels::body.start", scope=scope, user=user)}'
                f'<div class="{app_class}" x-data="orbitShell" '
                f":class=\"{{ 'is-drawer-open': drawerOpen{collapse_bind} }}\">\n"
                f'  <div class="or-drawer-backdrop" @click="closeDrawer()"></div>\n'
                f"{sidebar_html}"
                '  <div class="or-main">\n'
                f"{topbar_html}"
                f'    {render_hook("panels::content.start", scope=scope, user=user)}\n'
                f"{self._render_breadcrumbs(active_path)}"
                f'    <main class="or-content">{content}</main>\n'
                f'    {render_hook("panels::content.end", scope=scope, user=user)}\n'
                "  </div>\n"
                "</div>\n"
                f"{modal_html}"
                f'{render_hook("panels::body.end", scope=scope, user=user)}'
            )

        theme_boot = (
            "<script>(function(){try{"
            f"var fallback='{default_theme}';"
            "var t=localStorage.getItem('orbit-theme');"
            "if(t!=='light'&&t!=='dark'&&t!=='system'){t=fallback;}"
            "var dark=t==='dark'||(t!=='light'&&matchMedia('(prefers-color-scheme:dark)').matches);"
            "document.documentElement.setAttribute('data-theme',dark?'dark':'light');"
            "document.documentElement.setAttribute('data-theme-preference',t);"
            "document.documentElement.classList.toggle('dark',dark);"
            "}catch(e){}})();</script>"
            if self._dark_mode
            else ""
        )

        csrf_meta = ""
        try:
            from almasix.session.csrf import csrf_token

            token = csrf_token()
            if token:
                csrf_meta = f'  <meta name="csrf-token" content="{e(token)}" />\n'
        except Exception:
            pass

        favicon_html = ""
        fav = self.get_favicon_url()
        if fav:
            favicon_html = f'  <link rel="icon" href="{e(fav)}" />\n'

        return (
            "<!DOCTYPE html>\n"
            f'<html lang="en" translate="no" data-orbit-panel="{e(self.id)}" data-theme="light">\n'
            "<head>\n"
            '  <meta charset="utf-8" />\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1" />\n'
            '  <meta name="google" content="notranslate" />\n'
            f"{csrf_meta}"
            f"{favicon_html}"
            f"  <title>{brand}</title>\n"
            f"{theme_boot}\n"
            f'{render_hook("panels::head.start", scope=scope)}\n'
            # No Google Fonts CDN link — unreachable fonts.googleapis.com keeps the
            # tab spinner alive for tens of seconds. --or-font already falls back to
            # system UI fonts; apps can inject a webfont via panels::head hooks.
            '  <link rel="stylesheet" href="/vendor/orbit/orbit.css" />\n'
            # Register Alpine data before any Alpine CDN tag (Conduit may inject one in extra_head).
            '  <script src="/vendor/orbit/orbit.js"></script>\n'
            f"  <style>:root {{ --or-font: '{font}', ui-sans-serif, system-ui, sans-serif; "
            f"{color_vars}--or-brand-name-size: {brand_name_size}; "
            f"--or-brand-logo-height: {brand_logo_height}; "
            f"--or-content-max: {width_css}; }}</style>\n"
            f"{self._render_theme_styles()}"
            f"{extra_head}\n"
            f'{render_hook("panels::styles.after", scope=scope)}\n'
            f'{render_hook("panels::head.end", scope=scope)}\n'
            "</head>\n"
            '<body class="or-body">\n'
            f"{app_wrap}"
            + (
                ""
                if "alpinejs" in (extra_head or "").lower()
                else '  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>\n'
            )
            + f'{render_hook("panels::scripts.after", scope=scope)}\n'
            "</body>\n"
            "</html>"
        )

    def breadcrumbs(self, active_path: str | None = None) -> list[dict[str, str | None]]:
        """Resolve breadcrumb items for ``active_path``.

        Each item is ``{"label": str, "url": str | None}``. The last item is the
        current page (``url`` is ``None``).
        """
        home_url = self.get_home_url()
        crumbs: list[dict[str, str | None]] = [
            {"label": self._brand, "url": home_url},
        ]
        if not active_path:
            return crumbs

        path = active_path.rstrip("/") or "/"
        base = (self._path or "/").rstrip("/") or ""
        prefix = f"{base}/" if base else "/"
        if base and (path == base or path == f"{base}/"):
            crumbs[-1]["url"] = None
            return crumbs
        if not path.startswith(prefix) and path != base:
            # Path outside this panel — still show home.
            crumbs[-1]["url"] = None
            return crumbs

        remainder = path[len(prefix) :] if path.startswith(prefix) else path.lstrip("/")
        if not remainder:
            crumbs[-1]["url"] = None
            return crumbs

        segments = [s for s in remainder.split("/") if s]
        # rstrip('/') above means slash-only remainders never reach here; keep guard anyway.
        if not segments:  # pragma: no cover
            crumbs[-1]["url"] = None
            return crumbs

        slug = segments[0]
        resource = next(
            (r for r in self._resources if getattr(r, "get_slug", lambda: "")() == slug),
            None,
        )
        page = next(
            (p for p in self._pages if getattr(p, "get_slug", lambda: "")() == slug),
            None,
        )

        if resource is not None:
            label = resource.get_navigation_label()
            index_url = self.url(slug)
            crumbs.append({"label": label, "url": index_url})
            if len(segments) == 1:
                crumbs[-1]["url"] = None
                return crumbs
            action = segments[-1]
            if action == "create":
                crumbs.append({"label": "Create", "url": None})
            elif action == "edit":
                crumbs.append({"label": "Edit", "url": None})
            else:
                # /{slug}/{id} view (len(segments) >= 2 after the early return above)
                crumbs.append({"label": "View", "url": None})
            return crumbs

        if page is not None:
            label = page.get_navigation_label()
            crumbs.append({"label": label, "url": None})
            return crumbs

        # Unknown segment — show raw title-cased path pieces.
        for i, segment in enumerate(segments):
            is_last = i == len(segments) - 1
            label = segment.replace("-", " ").replace("_", " ").title()
            url = None
            if not is_last:
                url = self.url(*segments[: i + 1])
            crumbs.append({"label": label, "url": url})
        return crumbs

    def _render_breadcrumbs(self, active_path: str | None) -> str:
        if not self._breadcrumbs_enabled:
            return ""
        items = self.breadcrumbs(active_path)
        if len(items) <= 1:
            # Home-only: omit the trail (the brand already marks where you are).
            return ""
        parts: list[str] = ['    <nav class="or-breadcrumbs" aria-label="Breadcrumb"><ol class="or-breadcrumbs-list">']
        for i, item in enumerate(items):
            label = e(str(item.get("label") or ""))
            url = item.get("url")
            is_last = i == len(items) - 1 or not url
            if is_last or not url:
                parts.append(
                    f'<li class="or-breadcrumbs-item" aria-current="page">'
                    f'<span class="or-breadcrumbs-current">{label}</span></li>'
                )
            else:
                parts.append(
                    f'<li class="or-breadcrumbs-item">'
                    f'<a class="or-breadcrumbs-link" href="{e(str(url))}">{label}</a></li>'
                )
        parts.append("</ol></nav>\n")
        return "".join(parts)

    def _brand_html(self) -> str:
        name = e(self._brand)
        logo = ""
        show_name = True
        light = self.get_brand_logo_url(dark=False)
        home = e(self.get_home_url())
        if light:
            dark = self.get_brand_logo_url(dark=True) or light
            if dark == light:
                logo = (
                    f'<img class="or-brand-logo" src="{e(light)}" alt="{name}" />'
                )
            else:
                logo = (
                    f'<img class="or-brand-logo or-brand-logo-light" src="{e(light)}" alt="{name}" />'
                    f'<img class="or-brand-logo or-brand-logo-dark" src="{e(dark)}" alt="" />'
                )
            if self._brand_logo_only:
                show_name = False
        classes = "or-brand"
        if logo and not show_name:
            classes += " or-brand-logo-only"
        name_html = f'<span class="or-brand-name">{name}</span>' if show_name else ""
        return f'<a class="{classes}" href="{home}">{logo}{name_html}</a>'

    def _nav_group(self, label: str) -> str:
        tip = e(label)
        return (
            f'<div class="or-nav-group" data-tooltip="{tip}" role="presentation">'
            f'<span class="or-nav-group-label">{tip}</span>'
            f'<span class="or-nav-group-mark" aria-hidden="true"></span>'
            f"</div>"
        )

    def _nav_link(self, href: str, label: str, icon: str | None, *, active: bool = False) -> str:
        ic = render_icon(icon) if icon else ""
        active_cls = " is-active" if active else ""
        tip = e(label)
        return (
            f'<a class="or-nav-link{active_cls}" href="{e(href)}" '
            f'data-tooltip="{tip}" @click="closeDrawer()">'
            f"{ic}<span>{tip}</span></a>"
        )

    def _render_sidebar(self, ctx: Any, collapsible: bool, *, user: Any = None) -> str:
        layout = normalize_nav_layout(ctx.layout)
        if layout == "top":
            return ""

        if layout == "sidebar_topbar" and ctx.menu_roots:
            links = [
                self._nav_link(root.href, root.label, root.icon, active=root.active)
                for root in ctx.menu_roots
            ]
            nav = "".join(links)
        else:
            links = []
            current_group = object()
            for item in ctx.flat_items:
                group = item.get("group")
                if group != current_group:
                    current_group = group
                    if group:
                        links.append(self._nav_group(str(group)))
                links.append(
                    self._nav_link(
                        item["url"],
                        item["label"],
                        item.get("icon"),
                        active=bool(item.get("url") and item.get("active")),
                    )
                )
            nav = "".join(links)

        mobile_nav = ""
        if layout == "sidebar_topbar":
            mobile_parts: list[str] = []
            current_group = object()
            for item in ctx.flat_items:
                group = item.get("group")
                if group != current_group:
                    current_group = group
                    if group:
                        mobile_parts.append(self._nav_group(str(group)))
                mobile_parts.append(
                    self._nav_link(
                        item["url"],
                        item["label"],
                        item.get("icon"),
                        active=bool(item.get("url") and item.get("active")),
                    )
                )
            mobile_nav = (
                f'<nav class="or-sidebar-nav or-nav-mobile" aria-label="Mobile navigation">'
                f'{"".join(mobile_parts)}</nav>'
            )

        footer = ""
        if user is not None:
            label = e(getattr(user, "name", None) or getattr(user, "email", None) or "Signed in")
            footer = (
                '<div class="or-sidebar-footer">'
                f'Signed in as <strong>{label}</strong></div>'
            )

        collapse_btn = ""
        if collapsible:
            chev_left = render_icon("heroicon-o-chevron-left", size=_TOPBAR_ICON)
            chev_right = render_icon("heroicon-o-chevron-right", size=_TOPBAR_ICON)
            collapse_btn = (
                '<button type="button" class="or-sidebar-collapse or-icon-btn" '
                '@click="toggleCollapse()" '
                ':aria-label="collapsed ? \'Expand sidebar\' : \'Collapse sidebar\'" '
                ':aria-expanded="(!collapsed).toString()">'
                f'<span class="or-collapse-icon-expanded" x-show="!collapsed">{chev_left}</span>'
                f'<span class="or-collapse-icon-collapsed" x-show="collapsed" x-cloak>{chev_right}</span>'
                "</button>"
            )

        scope = self.id
        brand_block = self._brand_html()
        if collapsible:
            brand_block = (
                f'<div class="or-sidebar-brand" x-show="!collapsed">{brand_block}</div>'
            )
        else:
            brand_block = f'<div class="or-sidebar-brand">{brand_block}</div>'
        return (
            '  <aside class="or-sidebar">\n'
            '    <div class="or-brand-panel">\n'
            f"      {brand_block}\n"
            f"      {collapse_btn}\n"
            '      <button type="button" class="or-sidebar-close" @click="closeDrawer()" '
            f"aria-label=\"Close menu\">{render_icon('heroicon-o-x-mark', size=16)}</button>\n"
            "    </div>\n"
            f'    {render_hook("panels::sidebar.nav.start", scope=scope, user=user)}\n'
            f'    <nav class="or-sidebar-nav or-nav-desktop" aria-label="Applications">{nav}</nav>\n'
            f"{mobile_nav}\n"
            f'    {render_hook("panels::sidebar.nav.end", scope=scope, user=user)}\n'
            f"{footer}\n"
            "  </aside>\n"
        )

    def _render_topbar(self, ctx: Any, *, user: Any = None, collapsible: bool = False) -> str:
        layout = normalize_nav_layout(ctx.layout)
        secondary = []
        for item in ctx.menu_secondary:
            item_icon = render_icon(item.icon) if getattr(item, "icon", None) else ""
            if item.children:
                children = "".join(
                    (
                        f'<a class="or-topnav-child{" is-active" if c.active else ""}" '
                        f'href="{e(c.href)}">'
                        f'{render_icon(c.icon) if c.icon else ""}'
                        f"<span>{e(c.label)}</span></a>"
                    )
                    for c in item.children
                )
                secondary.append(
                    f'<div class="or-topnav-dropdown{" is-active" if item.active else ""}" '
                    f'x-data="{{ open: false }}" @click.outside="open = false">'
                    f'<button type="button" class="or-topnav-link" @click="open = !open">'
                    f"{item_icon}<span>{e(item.label)}</span>"
                    f"{render_icon('heroicon-o-chevron-down', size=14, css_class='or-icon or-topnav-chevron')}"
                    f"</button>"
                    f'<div class="or-topnav-menu" x-show="open" x-cloak>{children}</div></div>'
                )
            else:
                active = " is-active" if item.active else ""
                href = e(item.href or "#")
                secondary.append(
                    f'<a class="or-topnav-link{active}" href="{href}">'
                    f"{item_icon}<span>{e(item.label)}</span></a>"
                )

        start_bits: list[str] = []
        if layout != "top":
            start_bits.append(
                '<button type="button" class="or-topbar-menu-btn" @click="openDrawer()" '
                f"aria-label=\"Open menu\">{render_icon('heroicon-o-bars-3', size=_TOPBAR_ICON)}</button>"
            )
            if collapsible:
                start_bits.append(
                    f'<div class="or-topbar-brand" x-show="collapsed" x-cloak>'
                    f"{self._brand_html()}</div>"
                )
        else:
            start_bits.append(self._brand_html())

        scope = self.id
        start_bits.append(render_hook("panels::topbar.start", scope=scope, user=user))
        end_chrome = self._render_topbar_end(user=user)
        end_hook = render_hook("panels::topbar.end", scope=scope, user=user)

        topnav = "".join(secondary)
        active_root = ""
        if layout == "sidebar_topbar" and getattr(ctx, "menu_active_root", None):
            root = ctx.menu_active_root
            label = getattr(root, "label", None) or ""
            if label and label != "Dashboard":
                active_root = f'<p class="or-topbar-active-root">{e(label)}</p>'

        return (
            '    <header class="or-topbar">\n'
            f'      <div class="or-topbar-start">{"".join(start_bits)}</div>\n'
            f'      <nav class="or-topnav" aria-label="App menu">{topnav}</nav>\n'
            f"      {active_root}\n"
            f'      <div class="or-topbar-end">{end_chrome}{end_hook}</div>\n'
            "    </header>\n"
        )

    def _render_topbar_end(self, *, user: Any = None) -> str:
        parts: list[str] = []
        scope = self.id
        parts.append(render_hook("panels::global-search.before", scope=scope, user=user))
        parts.append('<div class="or-global-search-slot" data-orbit-global-search></div>')
        parts.append(render_hook("panels::global-search.after", scope=scope, user=user))

        if self._dark_mode and self._theme_switcher:
            sun = render_icon("heroicon-o-sun", size=_TOPBAR_ICON)
            moon = render_icon("heroicon-o-moon", size=_TOPBAR_ICON)
            system = render_icon("heroicon-o-computer-desktop", size=_TOPBAR_ICON)
            parts.append(
                '<button type="button" class="or-icon-btn or-theme-toggle" '
                '@click="cycleTheme()" :aria-label="\'Theme: \' + theme">'
                '<span class="or-theme-icons" aria-hidden="true">'
                f'<span class="or-theme-icon-sun">{sun}</span>'
                f'<span class="or-theme-icon-moon">{moon}</span>'
                f'<span class="or-theme-icon-system">{system}</span>'
                "</span></button>"
            )

        if self._notifications_enabled:
            notes = self._database_notifications
            if notes:
                items_html = "".join(
                    f'<li class="or-notify-item"><span class="or-notify-title">'
                    f'{e(n.get("title") or "Notification")}</span>'
                    f'<span class="or-notify-body">{e(n.get("body") or "")}</span></li>'
                    for n in notes
                )
            else:
                items_html = '<li class="or-notify-empty">No notifications</li>'
            bell = render_icon("heroicon-o-bell", size=_TOPBAR_ICON)
            parts.append(
                '<div class="or-notify" x-data="{ open: false }" @click.outside="open = false">'
                '<button type="button" class="or-icon-btn or-notify-btn" @click="open = !open" '
                f'aria-label="Notifications">{bell}</button>'
                '<div class="or-notify-panel" x-show="open" x-cloak role="menu">'
                f'<ul class="or-notify-list">{items_html}</ul></div></div>'
            )

        parts.append(render_hook("panels::user-menu.before", scope=scope, user=user))
        if user is not None:
            name = str(getattr(user, "name", None) or getattr(user, "email", None) or "User")
            initials = "".join(p[:1] for p in name.split()[:2]).upper() or "U"
            menu_items = list(self._user_menu_items)
            menu_html = "".join(
                f'<a class="or-user-menu-item" href="{e(i.get("url") or "#")}">'
                f'{e(i.get("label") or "")}</a>'
                for i in menu_items
            )
            logout = e(self.url("logout"))
            parts.append(
                '<div class="or-user-menu" x-data="{ open: false }" @click.outside="open = false">'
                '<button type="button" class="or-user-menu-btn" @click="open = !open">'
                f'<span class="or-avatar" aria-hidden="true">{e(initials)}</span>'
                f'<span class="or-user-name">{e(name)}</span>'
                f"{render_icon('heroicon-o-chevron-down', size=14, css_class='or-icon or-user-chevron')}"
                f"</button>"
                '<div class="or-user-menu-panel" x-show="open" x-cloak role="menu">'
                f"{menu_html}"
                f'<a class="or-user-menu-item" href="{logout}">Sign out</a>'
                "</div></div>"
            )
        parts.append(render_hook("panels::user-menu.after", scope=scope, user=user))
        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "path": self._path,
            "default": self._is_default,
            "domain": self._domain,
            "home_url": self._home_url,
            "favicon": self._favicon,
            "brand": self._brand,
            "brand_name_font_size": self._brand_name_font_size,
            "brand_logo_height": self._brand_logo_height,
            "font": self._font,
            "colors": self._colors,
            "resources": [r.__name__ for r in self._resources],
            "pages": [p.__name__ for p in self._pages],
            "middleware": [str(m) for m in self._middleware],
            "auth_middleware": [str(m) for m in self._auth_middleware],
            "navigation_layout": normalize_nav_layout(self._navigation_layout),
            "content_max_width": self._content_max_width,
            "simple_page_max_content_width": self._simple_page_max_content_width,
            "dark_mode": self._dark_mode,
            "theme_switcher": self._theme_switcher,
            "default_theme_mode": self._default_theme_mode,
            "breadcrumbs": self._breadcrumbs_enabled,
        }


def _action_modal_html() -> str:
    return (
        '  <div class="or-action-modal-host" x-data="orbitActionModal" x-cloak>\n'
        '    <div class="or-modal-backdrop" x-show="open" @click="if (closeOnClickAway) close()"></div>\n'
        '    <div class="or-modal" x-show="open" role="dialog" aria-modal="true"\n'
        '         :class="{ \'or-modal-slide\': slideOver, [\'or-modal-\' + modalWidth]: true }">\n'
        '      <h2 class="or-modal-title" x-text="heading"></h2>\n'
        '      <p class="or-modal-body" x-text="description" x-show="description"></p>\n'
        '      <form class="or-modal-form" x-show="hasForm" x-ref="actionForm" @submit.prevent="confirm()">\n'
        '        <div class="or-modal-form-fields" x-html="formHtml"></div>\n'
        "      </form>\n"
        '      <div class="or-modal-actions">\n'
        '        <button type="button" class="or-btn or-btn-gray" @click="close()">Cancel</button>\n'
        '        <button type="button" class="or-btn or-btn-primary" @click="confirm()"\n'
        '                x-text="hasForm ? (needsConfirm ? \'Confirm\' : \'Save\') : \'Confirm\'"></button>\n'
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
    )


class PanelRegistry:
    def __init__(self) -> None:
        self._panels: dict[str, Panel] = {}
        self._default_id: str | None = None

    def register(self, panel: Panel) -> Panel:
        self._panels[panel.id] = panel
        if panel.is_default() or self._default_id is None:
            self._default_id = panel.id
        return panel

    def get(self, panel_id: str) -> Panel | None:
        return self._panels.get(panel_id)

    def default(self, panel_id: str) -> Panel | None:
        """Mark ``panel_id`` as the default panel (must already be registered)."""
        panel = self._panels.get(panel_id)
        if panel is None:
            return None
        panel.default(True)
        self._default_id = panel_id
        return panel

    def get_default(self) -> Panel | None:
        if self._default_id and self._default_id in self._panels:
            return self._panels[self._default_id]
        panels = self.all()
        return panels[0] if panels else None

    def all(self) -> list[Panel]:
        return list(self._panels.values())
