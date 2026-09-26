"""Panel — admin shell registration (Filament Panel analogue)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Literal, Self

from almasix.orbit.panels.content_width import (
    DEFAULT_CONTENT_MAX_WIDTH,
    resolve_content_max_width,
)
from almasix.orbit.panels.discover import load_theme_css
from almasix.orbit.panels.global_search import render_global_search_input
from almasix.orbit.panels.hooks import register_render_hook, render_hook
from almasix.orbit.panels.navigation import (
    NavigationBuilder,
    NavigationGroup,
    NavigationItem,
    NavigationSubgroup,
    NavLayout,
    attrs_to_html,
    build_menu_layout,
    build_menu_secondary,
    group_items,
    nest_parent_items,
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
DEFAULT_BRAND_NAME_FONT_SIZE = "1.8rem"
# Fallback when a nav item has no icon — keeps the collapsed rail usable.
_NAV_FALLBACK_ICON = "heroicon-o-view-columns"
DEFAULT_BRAND_LOGO_HEIGHT = "2rem"
DEFAULT_SIMPLE_PAGE_MAX_CONTENT_WIDTH = "lg"
DEFAULT_SIDEBAR_WIDTH = "16rem"
DEFAULT_COLLAPSED_SIDEBAR_WIDTH = "4.5rem"

PageOption = bool | type[Page]
ThemeMode = Literal["light", "dark", "system"]
UserMenuPosition = Literal["topbar", "sidebar"]
PluginLike = Any  # ``Plugin`` / ``PanelPlugin`` or ``Callable[[Panel], Any]``
NavigationConfig = bool | NavigationBuilder | Callable[..., Any]


def _resolve_page_option(value: PageOption, *, default_cls: type[Page]) -> type[Page] | None:
    """``False`` → disabled; ``True`` → default class; page class → that class."""
    if value is False:
        return None
    if value is True:
        return default_cls
    if isinstance(value, type) and issubclass(value, Page):
        return value
    return default_cls


def _nav_subgroup_of(obj: Any) -> str | None:
    """Resolve ``navigation_subgroup`` or ``navigation_sub_category`` alias."""
    return getattr(obj, "navigation_subgroup", None) or getattr(
        obj, "navigation_sub_category", None
    )


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
        self._mfa_providers: list[Any] = []
        self._spa_enabled = False
        self._spa_url_exceptions: list[str] = []
        self._billing_provider: Any = None
        self._plugin_callbacks: list[Callable[[Panel], Any]] = []
        self._plugins: list[Any] = []
        self._boot_callbacks: list[Callable[[Panel], Any]] = []
        self._dark_mode = True
        self._theme_switcher = True
        self._default_theme_mode: ThemeMode = "system"
        self._sidebar_collapsible = False
        self._sidebar_fully_collapsible = False
        self._sidebar_width: str = DEFAULT_SIDEBAR_WIDTH
        self._collapsed_sidebar_width: str = DEFAULT_COLLAPSED_SIDEBAR_WIDTH
        self._collapsible_navigation_groups = True
        self._navigation_enabled = True
        self._navigation_builder: NavigationConfig | None = None
        self._topbar_enabled = True
        self._breadcrumbs_enabled = True
        self._discover_resources_in: list[str] = []
        self._discover_pages_in: list[str] = []
        self._discover_widgets_in: list[str] = []
        self._discover_clusters_in: list[str] = []
        self._theme_packages: list[str] = []
        self._theme_stylesheets: list[str] = []
        self._custom_nav_items: list[NavigationItem] = []
        self._nav_groups: dict[str, NavigationGroup] = {}
        self._nav_group_order: list[str] = []
        self._nav_subgroups: dict[tuple[str | None, str], NavigationSubgroup] = {}
        self._navigation_layout: NavLayout = "apps"
        self._user_menu_enabled = True
        self._user_menu_position: UserMenuPosition = "topbar"
        self._user_menu_items: list[dict[str, Any]] = []
        self._user_menu_specials: dict[str, dict[str, Any]] = {}
        self._clusters: list[type[Any]] = []
        self._notifications_enabled = True
        self._database_notifications_enabled = False
        self._database_notifications: list[dict[str, Any]] = []
        self._database_notifications_position: Literal["topbar", "sidebar"] = "topbar"
        self._database_notifications_polling: str | int | None = "30s"
        self._database_notification_store: Any = None
        self._live_broadcasts_enabled = False
        self._live_broadcasts_polling: str | int | None = "2s"
        self._broadcast_hub: Any = None
        self._uploads_enabled = True
        self._global_search_enabled = True
        self._global_search_debounce_ms = 300
        self._global_search_placeholder = "Search…"
        self._global_search_limit = 10
        self._panel_user: Any = None
        self._content_max_width: str = DEFAULT_CONTENT_MAX_WIDTH
        self._simple_page_max_content_width: str = DEFAULT_SIMPLE_PAGE_MAX_CONTENT_WIDTH
        # Back-compat alias used by older callers / routing.
        self._demo_user: Any = None
        self._tenancy: Any = None

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

    def multi_factor_authentication(self, *providers: Any) -> Self:
        """Register MFA providers (authenticator TOTP, email codes, or custom)."""
        flat: list[Any] = []
        for item in providers:
            if item is None or item is False:
                continue
            if isinstance(item, (list, tuple)):
                flat.extend(item)
            else:
                flat.append(item)
        self._mfa_providers = flat
        return self

    def get_mfa_providers(self) -> list[Any]:
        return list(self._mfa_providers)

    def has_mfa_providers(self) -> bool:
        return bool(self._mfa_providers)

    def enabled_mfa_providers(self, user: Any) -> list[Any]:
        from almasix.orbit.panels.mfa import enabled_providers

        return enabled_providers(self._mfa_providers, user)

    def tenant(
        self,
        model: type[Any] | Any | bool | None = None,
        *,
        ownership_relationship: str | None = None,
        slug_attribute: str | None = None,
    ) -> Self:
        """Enable multi-tenancy with a model, a :class:`Tenancy` config, or ``False``."""
        from almasix.orbit.panels.tenancy import Tenancy

        if model is False or model is None:
            self._tenancy = None
            return self
        if isinstance(model, Tenancy):
            self._tenancy = model
        elif model is True:
            self._tenancy = Tenancy()
        else:
            tenancy = Tenancy().model(model).tenant_route_prefix(True)  # type: ignore[arg-type]
            if ownership_relationship:
                tenancy.ownership_relationship(ownership_relationship)
            if slug_attribute:
                tenancy.slug_attribute(slug_attribute)
            self._tenancy = tenancy
        return self

    def tenant_registration(self, page: PageOption | type[Any] = True) -> Self:
        tenancy = self._ensure_tenancy()
        tenancy.registration(page)  # type: ignore[arg-type]
        return self

    def tenant_profile(self, page: PageOption | type[Any] = True) -> Self:
        tenancy = self._ensure_tenancy()
        tenancy.profile(page)  # type: ignore[arg-type]
        return self

    def tenant_billing(self, page: PageOption | type[Any] | bool = True) -> Self:
        tenancy = self._ensure_tenancy()
        tenancy.billing(page)  # type: ignore[arg-type]
        if page is not False and self._billing_provider is None:
            from almasix.orbit.panels.billing import MemoryBillingProvider

            self._billing_provider = MemoryBillingProvider()
        return self

    def billing_provider(self, provider: Any) -> Self:
        """Set the :class:`~almasix.orbit.panels.billing.BillingProvider` for this panel."""
        self._billing_provider = provider
        return self

    def get_billing_provider(self) -> Any:
        return self._billing_provider

    def spa(self, condition: bool = True) -> Self:
        """Navigate panel links without a full document reload (Alpine fetch + history)."""
        self._spa_enabled = bool(condition)
        return self

    def spa_enabled(self) -> bool:
        return bool(self._spa_enabled)

    def spa_url_exceptions(self, urls: str | Sequence[str], *more: str) -> Self:
        """Paths that always do a full page load (login/logout are excluded automatically)."""
        items: list[str] = []
        if isinstance(urls, str):
            items.append(urls)
        else:
            items.extend(str(u) for u in urls)
        items.extend(str(u) for u in more)
        self._spa_url_exceptions.extend(item for item in items if item)
        return self

    def spa_exceptions(self) -> list[str]:
        built: list[str] = []
        if self.login_enabled():
            built.append(self.url("login"))
            built.append(self.url("logout"))
        if self.signup_enabled():
            built.append(self.url("register"))
        if self.has_mfa_providers():
            built.append(self.url("mfa-challenge"))
        return built + list(self._spa_url_exceptions)

    def _spa_html_attrs(self) -> str:
        if not self._spa_enabled:
            return ""
        exceptions = ",".join(e(item) for item in self.spa_exceptions())
        root = e(self.get_path() or "/")
        return (
            f' data-orbit-spa="true" data-orbit-spa-root="{root}" '
            f'data-orbit-spa-exceptions="{exceptions}"'
        )

    def tenant_middleware(
        self,
        middleware: Sequence[Any],
        is_persistent: bool = False,
    ) -> Self:
        tenancy = self._ensure_tenancy()
        tenancy.tenant_middleware(middleware, is_persistent=is_persistent)
        return self

    def get_tenancy(self) -> Any | None:
        return self._tenancy

    def get_tenant(self) -> Any | None:
        tenancy = self._tenancy
        if tenancy is None:
            return None
        return tenancy.get_current()

    def _ensure_tenancy(self) -> Any:
        from almasix.orbit.panels.tenancy import Tenancy

        if self._tenancy is None:
            self._tenancy = Tenancy()
        return self._tenancy

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
        """Collapse the sidebar to an icon rail on desktop (Filament ``sidebarCollapsibleOnDesktop``)."""
        self._sidebar_collapsible = bool(condition)
        return self

    def sidebar_collapsible_on_desktop(self, condition: bool = True) -> Self:
        """Alias for :meth:`sidebar_collapsible`."""
        return self.sidebar_collapsible(condition)

    def sidebar_fully_collapsible_on_desktop(self, condition: bool = True) -> Self:
        """Hide the entire sidebar when collapsed (not just the icon rail)."""
        self._sidebar_fully_collapsible = bool(condition)
        if condition:
            self._sidebar_collapsible = True
        return self

    def sidebar_width(self, css: str) -> Self:
        self._sidebar_width = (css or DEFAULT_SIDEBAR_WIDTH).strip() or DEFAULT_SIDEBAR_WIDTH
        return self

    def collapsed_sidebar_width(self, css: str) -> Self:
        self._collapsed_sidebar_width = (
            (css or DEFAULT_COLLAPSED_SIDEBAR_WIDTH).strip() or DEFAULT_COLLAPSED_SIDEBAR_WIDTH
        )
        return self

    def collapsible_navigation_groups(self, condition: bool = True) -> Self:
        """Global default for whether navigation groups are collapsible."""
        self._collapsible_navigation_groups = bool(condition)
        return self

    def navigation(self, config: NavigationConfig = True) -> Self:
        """Disable navigation (``False``) or replace items via builder/callable."""
        if config is False:
            self._navigation_enabled = False
            self._navigation_builder = None
            return self
        if config is True:
            self._navigation_enabled = True
            self._navigation_builder = None
            return self
        self._navigation_enabled = True
        self._navigation_builder = config
        return self

    def topbar(self, condition: bool = True) -> Self:
        self._topbar_enabled = bool(condition)
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

    def user_menu(self, enabled: bool = True, *, position: UserMenuPosition | None = None) -> Self:
        """Enable/disable the user menu; optionally set ``topbar`` or ``sidebar`` position."""
        if enabled is False:
            self._user_menu_enabled = False
            return self
        self._user_menu_enabled = True
        if position is not None:
            self._user_menu_position = position
        return self

    def user_menu_position(self, position: UserMenuPosition) -> Self:
        self._user_menu_position = position
        return self

    def user_menu_items(
        self,
        items: Sequence[UserMenuItem | dict[str, Any]] | dict[str, Any] | None = None,
    ) -> Self:
        if items is None:
            return self
        if isinstance(items, dict):
            for key, value in items.items():
                self._register_user_menu_entry(key, value)
            return self
        for item in items:
            self.user_menu_item(item)
        return self

    def user_menu_item(self, item: UserMenuItem | dict[str, Any]) -> Self:
        if isinstance(item, UserMenuItem):
            self._user_menu_items.append(item.to_dict())
        else:
            self._user_menu_items.append(dict(item))
        return self

    def _register_user_menu_entry(self, key: str, value: Any) -> None:
        if key in ("profile", "logout"):
            if callable(value):
                base = UserMenuItem.make(key)
                if key == "logout":
                    base.label("Sign out").url(self.url("logout")).post_to_url()
                else:
                    # ``profile`` (only other special key admitted above).
                    base.label("Profile")
                customized = value(base)
                data = customized.to_dict() if isinstance(customized, UserMenuItem) else dict(customized)
                data["name"] = key
                self._user_menu_specials[key] = data
            elif isinstance(value, UserMenuItem):
                data = value.to_dict()
                data["name"] = key
                self._user_menu_specials[key] = data
            else:
                data = dict(value)
                data["name"] = key
                self._user_menu_specials[key] = data
            return
        if isinstance(value, UserMenuItem):
            self.user_menu_item(value)
        else:
            self.user_menu_item(dict(value))

    def clusters(self, clusters: Sequence[type[Any]]) -> Self:
        self._clusters.extend(list(clusters))
        return self

    def discover_clusters(self, *paths: str) -> Self:
        self._discover_clusters_in.extend(str(p) for p in paths)
        return self

    def get_clusters(self) -> list[type[Any]]:
        return list(self._clusters)

    def database_notifications(
        self,
        enabled: bool | Sequence[PanelNotification | dict[str, Any]] = True,
        *,
        position: Literal["topbar", "sidebar"] | str | None = None,
    ) -> Self:
        """Enable the database notifications bell.

        Pass ``True``/``False`` to toggle the feature, or a sequence of seed items
        (enables the feature and registers demo notifications). Optional
        ``position`` moves the trigger to ``topbar`` (default) or ``sidebar``.
        """
        if isinstance(enabled, bool):
            self._database_notifications_enabled = enabled
        else:
            self._database_notifications_enabled = True
            for item in enabled:
                self.notification(item)
        if position is not None:
            self.database_notifications_position(position)
        return self

    def database_notifications_position(
        self,
        position: Literal["topbar", "sidebar"] | str,
    ) -> Self:
        value = str(position).strip().lower()
        self._database_notifications_position = (
            "sidebar" if value == "sidebar" else "topbar"
        )
        return self

    def database_notifications_polling(self, interval: str | int | None) -> Self:
        """Polling interval for the database bell (``'30s'``, ms int, or ``None``)."""
        self._database_notifications_polling = interval
        return self

    def notification(self, item: PanelNotification | dict[str, Any]) -> Self:
        self._database_notifications_enabled = True
        if isinstance(item, PanelNotification):
            self._database_notifications.append(item.to_dict())
        else:
            self._database_notifications.append(dict(item))
        store = self._database_notification_store
        if store is not None:
            try:
                store.save(dict(self._database_notifications[-1]))
            except Exception:
                pass
        return self

    def database_notifications_enabled(self) -> bool:
        return bool(self._database_notifications_enabled)

    def database_notifications_store(self, store: Any) -> Self:
        """Use a :class:`~almasix.orbit.notifications.store.DatabaseNotificationStore`."""
        self._database_notification_store = store
        try:
            from almasix.orbit.notifications import get_notifier

            get_notifier().use_store(store)
        except Exception:
            pass
        if store is not None:
            for item in list(self._database_notifications):
                try:
                    store.save(dict(item))
                except Exception:
                    pass
        return self

    def get_notification_store(self) -> Any:
        return self._database_notification_store

    def sqlite_notifications(self, path: str = "orbit-notifications.sqlite") -> Self:
        """Persist the database bell with stdlib SQLite (file path or ``:memory:``).

        Prefer :meth:`database_notifications_using_almasix` when the app has run
        ``smith notifications:table`` — that shares the framework inbox table.
        """
        from almasix.orbit.notifications import SqliteNotificationStore

        if not self._database_notifications_enabled:
            self.database_notifications(True)
        return self.database_notifications_store(SqliteNotificationStore(path))

    def database_notifications_using_almasix(self) -> Self:
        """Persist the bell in Almasix's ``notifications`` table (Filament-style).

        Run ``smith notifications:table`` then ``smith migrate`` first. Enables
        the bell if it is not already on.
        """
        from almasix.orbit.notifications import AlmasixDatabaseNotificationStore

        if not self._database_notifications_enabled:
            self.database_notifications(True)
        return self.database_notifications_store(AlmasixDatabaseNotificationStore())

    def notifications_url(self) -> str:
        from almasix.orbit.panels.notification_routes import panel_notifications_url

        return panel_notifications_url(self)

    def live_broadcasts(
        self,
        enabled: bool | Any = True,
        *,
        polling: str | int | None = "2s",
        hub: Any = None,
    ) -> Self:
        """Enable the ``/orbit-live`` poll endpoint and bind a broadcast hub."""
        from almasix.orbit.notifications import MemoryBroadcastHub, set_broadcast_hub

        self._live_broadcasts_polling = polling
        if enabled is False:
            self._live_broadcasts_enabled = False
            return self
        if enabled is not True:
            hub = enabled
        self._live_broadcasts_enabled = True
        if hub is not None:
            self._broadcast_hub = hub
        elif self._broadcast_hub is None:
            self._broadcast_hub = MemoryBroadcastHub()
        set_broadcast_hub(self._broadcast_hub)
        return self

    def live_broadcasts_enabled(self) -> bool:
        return bool(self._live_broadcasts_enabled)

    def get_broadcast_hub(self) -> Any:
        return self._broadcast_hub

    def live_url(self) -> str:
        from almasix.orbit.panels.notification_routes import panel_live_url

        return panel_live_url(self)

    def notifications(self, condition: bool = True) -> Self:
        """Enable the toast notification host (default on)."""
        self._notifications_enabled = bool(condition)
        return self

    def uploads(self, condition: bool = True) -> Self:
        """Toggle this panel's file-upload endpoint (on by default)."""
        self._uploads_enabled = bool(condition)
        return self

    def uploads_enabled(self) -> bool:
        return bool(self._uploads_enabled)

    def upload_url(self) -> str:
        """URL ``FileUpload`` fields post to on this panel."""
        from almasix.orbit.panels.uploads import panel_upload_url

        return panel_upload_url(self)

    def global_search(
        self,
        condition: bool = True,
        *,
        debounce: int | None = None,
        placeholder: str | None = None,
        limit: int | None = None,
    ) -> Self:
        """Toggle and configure the topbar global search box (default on).

        The box only appears once at least one resource declares
        ``global_search_attributes``.
        """
        self._global_search_enabled = bool(condition)
        if debounce is not None:
            self._global_search_debounce_ms = int(debounce)
        if placeholder is not None:
            self._global_search_placeholder = str(placeholder)
        if limit is not None:
            self._global_search_limit = int(limit)
        return self

    def global_search_debounce(self, milliseconds: int) -> Self:
        self._global_search_debounce_ms = int(milliseconds)
        return self

    def global_search_placeholder(self, text: str) -> Self:
        self._global_search_placeholder = str(text)
        return self

    def global_search_limit(self, limit: int) -> Self:
        """Cap on results shown across all resources."""
        self._global_search_limit = int(limit)
        return self

    def has_global_search(self) -> bool:
        """True when search is enabled and some resource opts in."""
        if not self._global_search_enabled:
            return False
        return any(
            callable(getattr(resource, "is_globally_searchable", None))
            and resource.is_globally_searchable()
            for resource in self.get_resources()
        )

    def global_search_url(self) -> str:
        """URL of this panel's global-search endpoint."""
        prefix = self.get_path().rstrip("/")
        return f"{prefix}/global-search" if prefix and prefix != "/" else "/global-search"

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

    def navigation_groups(self, groups: Sequence[NavigationGroup | str]) -> Self:
        """Register group metadata objects, or a list of group labels for order."""
        for group in groups:
            if isinstance(group, str):
                label = group.strip()
                if label and label not in self._nav_group_order:
                    self._nav_group_order.append(label)
                if label and label not in self._nav_groups:
                    self._nav_groups[label] = NavigationGroup.make(label)
                continue
            self.navigation_group(group)
        return self

    def navigation_group(self, group: NavigationGroup) -> Self:
        """Optional group metadata (icon/sort). Group names still come from resources/pages."""
        name = group.get_name() or group.get_label()
        if name:
            self._nav_groups[str(name)] = group
            if str(name) not in self._nav_group_order:
                self._nav_group_order.append(str(name))
        # Nested fluent items on the group also register as panel nav items.
        for item in getattr(group, "_items", []) or []:
            if not item._group:
                item.group(str(name) if name else None)
            self._custom_nav_items.append(item)
        return self

    def navigation_subgroups(self, subgroups: Sequence[NavigationSubgroup]) -> Self:
        for subgroup in subgroups:
            self.navigation_subgroup(subgroup)
        return self

    def navigation_subgroup(self, subgroup: NavigationSubgroup) -> Self:
        """Register second-level nav category metadata (icon/sort/parent group)."""
        name = subgroup.get_name() or subgroup.get_label()
        if name:
            parent = getattr(subgroup, "_parent", None)
            self._nav_subgroups[(parent, str(name))] = subgroup
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
        seen_widgets: set[str] = set()
        for w in self._widgets:
            if isinstance(w, type):
                seen_widgets.add(class_key(w))
            else:
                seen_widgets.add(f"instance:{id(w)}")

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

        if self._discover_clusters_in:
            from almasix.orbit.panels.cluster import Cluster

            seen_clusters = {class_key(c) for c in self._clusters}
            for path in self._discover_clusters_in:
                for cls in discover_classes(path, base_class=Cluster):
                    key = class_key(cls)
                    if key not in seen_clusters:
                        self._clusters.append(cls)
                        seen_clusters.add(key)

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
        stack = list(self._middleware)
        tenancy = self._tenancy
        if tenancy is not None and tenancy.is_enabled():
            for item in tenancy.get_tenant_middleware():
                if item not in stack:
                    stack.append(item)
        return stack

    def get_tenant_middleware(self) -> list[Any]:
        tenancy = self._tenancy
        if tenancy is None:
            return []
        return tenancy.get_tenant_middleware()

    def _collect_navigation_items(
        self,
        *,
        user: Any = None,
        active_path: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self._navigation_enabled:
            return []

        # Stamp panel path so resource/page URL helpers include it.
        for res in self._resources:
            res._panel_path = self.get_path()  # type: ignore[attr-defined]
        for page in self._pages:
            page._panel_path = self.get_path()  # type: ignore[attr-defined]

        tenant = self.get_tenant()
        ctx: dict[str, Any] = {
            "user": user,
            "active_path": active_path,
            "panel": self,
            "tenant": tenant,
        }
        self._stamp_tenant_paths(tenant)

        # Custom builder replaces auto-generated navigation entirely.
        if self._navigation_builder is not None:
            return self._collect_from_builder(**ctx)

        items: list[dict[str, Any]] = []
        registered_clusters: set[type[Any] | str] = set()

        dash = self.dashboard_page() if self.dashboard_enabled() else None
        if dash is not None and dash not in self._pages:
            if self._should_register(dash, **ctx) and self._can_access_page(dash, user):
                items.append(
                    self._page_nav_dict(
                        dash,
                        url=self._tenant_home_url(tenant),
                        sort_default=-100,
                        **ctx,
                    )
                )

        for res in self._resources:
            cluster = self._resolve_cluster(res)
            if cluster is not None:
                registered_clusters.add(cluster if isinstance(cluster, type) else cluster)
                continue
            if not self._should_register(res, **ctx):
                continue
            if user is not None and hasattr(res, "can_view_any") and not res.can_view_any(user):
                continue
            items.append(self._resource_nav_dict(res, **ctx))

        for page in self._pages:
            cluster = self._resolve_cluster(page)
            if cluster is not None:
                registered_clusters.add(cluster if isinstance(cluster, type) else cluster)
                continue
            if dash is not None and page is dash:
                if self._should_register(page, **ctx) and self._can_access_page(page, user):
                    items.append(
                        self._page_nav_dict(
                            page,
                            url=self._tenant_home_url(tenant),
                            sort_default=-100,
                            **ctx,
                        )
                    )
                continue
            if not self._should_register(page, **ctx):
                continue
            if not self._can_access_page(page, user):
                continue
            items.append(self._page_nav_dict(page, **ctx))

        # One main-nav entry per cluster that has members on this panel.
        for cluster in self._iter_clusters_for_nav(registered_clusters):
            cluster_item = self._cluster_nav_dict(cluster, **ctx)
            if cluster_item is not None:
                items.append(cluster_item)

        for item in self._custom_nav_items:
            if not item.is_visible(**ctx):
                continue
            nav = item.to_nav_dict(**ctx)
            items.append(nav)

        items.sort(key=lambda i: (i.get("sort") or 0, i.get("label") or ""))
        return items

    def _collect_from_builder(self, **ctx: Any) -> list[dict[str, Any]]:
        builder = self._navigation_builder
        if callable(builder) and not isinstance(builder, NavigationBuilder):
            result = builder(NavigationBuilder.make())
            if isinstance(result, NavigationBuilder):
                builder = result
            elif result is False:
                return []
            else:
                builder = result
        if not isinstance(builder, NavigationBuilder):
            return []
        for group in builder.get_groups():
            name = group.get_name() or group.get_label()
            if name:
                self._nav_groups[str(name)] = group
        items: list[dict[str, Any]] = []
        for item in builder.get_items():
            if not item.is_visible(**ctx):
                continue
            items.append(item.to_nav_dict(**ctx))
        items.sort(key=lambda i: (i.get("sort") or 0, i.get("label") or ""))
        return items

    def _tenant_home_url(self, tenant: Any = None) -> str:
        """Dashboard URL, including the current tenant slug when prefixes are on."""
        tenancy = self._tenancy
        slug = getattr(tenant, "slug", None) if tenant is not None else None
        if (
            tenancy is not None
            and tenancy.is_enabled()
            and tenancy.get_tenant_route_prefix()
            and slug
        ):
            extra = tenancy.route_prefix_segment()
            return self.url(extra, str(slug)) if extra else self.url(str(slug))
        return self.url()

    def _stamp_tenant_paths(self, tenant: Any = None) -> None:
        """Stamp ``_tenant_path`` on resources/pages when tenant URL prefixes are on."""
        tenancy = self._tenancy
        segment = ""
        if tenancy is not None and tenancy.is_enabled() and tenancy.get_tenant_route_prefix():
            slug = None
            if tenant is not None:
                slug = getattr(tenant, "slug", None) or str(getattr(tenant, "id", "") or "")
            segment = tenancy.path_prefix_for(slug or None)
        for res in self._resources:
            res._tenant_path = segment  # type: ignore[attr-defined]
        for page in self._pages:
            page._tenant_path = segment  # type: ignore[attr-defined]

    def _should_register(self, obj: Any, **ctx: Any) -> bool:
        getter = getattr(obj, "get_should_register_navigation", None)
        if callable(getter):
            return bool(getter(**ctx))
        flag = getattr(obj, "should_register_navigation", True)
        if callable(flag):
            return bool(flag(**ctx))
        return bool(flag)

    def _can_access_page(self, page: Any, user: Any) -> bool:
        if user is None:
            # No auth context — keep pages visible (guest shells / tests).
            return True
        can = getattr(page, "can_access", None)
        if callable(can):
            return bool(can(user))
        return True

    def _resolve_cluster(self, obj: Any) -> type[Any] | str | None:
        getter = getattr(obj, "get_cluster", None)
        if callable(getter):
            return getter()
        return getattr(obj, "cluster", None)

    def _cluster_key(self, cluster: type[Any] | str) -> str:
        if isinstance(cluster, str):
            return cluster
        return f"{cluster.__module__}.{cluster.__qualname__}"

    def _iter_clusters_for_nav(
        self, registered: set[type[Any] | str]
    ) -> list[type[Any]]:
        """Return concrete Cluster classes for main-nav entries."""
        by_key: dict[str, type[Any]] = {}
        for cluster in self._clusters:
            by_key[self._cluster_key(cluster)] = cluster
        out: list[type[Any]] = []
        seen: set[str] = set()
        for cluster in registered:
            if isinstance(cluster, type):
                key = self._cluster_key(cluster)
                if key not in seen:
                    out.append(cluster)
                    seen.add(key)
                continue
            # String name — match registered panel clusters by slug/name.
            for cand in self._clusters:
                if cand.get_slug() == cluster or cand.__name__ == cluster:
                    key = self._cluster_key(cand)
                    if key not in seen:
                        out.append(cand)
                        seen.add(key)
                    break
            else:
                # Synthesize a minimal cluster class from the string slug.
                from almasix.orbit.panels.cluster import Cluster

                slug_value = str(cluster)
                label = slug_value.replace("_", " ").replace("-", " ").title()
                class_name = f"{slug_value.title().replace('_', '').replace('-', '')}Cluster"
                # ``type()`` avoids class-body scoping (locals are not visible as ``slug = slug``).
                _DynamicCluster = type(
                    class_name,
                    (Cluster,),
                    {
                        "slug": slug_value,
                        "navigation_label": label,
                    },
                )
                key = self._cluster_key(_DynamicCluster)
                if key not in seen:
                    out.append(_DynamicCluster)
                    seen.add(key)
        # Also include explicitly registered clusters that have members
        for cluster in self._clusters:
            key = self._cluster_key(cluster)
            members = self._cluster_members(cluster)
            if members and key not in seen:
                out.append(cluster)
                seen.add(key)
        return out

    def _cluster_members(self, cluster: type[Any] | str) -> list[type[Any]]:
        members: list[type[Any]] = []
        key = self._cluster_key(cluster) if not isinstance(cluster, str) else None
        slug = cluster.get_slug() if isinstance(cluster, type) else str(cluster)
        for obj in list(self._resources) + list(self._pages):
            resolved = self._resolve_cluster(obj)
            if resolved is None:
                continue
            if resolved is cluster or resolved == cluster:
                members.append(obj)
                continue
            if isinstance(resolved, type) and key and self._cluster_key(resolved) == key:
                members.append(obj)
                continue
            if isinstance(resolved, str) and resolved in (slug, getattr(cluster, "__name__", "")):
                members.append(obj)
        return members

    def _cluster_nav_dict(self, cluster: type[Any], **ctx: Any) -> dict[str, Any] | None:
        user = ctx.get("user")
        members = self._cluster_members(cluster)
        if not members:
            return None
        # First visible member URL becomes the cluster landing link.
        first_url = None
        for member in sorted(
            members,
            key=lambda m: (
                int(getattr(m, "navigation_sort", 0) or 0),
                str(getattr(m, "get_navigation_label", lambda: m.__name__)()),
            ),
        ):
            if not self._should_register(member, **ctx):
                continue
            if hasattr(member, "can_view_any") and user is not None:
                if not member.can_view_any(user):
                    continue
            if hasattr(member, "can_access") and not self._can_access_page(member, user):
                continue
            first_url = self._member_url(member)
            break
        if not first_url:
            return None
        return {
            "slug": cluster.get_slug(),
            "label": cluster.get_navigation_label(),
            "icon": getattr(cluster, "navigation_icon", None) or "heroicon-o-squares-2x2",
            "active_icon": getattr(cluster, "active_navigation_icon", None),
            "group": getattr(cluster, "navigation_group", None),
            "subgroup": None,
            "url": first_url,
            "sort": getattr(cluster, "navigation_sort", 0),
            "badge": None,
            "badge_color": None,
            "badge_tooltip": None,
            "open_in_new_tab": False,
            "parent_item": None,
            "cluster": True,
            "cluster_slug": cluster.get_slug(),
        }

    def _member_url(self, member: type[Any]) -> str:
        if hasattr(member, "get_pages") and callable(member.get_pages):
            pages = member.get_pages()
            if isinstance(pages, dict) and pages.get("index"):
                return str(pages["index"])
        slug = member.get_slug() if hasattr(member, "get_slug") else member.__name__.lower()
        prefix = ""
        if hasattr(member, "get_url_path_prefix"):
            prefix = member.get_url_path_prefix()
        else:
            prefix = (self._path or "").rstrip("/")
            cluster = self._resolve_cluster(member)
            if cluster is not None:
                if isinstance(cluster, type):
                    prefix = f"{prefix}{cluster.path_prefix()}"
                else:
                    prefix = f"{prefix}/{cluster}"
        return f"{prefix}/{slug}" if prefix else f"/{slug}"

    def _resource_nav_dict(self, res: type[Any], **ctx: Any) -> dict[str, Any]:
        badge = res.get_navigation_badge(**ctx) if hasattr(res, "get_navigation_badge") else None
        return {
            "slug": res.get_slug(),
            "label": res.get_navigation_label(),
            "icon": getattr(res, "navigation_icon", "heroicon-o-users"),
            "active_icon": getattr(res, "active_navigation_icon", None),
            "group": getattr(res, "navigation_group", None),
            "subgroup": _nav_subgroup_of(res),
            "url": self._member_url(res),
            "sort": getattr(res, "navigation_sort", 0),
            "badge": badge,
            "badge_color": (
                res.get_navigation_badge_color(**ctx)
                if hasattr(res, "get_navigation_badge_color")
                else None
            ),
            "badge_tooltip": (
                res.get_navigation_badge_tooltip(**ctx)
                if hasattr(res, "get_navigation_badge_tooltip")
                else None
            ),
            "open_in_new_tab": False,
            "parent_item": (
                res.get_navigation_parent_item()
                if hasattr(res, "get_navigation_parent_item")
                else getattr(res, "navigation_parent_item", None)
            ),
        }

    def _page_nav_dict(
        self,
        page: type[Any],
        *,
        url: str | None = None,
        sort_default: int = 0,
        **ctx: Any,
    ) -> dict[str, Any]:
        slug = page.get_slug() if hasattr(page, "get_slug") else page.__name__.lower()
        if url is None:
            prefix = ""
            if hasattr(page, "get_url_path_prefix"):
                # Ensure panel path is available for page URL building.
                if not getattr(page, "_panel_path", None):
                    page._panel_path = self.get_path()  # type: ignore[attr-defined]
                prefix = page.get_url_path_prefix()
            else:
                prefix = (self._path or "").rstrip("/")
            url = f"{prefix}/{slug}" if prefix else self.url(slug)
        badge = page.get_navigation_badge(**ctx) if hasattr(page, "get_navigation_badge") else None
        return {
            "slug": slug,
            "label": page.get_navigation_label(),
            "icon": getattr(page, "navigation_icon", "heroicon-o-home"),
            "active_icon": getattr(page, "active_navigation_icon", None),
            "group": getattr(page, "navigation_group", None),
            "subgroup": _nav_subgroup_of(page),
            "url": url,
            "sort": getattr(page, "navigation_sort", sort_default),
            "badge": badge,
            "badge_color": (
                page.get_navigation_badge_color(**ctx)
                if hasattr(page, "get_navigation_badge_color")
                else None
            ),
            "badge_tooltip": (
                page.get_navigation_badge_tooltip(**ctx)
                if hasattr(page, "get_navigation_badge_tooltip")
                else None
            ),
            "open_in_new_tab": False,
            "parent_item": (
                page.get_navigation_parent_item()
                if hasattr(page, "get_navigation_parent_item")
                else getattr(page, "navigation_parent_item", None)
            ),
        }

    def menu_layout_context(
        self, active_path: str | None = None, *, user: Any = None
    ) -> Any:
        meta = dict(self._nav_groups)
        group_order = list(self._nav_group_order)
        # Ensure the Dashboard group is always the first apps/sidebar root.
        if self.dashboard_enabled():
            dash = self.dashboard_page()
            if dash is not None:
                group_name = getattr(dash, "navigation_group", None) or dash.get_navigation_label()
                if group_name:
                    gname = str(group_name)
                    if gname not in meta:
                        meta[gname] = (
                            NavigationGroup.make(gname)
                            .icon(getattr(dash, "navigation_icon", "heroicon-o-home"))
                            .sort(getattr(dash, "navigation_sort", -100))
                        )
                    if gname in group_order:
                        group_order.remove(gname)
                    group_order.insert(0, gname)
        # Stamp panel path onto resources/pages so URL helpers include it.
        for res in self._resources:
            res._panel_path = self.get_path()  # type: ignore[attr-defined]
        for page in self._pages:
            page._panel_path = self.get_path()  # type: ignore[attr-defined]
        return build_menu_layout(
            self._collect_navigation_items(user=user, active_path=active_path),
            group_meta=meta,
            subgroup_meta=dict(self._nav_subgroups),
            active_path=active_path,
            layout=normalize_nav_layout(self._navigation_layout),
            panel_path=self._path,
            group_order=group_order or None,
        )

    def collect_cluster_sub_navigation(
        self,
        active_path: str | None = None,
        *,
        user: Any = None,
    ) -> tuple[type[Any] | None, list[dict[str, Any]]]:
        """Return ``(cluster, items)`` when ``active_path`` is inside a cluster."""
        if not active_path:
            return None, []
        path = active_path.rstrip("/") or "/"
        base = (self._path or "/").rstrip("/")
        for cluster in self._iter_clusters_for_nav(
            {c for c in (self._resolve_cluster(o) for o in list(self._resources) + list(self._pages)) if c}
        ):
            prefix = f"{base}{cluster.path_prefix()}".rstrip("/")
            if path == prefix or path.startswith(prefix + "/"):
                items: list[dict[str, Any]] = []
                ctx = {"user": user, "active_path": active_path, "panel": self}
                for member in self._cluster_members(cluster):
                    if not self._should_register(member, **ctx):
                        continue
                    if hasattr(member, "can_view_any") and user is not None:
                        if not member.can_view_any(user):
                            continue
                    if hasattr(member, "can_access") and not self._can_access_page(member, user):
                        continue
                    if hasattr(member, "get_pages"):
                        items.append(self._resource_nav_dict(member, **ctx))
                    else:
                        items.append(self._page_nav_dict(member, **ctx))
                items.sort(key=lambda i: (i.get("sort") or 0, i.get("label") or ""))
                from almasix.orbit.panels.navigation import apply_active_state

                return cluster, apply_active_state(items, active_path=active_path)
        return None, []

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
        record_title: str | None = None,
    ) -> str:
        """Render the admin document shell around page ``content``.

        ``bare=True`` skips sidebar/topbar (auth pages). ``extra_head`` injects
        Conduit/Alpine asset tags when mounting live hosts.
        """
        layout = normalize_nav_layout(self._navigation_layout)
        ctx = self.menu_layout_context(active_path=active_path, user=user)
        brand = e(self._brand)
        font = e(self._font)
        collapsible = self._sidebar_collapsible
        fully_collapsible = self._sidebar_fully_collapsible
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
        sidebar_w = e(self._sidebar_width or DEFAULT_SIDEBAR_WIDTH)
        collapsed_w = e(self._collapsed_sidebar_width or DEFAULT_COLLAPSED_SIDEBAR_WIDTH)
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
                f"{self._render_toast_host()}"
            )
            app_wrap = body_inner
        else:
            show_sidebar = self._navigation_enabled and layout != "top"
            show_topbar = self._topbar_enabled
            sidebar_html = (
                self._render_sidebar(ctx, collapsible, user=user) if show_sidebar else ""
            )
            topbar_html = (
                self._render_topbar(ctx, user=user, collapsible=collapsible)
                if show_topbar
                else ""
            )
            # User menu in sidebar when positioned there or topbar is off.
            if (
                self._user_menu_enabled
                and user is not None
                and (
                    self._user_menu_position == "sidebar"
                    or not show_topbar
                )
                and show_sidebar
            ):
                sidebar_html = sidebar_html.replace(
                    "</aside>",
                    f'{self._render_user_menu(user=user, placement="sidebar")}</aside>',
                    1,
                )
            # Tenant switcher in sidebar when the topbar is off (still tenancy-aware).
            if (
                not show_topbar
                and show_sidebar
                and self._tenancy is not None
                and self._tenancy.is_enabled()
            ):
                switcher = self._tenancy.render_switcher(user=user, panel=self)
                if switcher:
                    sidebar_html = sidebar_html.replace(
                        "</aside>",
                        f'<div class="or-tenant-switcher-sidebar">{switcher}</div></aside>',
                        1,
                    )
            cluster, cluster_items = self.collect_cluster_sub_navigation(
                active_path, user=user
            )
            cluster_nav = self._render_cluster_sub_nav(cluster, cluster_items)
            modal_html = _action_modal_html()
            app_class = "or-app"
            if layout == "sidebar_topbar":
                app_class += " or-app-split or-app-apps"
            if layout == "top":
                app_class += " or-app-top"
            if layout == "sidebar":
                app_class += " or-app-sidebar"
            if not show_sidebar:
                app_class += " or-app-no-sidebar"
            if fully_collapsible:
                app_class += " or-app-fully-collapsible"
            collapse_bind = ""
            if collapsible and layout != "top" and show_sidebar:
                if fully_collapsible:
                    collapse_bind = ", 'is-collapsed': collapsed, 'is-fully-collapsed': collapsed"
                else:
                    collapse_bind = ", 'is-collapsed': collapsed"
            content_inner = content
            if cluster_nav:
                position = getattr(cluster, "sub_navigation_position", "start")
                if position == "top":
                    content_inner = (
                        '<div class="or-cluster-layout or-cluster-layout-top">'
                        f"{cluster_nav}"
                        f'<div class="or-cluster-body">{content}</div></div>'
                    )
                elif position == "end":
                    content_inner = (
                        '<div class="or-cluster-layout or-cluster-layout-end">'
                        f'<div class="or-cluster-body">{content}</div>{cluster_nav}</div>'
                    )
                else:
                    content_inner = (
                        '<div class="or-cluster-layout or-cluster-layout-start">'
                        f"{cluster_nav}"
                        f'<div class="or-cluster-body">{content}</div></div>'
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
                f"{self._render_breadcrumbs(active_path, record_title)}"
                f'    <main class="or-content">{content_inner}</main>\n'
                f'    {render_hook("panels::content.end", scope=scope, user=user)}\n'
                "  </div>\n"
                "</div>\n"
                f"{modal_html}"
                f"{self._render_toast_host()}"
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
            f'<html lang="en" translate="no" data-orbit-panel="{e(self.id)}" '
            f'data-theme="light"{self._spa_html_attrs()}>\n'
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
            '  <link rel="stylesheet" href="/vendor/orbit/rich-editor/styles.css" />\n'
            '  <link rel="stylesheet" href="/vendor/orbit/rich-editor/simple.css" />\n'
            '  <link rel="stylesheet" href="/vendor/orbit/rich-editor/notion.css" />\n'
            '  <link rel="stylesheet" href="/vendor/orbit/filepond.bundle.min.css" />\n'
            '  <link rel="stylesheet" href="/vendor/orbit/flowbite-datepicker.min.css" />\n'
            # Chart + FilePond before orbit.js so boot hooks find globals.
            '  <script src="/vendor/orbit/chart.umd.min.js"></script>\n'
            '  <script src="/vendor/orbit/apexcharts.min.js"></script>\n'
            '  <script src="/vendor/orbit/filepond.bundle.min.js"></script>\n'
            # Datepicker Alpine host before orbit.js; Flowbite lib loads lazily on first open.
            '  <script src="/vendor/orbit/orbit-datepicker.js"></script>\n'
            # Register Alpine data before any Alpine CDN tag (Conduit may inject one in extra_head).
            '  <script src="/vendor/orbit/orbit.js"></script>\n'
            f"  <style>:root {{ --or-font: '{font}', ui-sans-serif, system-ui, sans-serif; "
            f"{color_vars}--or-brand-name-size: {brand_name_size}; "
            f"--or-brand-logo-height: {brand_logo_height}; "
            f"--or-sidebar-w: {sidebar_w}; --or-sidebar-collapsed-w: {collapsed_w}; "
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

    def breadcrumbs(
        self,
        active_path: str | None = None,
        *,
        record_title: str | None = None,
    ) -> list[dict[str, str | None]]:
        """Resolve breadcrumb items for ``active_path``.

        Each item is ``{"label": str, "url": str | None}``. The last item is the
        current page (``url`` is ``None``). ``record_title`` replaces the generic
        "View" / "Edit" leaf on a record page.
        """
        for res in self._resources:
            res._panel_path = self.get_path()  # type: ignore[attr-defined]
        for page in self._pages:
            page._panel_path = self.get_path()  # type: ignore[attr-defined]
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
        # Cluster-prefixed paths: /{panel}/{cluster}/{resource}/...
        cluster_match = None
        for cluster in self.get_clusters() or []:
            if cluster.get_slug() == slug:
                cluster_match = cluster
                break
        if cluster_match is None:
            # Also detect clusters implied by resource/page membership.
            for obj in list(self._resources) + list(self._pages):
                cluster = self._resolve_cluster(obj)
                if isinstance(cluster, type) and cluster.get_slug() == slug:
                    cluster_match = cluster
                    if cluster not in self._clusters:
                        self._clusters.append(cluster)
                    break

        if cluster_match is not None:
            cluster_url = self.url(cluster_match.get_slug())
            # Prefer first member URL for the cluster breadcrumb link.
            members = self._cluster_members(cluster_match)
            if members:
                cluster_url = self._member_url(members[0])
            crumbs.append(
                {
                    "label": cluster_match.get_cluster_breadcrumb()
                    if hasattr(cluster_match, "get_cluster_breadcrumb")
                    else cluster_match.get_navigation_label(),
                    "url": cluster_url,
                }
            )
            segments = segments[1:]
            if not segments:
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
            index_url = self._member_url(resource)
            crumbs.append({"label": label, "url": index_url})
            if len(segments) == 1:
                crumbs[-1]["url"] = None
                return crumbs
            action = segments[-1]
            title = str(record_title).strip() if record_title else ""
            if action == "create":
                crumbs.append({"label": "Create", "url": None})
            elif action == "edit":
                if title:
                    crumbs.append(
                        {"label": title, "url": self._record_view_url(resource, segments)}
                    )
                crumbs.append({"label": "Edit", "url": None})
            else:
                # /{slug}/{id} view (len(segments) >= 2 after the early return above)
                crumbs.append({"label": title or "View", "url": None})
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

    def _record_view_url(self, resource: Any, segments: list[str]) -> str | None:
        """View URL for ``/{slug}/{id}/edit`` so the record crumb stays clickable."""
        if len(segments) < 2:
            return None
        try:
            return str(resource.page_url("view", {"id": segments[1]}))
        except Exception:
            return None

    def _render_breadcrumbs(
        self, active_path: str | None, record_title: str | None = None
    ) -> str:
        if not self._breadcrumbs_enabled:
            return ""
        items = self.breadcrumbs(active_path, record_title=record_title)
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

    def _nav_group(
        self,
        label: str,
        *,
        group: NavigationGroup | None = None,
        children_html: str = "",
        open: bool = True,
    ) -> str:
        tip = e(label)
        extra = ""
        if group is not None:
            extra = attrs_to_html(group.get_extra_sidebar_attributes())
        collapsible = self._collapsible_navigation_groups
        collapsed = False
        if group is not None:
            collapsible = group.is_collapsible() and self._collapsible_navigation_groups
            collapsed = group.is_collapsed()
        if collapsible and children_html:
            open_js = "false" if collapsed and not open else ("true" if open or not collapsed else "false")
            if open:
                open_js = "true"
            return (
                f'<div class="or-nav-group or-nav-group-collapsible" data-tooltip="{tip}" '
                f'x-data="{{ open: {open_js} }}"{extra}>'
                f'<button type="button" class="or-nav-group-trigger" @click="open = !open" '
                f':aria-expanded="open.toString()">'
                f'<span class="or-nav-group-label">{tip}</span>'
                f'{render_icon("heroicon-o-chevron-down", size=14, css_class="or-icon or-nav-group-chevron")}'
                f"</button>"
                f'<div class="or-nav-group-panel" x-show="open" x-cloak>{children_html}</div>'
                f"</div>"
            )
        return (
            f'<div class="or-nav-group" data-tooltip="{tip}" role="presentation"{extra}>'
            f'<span class="or-nav-group-label">{tip}</span>'
            f'<span class="or-nav-group-mark" aria-hidden="true"></span>'
            f"</div>"
            f"{children_html}"
        )

    def _nav_icon(self, name: str | None) -> str:
        """SVG for a nav item; always returns real SVG (fallback if unknown/empty)."""
        from almasix.orbit.support.icons import has_icon

        return render_icon(name if has_icon(name) else _NAV_FALLBACK_ICON)

    def _nav_badge(
        self,
        badge: str | None,
        *,
        color: str | None = None,
        tooltip: str | None = None,
    ) -> str:
        if not badge:
            return ""
        color_cls = f" or-nav-badge-{e(color)}" if color else ""
        tip = f' title="{e(tooltip)}"' if tooltip else ""
        return f'<span class="or-nav-badge{color_cls}"{tip}>{e(badge)}</span>'

    def _nav_link(
        self,
        href: str,
        label: str,
        icon: str | None,
        *,
        active: bool = False,
        active_icon: str | None = None,
        badge: str | None = None,
        badge_color: str | None = None,
        badge_tooltip: str | None = None,
        open_in_new_tab: bool = False,
        children: list[dict[str, Any]] | None = None,
        nested: bool = False,
    ) -> str:
        display_icon = active_icon if active and active_icon else icon
        ic = self._nav_icon(display_icon)
        active_cls = " is-active" if active else ""
        nested_cls = " or-nav-link-nested" if nested else ""
        tip = e(label)
        target = ' target="_blank" rel="noopener noreferrer"' if open_in_new_tab else ""
        badge_html = self._nav_badge(badge, color=badge_color, tooltip=badge_tooltip)
        link = (
            f'<a class="or-nav-link{active_cls}{nested_cls}" href="{e(href)}"{target} '
            f'data-tooltip="{tip}" @click="closeDrawer()">'
            f"{ic}<span>{tip}</span>{badge_html}</a>"
        )
        if not children:
            return link
        child_html = "".join(
            self._nav_link(
                str(c.get("url") or "#"),
                str(c.get("label") or ""),
                c.get("icon"),
                active=bool(c.get("active")),
                active_icon=c.get("active_icon"),
                badge=c.get("badge"),
                badge_color=c.get("badge_color"),
                badge_tooltip=c.get("badge_tooltip"),
                open_in_new_tab=bool(c.get("open_in_new_tab")),
                children=c.get("children") or None,
                nested=True,
            )
            for c in children
        )
        parent_active = active or any(c.get("active") for c in children)
        return (
            f'<div class="or-nav-parent{" is-active" if parent_active else ""}">'
            f"{link}"
            f'<div class="or-nav-children">{child_html}</div></div>'
        )

    def _nav_accordion(self, label: str, icon: str | None, children_html: str, *, open: bool) -> str:
        tip = e(label)
        ic = self._nav_icon(icon)
        chev = render_icon("heroicon-o-chevron-down", size=14, css_class="or-icon or-nav-accordion-chevron")
        open_js = "true" if open else "false"
        active_cls = " is-active" if open else ""
        return (
            f'<div class="or-nav-accordion{active_cls}" '
            f'x-data="{{ open: {open_js} }}" data-tooltip="{tip}">'
            f'<button type="button" class="or-nav-accordion-trigger" '
            f'@click="open = !open" :aria-expanded="open.toString()">'
            f"{ic}<span>{tip}</span>{chev}</button>"
            f'<div class="or-nav-accordion-panel" x-show="open" x-cloak>{children_html}</div>'
            f"</div>"
        )

    def _render_flat_nav_tree(self, items: list[dict[str, Any]]) -> str:
        """Sidebar tree: group labels + optional subgroup accordions + links."""
        nested = nest_parent_items(list(items))
        grouped = group_items(nested)

        def _group_sort_key(g: str | None) -> tuple[Any, ...]:
            members = grouped[g]
            item_min = min((int(m.get("sort") or 0) for m in members), default=0)
            if g is None:
                return (item_min, len(self._nav_group_order), "")
            order_idx = (
                self._nav_group_order.index(g)
                if g in self._nav_group_order
                else len(self._nav_group_order)
            )
            meta_sort = (
                self._nav_groups[g]._sort if g in self._nav_groups else item_min
            )
            return (min(item_min, int(meta_sort)), order_idx, g)

        ordered = sorted(grouped.keys(), key=_group_sort_key)
        parts: list[str] = []
        for key in ordered:
            members = grouped[key]
            group_meta = self._nav_groups.get(str(key)) if key else None
            secondary = build_menu_secondary(
                members,
                active_url=next(
                    (str(m["url"]) for m in members if m.get("active")),
                    None,
                ),
                subgroup_meta=self._nav_subgroups,
                parent_group=key,
            )
            group_children: list[str] = []
            group_has_active = False
            for entry in secondary:
                matching = next((m for m in members if m.get("label") == entry.label), None)
                nested_children = (matching or {}).get("children") or []
                if entry.children:
                    children = "".join(
                        self._nav_link(
                            c.href,
                            c.label,
                            c.icon,
                            active=c.active,
                            active_icon=getattr(c, "active_icon", None),
                            badge=getattr(c, "badge", None),
                            badge_color=getattr(c, "badge_color", None),
                            badge_tooltip=getattr(c, "badge_tooltip", None),
                            open_in_new_tab=getattr(c, "open_in_new_tab", False),
                        )
                        for c in entry.children
                    )
                    group_children.append(
                        self._nav_accordion(
                            entry.label,
                            entry.icon,
                            children,
                            open=entry.active or any(c.active for c in entry.children),
                        )
                    )
                    if entry.active or any(c.active for c in entry.children):
                        group_has_active = True
                else:
                    link = self._nav_link(
                        entry.href or "#",
                        entry.label,
                        entry.icon,
                        active=entry.active,
                        active_icon=getattr(entry, "active_icon", None),
                        badge=getattr(entry, "badge", None),
                        badge_color=getattr(entry, "badge_color", None),
                        badge_tooltip=getattr(entry, "badge_tooltip", None),
                        open_in_new_tab=getattr(entry, "open_in_new_tab", False),
                        children=nested_children or None,
                    )
                    group_children.append(link)
                    if entry.active or any(c.get("active") for c in nested_children):
                        group_has_active = True
            children_html = "".join(group_children)
            if key:
                only = secondary[0] if len(secondary) == 1 else None
                matching = (
                    next((m for m in members if m.get("label") == only.label), None)
                    if only is not None
                    else None
                )
                # Dashboard-style singleton: group label == sole link label →
                # render the link at the top level (no one-item collapsible nest).
                if (
                    only is not None
                    and str(only.label) == str(key)
                    and not only.children
                    and not (matching or {}).get("children")
                ):
                    parts.append(children_html)
                else:
                    parts.append(
                        self._nav_group(
                            str(key),
                            group=group_meta,
                            children_html=children_html,
                            open=group_has_active,
                        )
                    )
            else:
                parts.append(children_html)
        return "".join(parts)

    def _render_cluster_sub_nav(
        self, cluster: type[Any] | None, items: list[dict[str, Any]]
    ) -> str:
        if cluster is None or not items:
            return ""
        should = True
        getter = getattr(cluster, "get_should_register_sub_navigation", None)
        if callable(getter):
            should = bool(getter())
        else:
            should = bool(getattr(cluster, "should_register_sub_navigation", True))
        if not should:
            return ""
        position = getattr(cluster, "sub_navigation_position", "start")
        links = "".join(
            self._nav_link(
                str(i.get("url") or "#"),
                str(i.get("label") or ""),
                i.get("icon"),
                active=bool(i.get("active")),
                active_icon=i.get("active_icon"),
                badge=i.get("badge"),
                badge_color=i.get("badge_color"),
                badge_tooltip=i.get("badge_tooltip"),
            )
            for i in items
        )
        return (
            f'<nav class="or-cluster-nav or-cluster-nav-{e(position)}" '
            f'aria-label="{e(cluster.get_navigation_label())}">{links}</nav>'
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
            nav = self._render_flat_nav_tree(list(ctx.flat_items))

        mobile_nav = ""
        if layout == "sidebar_topbar":
            mobile_nav = (
                f'<nav class="or-sidebar-nav or-nav-mobile" aria-label="Mobile navigation">'
                f"{self._render_flat_nav_tree(list(ctx.flat_items))}</nav>"
            )

        footer = ""
        if user is not None:
            label = e(getattr(user, "name", None) or getattr(user, "email", None) or "Signed in")
            footer = (
                '<div class="or-sidebar-footer">'
                f'Signed in as <strong>{label}</strong></div>'
            )

        db_notify = ""
        if (
            self._notifications_enabled
            and self._database_notifications_enabled
            and (
                self._database_notifications_position == "sidebar"
                or not self._topbar_enabled
            )
        ):
            db_notify = (
                f'<div class="or-sidebar-notifications">'
                f"{self._render_database_notifications_trigger(user=user)}</div>"
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
            f"{db_notify}\n"
            f"{footer}\n"
            "  </aside>\n"
        )

    def _render_topbar(self, ctx: Any, *, user: Any = None, collapsible: bool = False) -> str:
        layout = normalize_nav_layout(ctx.layout)
        secondary = []
        for item in ctx.menu_secondary:
            item_icon_name = (
                item.active_icon if item.active and getattr(item, "active_icon", None) else item.icon
            )
            item_icon = render_icon(item_icon_name) if item_icon_name else ""
            badge = self._nav_badge(
                getattr(item, "badge", None),
                color=getattr(item, "badge_color", None),
                tooltip=getattr(item, "badge_tooltip", None),
            )
            target = (
                ' target="_blank" rel="noopener noreferrer"'
                if getattr(item, "open_in_new_tab", False)
                else ""
            )
            if item.children:
                child_bits: list[str] = []
                for c in item.children:
                    child_active = " is-active" if c.active else ""
                    child_target = (
                        ' target="_blank" rel="noopener noreferrer"'
                        if getattr(c, "open_in_new_tab", False)
                        else ""
                    )
                    child_icon_name = (
                        c.active_icon
                        if c.active and getattr(c, "active_icon", None)
                        else c.icon
                    )
                    child_icon = render_icon(child_icon_name) if child_icon_name else ""
                    child_badge = self._nav_badge(
                        getattr(c, "badge", None),
                        color=getattr(c, "badge_color", None),
                        tooltip=getattr(c, "badge_tooltip", None),
                    )
                    child_bits.append(
                        f'<a class="or-topnav-child{child_active}" href="{e(c.href)}"{child_target}>'
                        f"{child_icon}<span>{e(c.label)}</span>{child_badge}</a>"
                    )
                children = "".join(child_bits)
                extra = ""
                group_meta = self._nav_groups.get(item.label)
                if group_meta is not None:
                    extra = attrs_to_html(group_meta.get_extra_topbar_attributes())
                secondary.append(
                    f'<div class="or-topnav-dropdown{" is-active" if item.active else ""}" '
                    f'x-data="{{ open: false }}" @click.outside="open = false"{extra}>'
                    f'<button type="button" class="or-topnav-link" @click="open = !open">'
                    f"{item_icon}<span>{e(item.label)}</span>{badge}"
                    f"{render_icon('heroicon-o-chevron-down', size=14, css_class='or-icon or-topnav-chevron')}"
                    f"</button>"
                    f'<div class="or-topnav-menu" x-show="open" x-cloak>{children}</div></div>'
                )
            else:
                active = " is-active" if item.active else ""
                href = e(item.href or "#")
                secondary.append(
                    f'<a class="or-topnav-link{active}" href="{href}"{target}>'
                    f"{item_icon}<span>{e(item.label)}</span>{badge}</a>"
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

    def _render_user_menu_items_html(self, *, user: Any = None) -> str:
        items = [dict(i) for i in self._user_menu_items if i.get("visible", True)]

        # Filament-style special keys registered via ``user_menu_items({"profile": …})``.
        if "profile" in self._user_menu_specials:
            profile = dict(self._user_menu_specials["profile"])
            if profile.get("visible", True) and not any(i.get("name") == "profile" for i in items):
                items.insert(0, profile)

        has_logout = any(i.get("name") == "logout" for i in items)
        if "logout" in self._user_menu_specials:
            logout = dict(self._user_menu_specials["logout"])
            if logout.get("visible", True) and not has_logout:
                items.append(logout)
                has_logout = True
        if not has_logout:
            items.append(
                {
                    "name": "logout",
                    "label": "Sign out",
                    "url": self.url("logout"),
                    "icon": "heroicon-o-arrow-left-on-rectangle",
                    "sort": 1000,
                    "group": "__logout__",
                    "post_to_url": False,
                    "visible": True,
                }
            )

        items.sort(key=lambda i: (i.get("sort") or 0, i.get("label") or ""))
        parts: list[str] = []
        last_group: Any = object()
        for item in items:
            group = item.get("group")
            if last_group is not object() and group != last_group:
                parts.append('<div class="or-user-menu-divider" role="separator"></div>')
            last_group = group
            icon = render_icon(item["icon"]) if item.get("icon") else ""
            label = e(str(item.get("label") or ""))
            url = e(str(item.get("url") or "#"))
            if item.get("post_to_url"):
                parts.append(
                    f'<form class="or-user-menu-form" method="post" action="{url}">'
                    f'<button type="submit" class="or-user-menu-item">{icon}<span>{label}</span></button>'
                    f"</form>"
                )
            else:
                parts.append(
                    f'<a class="or-user-menu-item" href="{url}">{icon}<span>{label}</span></a>'
                )
        return "".join(parts)

    def _render_user_menu(self, *, user: Any = None, placement: str = "topbar") -> str:
        if not self._user_menu_enabled or user is None:
            return ""
        name = str(getattr(user, "name", None) or getattr(user, "email", None) or "User")
        initials = "".join(p[:1] for p in name.split()[:2]).upper() or "U"
        menu_html = self._render_user_menu_items_html(user=user)
        return (
            f'<div class="or-user-menu or-user-menu-{e(placement)}" '
            f'x-data="{{ open: false }}" @click.outside="open = false">'
            '<button type="button" class="or-user-menu-btn" @click="open = !open">'
            f'<span class="or-avatar" aria-hidden="true">{e(initials)}</span>'
            f'<span class="or-user-name">{e(name)}</span>'
            f"{render_icon('heroicon-o-chevron-down', size=14, css_class='or-icon or-user-chevron')}"
            f"</button>"
            '<div class="or-user-menu-panel" x-show="open" x-cloak role="menu">'
            f"{menu_html}"
            "</div></div>"
        )

    def _render_topbar_end(self, *, user: Any = None) -> str:
        parts: list[str] = []
        scope = self.id
        parts.append(render_hook("panels::global-search.before", scope=scope, user=user))
        if self.has_global_search():
            parts.append(
                render_global_search_input(
                    debounce_ms=self._global_search_debounce_ms,
                    endpoint=self.global_search_url(),
                    placeholder=self._global_search_placeholder,
                )
            )
        else:
            parts.append('<div class="or-global-search-slot" data-orbit-global-search></div>')
        parts.append(render_hook("panels::global-search.after", scope=scope, user=user))

        tenancy = self._tenancy
        if tenancy is not None and tenancy.is_enabled():
            switcher = tenancy.render_switcher(user=user, panel=self)
            if switcher:
                parts.append(switcher)

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

        if (
            self._notifications_enabled
            and self._database_notifications_enabled
            and self._database_notifications_position == "topbar"
        ):
            parts.append(self._render_database_notifications_trigger(user=user))

        parts.append(render_hook("panels::user-menu.before", scope=scope, user=user))
        if (
            self._user_menu_enabled
            and user is not None
            and self._user_menu_position == "topbar"
            and self._topbar_enabled
        ):
            parts.append(self._render_user_menu(user=user, placement="topbar"))
        parts.append(render_hook("panels::user-menu.after", scope=scope, user=user))
        return "".join(parts)

    def _interval_ms(self, raw: str | int | None) -> int | None:
        if raw is None:
            return None
        if isinstance(raw, int):
            return raw if raw > 0 else None
        text = str(raw).strip().lower()
        if not text or text in {"null", "none", "false"}:
            return None
        if text.endswith("ms"):
            try:
                return int(text[:-2])
            except ValueError:
                return None
        if text.endswith("s"):
            try:
                return int(float(text[:-1]) * 1000)
            except ValueError:
                return None
        try:
            return int(text)
        except ValueError:
            return None

    def _polling_ms(self) -> int | None:
        return self._interval_ms(self._database_notifications_polling)

    def _live_polling_ms(self) -> int | None:
        return self._interval_ms(self._live_broadcasts_polling)

    def _render_database_notifications_trigger(self, user: Any = None) -> str:
        import json
        from uuid import uuid4

        from almasix.orbit.panels.notification_routes import (
            panel_notifications_url,
            sort_notifications_latest_first,
        )

        notes = list(self._database_notifications)
        store = self._database_notification_store
        if store is not None:
            try:
                notes = [row.to_dict() for row in store.get_for_user(user)] or notes
            except Exception:
                pass
        normalized: list[dict[str, Any]] = []
        for note in notes:
            row = dict(note)
            row.setdefault("id", str(uuid4()))
            row.setdefault("read", False)
            row.setdefault("title", "Notification")
            row.setdefault("body", "")
            row.setdefault("created_at", "")
            normalized.append(row)
        normalized = sort_notifications_latest_first(normalized)
        unread = sum(1 for n in normalized if not n.get("read"))
        polling = self._polling_ms()
        polling_attr = f' data-polling="{polling}"' if polling else ' data-polling=""'
        url_attr = f' data-orbit-notifications-url="{e(panel_notifications_url(self))}"'
        payload = e(json.dumps(normalized))
        bell = render_icon("heroicon-o-bell", size=_TOPBAR_ICON)
        badge = (
            f'<span class="or-notify-badge" x-text="unreadCount" '
            f'x-show="unreadCount > 0" x-cloak>{unread}</span>'
            if normalized
            else '<span class="or-notify-badge" x-text="unreadCount" x-show="unreadCount > 0" x-cloak></span>'
        )
        return (
            f'<div class="or-notify" x-data="orbitDatabaseNotifications" '
            f'data-notifications="{payload}"{polling_attr}{url_attr} '
            f'@keydown.escape.window="onEscape()" '
            f'@click.outside="if (!deckOpen && !detailOpen) open = false">'
            '<button type="button" class="or-icon-btn or-notify-btn" @click="toggle()" '
            f'aria-label="Notifications" aria-haspopup="true">{bell}{badge}</button>'
            # Compact dropdown — unread only
            '<div class="or-notify-panel" x-show="open" x-cloak role="menu">'
            '<div class="or-notify-header">'
            '<span class="or-notify-heading">Notifications</span>'
            '<button type="button" class="or-notify-mark-all" @click="markAllRead()" '
            'x-show="unreadCount > 0">Mark all as read</button>'
            "</div>"
            '<ul class="or-notify-list">'
            '<template x-for="n in unreadList" :key="n.id">'
            '<li class="or-notify-item is-unread" @click="openDetail(n)">'
            '<div class="or-notify-item-top">'
            '<span class="or-notify-title" x-text="n.title || \'Notification\'"></span>'
            '<time class="or-notify-time" x-text="formatTime(n.created_at)" '
            'x-show="n.created_at"></time>'
            "</div>"
            '<span class="or-notify-body" x-text="n.body || \'\'" x-show="n.body"></span>'
            "</li>"
            "</template>"
            '<li class="or-notify-empty" x-show="unreadList.length === 0">'
            "No unread notifications</li>"
            "</ul>"
            '<div class="or-notify-footer">'
            '<button type="button" class="or-notify-view-all" @click="openDeck()">'
            "View all</button>"
            "</div>"
            "</div>"
            # Right-side notifications deck (full history + infinite scroll)
            '<div class="or-notify-deck-backdrop" x-show="deckOpen" x-cloak '
            '@click="closeDeck()"></div>'
            '<aside class="or-notify-deck" x-show="deckOpen" x-cloak '
            'role="dialog" aria-modal="true" aria-label="Notification history">'
            '<div class="or-notify-deck-header">'
            '<h2 class="or-notify-deck-title">All notifications</h2>'
            '<div class="or-notify-deck-actions">'
            '<button type="button" class="or-notify-mark-all" @click="markAllRead()" '
            'x-show="unreadCount > 0">Mark all as read</button>'
            '<button type="button" class="or-notify-deck-close" @click="closeDeck()" '
            'aria-label="Close">&times;</button>'
            "</div></div>"
            '<ul class="or-notify-deck-list" x-ref="deckList" @scroll="onDeckScroll($event)">'
            '<template x-for="n in deckList" :key="n.id">'
            '<li class="or-notify-deck-item" :class="{ \'is-unread\': !n.read }" '
            '@click="openDetail(n)">'
            '<div class="or-notify-item-top">'
            '<span class="or-notify-title" x-text="n.title || \'Notification\'"></span>'
            '<time class="or-notify-time" x-text="formatTime(n.created_at)" '
            'x-show="n.created_at"></time>'
            "</div>"
            '<span class="or-notify-body" x-text="n.body || \'\'" x-show="n.body"></span>'
            "</li>"
            "</template>"
            '<li class="or-notify-empty" x-show="notifications.length === 0">'
            "No notifications yet</li>"
            '<li class="or-notify-deck-more" x-show="deckHasMore" x-cloak>'
            '<button type="button" class="or-notify-view-all" @click="loadMoreDeck()">'
            "Load more</button>"
            "</li>"
            '<li class="or-notify-deck-end" '
            'x-show="notifications.length > 0 && !deckHasMore" x-cloak>'
            "End of history</li>"
            "</ul>"
            "</aside>"
            # Detail modal
            '<div class="or-notify-detail-backdrop" x-show="detailOpen" x-cloak '
            '@click="closeDetail()"></div>'
            '<div class="or-notify-detail" x-show="detailOpen" x-cloak '
            'role="dialog" aria-modal="true" :aria-labelledby="detailTitleId">'
            '<button type="button" class="or-modal-close" @click="closeDetail()" '
            'aria-label="Close">&times;</button>'
            '<p class="or-notify-detail-meta">'
            '<span class="or-notify-detail-status" x-text="selected?.status || \'info\'" '
            'x-show="selected"></span>'
            '<time class="or-notify-time" x-text="formatTime(selected?.created_at)" '
            'x-show="selected?.created_at"></time>'
            "</p>"
            '<h2 class="or-modal-title" :id="detailTitleId" '
            'x-text="selected?.title || \'Notification\'"></h2>'
            '<p class="or-modal-body" x-text="selected?.body || \'\'" '
            'x-show="selected?.body"></p>'
            '<div class="or-notify-detail-actions">'
            '<button type="button" class="or-btn or-btn-gray" @click="closeDetail()">'
            "Close</button>"
            '<button type="button" class="or-btn or-btn-gray" '
            '@click="markUnread(selected.id)" '
            'x-show="selected && selected.read">Mark unread</button>'
            "</div>"
            "</div>"
            "</div>"
        )

    def _render_toast_host(self) -> str:
        if not self._notifications_enabled:
            return ""
        try:
            from almasix.orbit.notifications import get_notifier

            html = get_notifier().render_toast_host(include_flash=True)
            if self._live_broadcasts_enabled:
                from almasix.orbit.panels.notification_routes import panel_live_url

                polling = self._live_polling_ms() or 0
                return (
                    f'<div class="or-live-notifier" x-data="orbitLiveNotifications" '
                    f'data-orbit-live-url="{e(panel_live_url(self))}" '
                    f'data-polling="{polling}">{html}</div>'
                )
            return html
        except ImportError:  # pragma: no cover
            from almasix.orbit.notifications.alignment import Notifications

            classes = Notifications.host_classes()
            return (
                f'<div class="{classes}" x-data="orbitNotifications" '
                f'role="region" aria-label="Notifications"></div>'
            )

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
            "tenancy": self._tenancy.to_dict() if self._tenancy is not None else None,
            "mfa_providers": [
                p.get_id() if hasattr(p, "get_id") else type(p).__name__ for p in self._mfa_providers
            ],
            "spa": self._spa_enabled,
        }


def _action_modal_html() -> str:
    return (
        '  <div class="or-action-modal-host" x-data="orbitActionModal" x-cloak\n'
        '       @keydown.escape.window="if (open && closeOnEscape) close()">\n'
        '    <div class="or-modal-backdrop" x-show="open" '
        '@click="if (closeOnClickAway) close()"></div>\n'
        '    <div class="or-modal" x-show="open"\n'
        '         :role="confirmOnly ? \'alertdialog\' : \'dialog\'" aria-modal="true"\n'
        '         :class="{\n'
        "           'or-modal-slide': slideOver,\n"
        "           'or-modal-slide-left': slideOver && slideOverPosition === 'left',\n"
        "           'or-modal-sticky-header': stickyHeader,\n"
        "           'or-modal-sticky-footer': stickyFooter,\n"
        "           'or-modal-align-center': modalAlignment === 'center',\n"
        "           ['or-modal-' + modalWidth]: true\n"
        '         }">\n'
        '      <button type="button" class="or-modal-close" x-show="showCloseButton"\n'
        '              @click="close()" aria-label="Close">&times;</button>\n'
        '      <div class="or-modal-header" :class="{ \'or-modal-header-sticky\': stickyHeader }">\n'
        '        <div class="or-modal-icon" x-show="modalIcon"\n'
        '             :data-color="modalIconColor || \'primary\'" x-html="modalIconHtml"></div>\n'
        '        <h2 class="or-modal-title" x-text="heading"></h2>\n'
        "      </div>\n"
        '      <p class="or-modal-body" x-text="description" x-show="description"></p>\n'
        '      <form class="or-modal-form" x-show="hasForm" x-ref="actionForm" '
        '@submit.prevent="confirm()">\n'
        '        <div class="or-modal-form-fields" x-html="formHtml"></div>\n'
        "      </form>\n"
        '      <div class="or-modal-actions" '
        ':class="{ \'or-modal-actions-sticky\': stickyFooter }">\n'
        '        <button type="button" class="or-btn or-btn-gray" @click="close()"\n'
        '                x-text="cancelLabel"></button>\n'
        '        <button type="button" class="or-btn or-btn-primary" @click="confirm()"\n'
        '                x-text="submitLabel"></button>\n'
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

    def get_by_path(self, path: str | None) -> Panel | None:
        """Find a registered panel whose path matches ``path``."""
        cleaned = (path or "").strip() or "/"
        if not cleaned.startswith("/"):
            cleaned = f"/{cleaned}"
        if cleaned != "/":
            cleaned = cleaned.rstrip("/")
        for panel in self.all():
            candidate = panel.get_path() or "/"
            if candidate != "/":
                candidate = candidate.rstrip("/")
            if candidate == cleaned:
                return panel
        return None

    def get_by_domain(self, domain: str | None) -> Panel | None:
        """Find a registered panel bound to ``domain`` (host, no port)."""
        host = str(domain or "").split("/")[0].split(":")[0].strip().lower()
        if not host:
            return None
        for panel in self.all():
            bound = (panel.get_domain() or "").split(":")[0].strip().lower()
            if bound and bound == host:
                return panel
        return None
