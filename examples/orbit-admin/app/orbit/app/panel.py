"""Orbit panel: app (Panel Configuration showcase)."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.mfa import AppAuthentication, EmailAuthentication
from almasix.orbit.panels.navigation import NavigationGroup, NavigationItem, NavigationSubgroup
from almasix.orbit.panels.tenancy import Tenancy, Tenant
from almasix.orbit.panels.users import PanelNotification, UserMenuItem

from app.orbit.app.clusters.settings_hub_cluster import SettingsHubCluster
from app.orbit.app.pages.nav_account_pages import NavAccountPage, NavPreferencesPage
from app.orbit.app.plugins import BrandingPlugin
from app.orbit.app.resources.actions_overview_resource import ActionsOverviewResource
from app.orbit.app.resources.author_resource import AuthorResource
from app.orbit.app.resources.columns_overview_resource import ColumnsOverviewResource
from app.orbit.app.resources.editable_columns_resource import EditableColumnsResource
from app.orbit.app.resources.generated_post_resource import GeneratedPostResource
from app.orbit.app.resources.grouped_posts_resource import GroupedPostsResource
from app.orbit.app.resources.infolists_overview_resource import InfolistsOverviewResource
from app.orbit.app.resources.kitchen_sink_resource import KitchenSinkResource
from app.orbit.app.resources.layout_columns_resource import LayoutColumnsResource
from app.orbit.app.resources.media_columns_resource import MediaColumnsResource
from app.orbit.app.resources.modal_tasks_resource import ModalTasksResource
from app.orbit.app.resources.nav_colors_resource import NavColorsResource
from app.orbit.app.resources.nav_fonts_resource import NavFontsResource
from app.orbit.app.resources.navigation_overview_resource import NavigationOverviewResource
from app.orbit.app.resources.notifications_overview_resource import NotificationsOverviewResource
from app.orbit.app.resources.post_resource import PostResource
from app.orbit.app.resources.settings_resource import SettingsResource
from app.orbit.app.resources.tables_overview_resource import TablesOverviewResource
from app.orbit.app.resources.tenancy_overview_resource import TenancyOverviewResource
from app.orbit.app.resources.text_columns_resource import TextColumnsResource
from app.orbit.app.widgets import (
    OverviewStats,
    RecentPostsTable,
    RevenueApexChart,
    SignupsChart,
    WelcomeWidget,
)


def _demo_tenancy() -> Tenancy:
    """Two fake teams + scoping that only filters rows with ``tenant_id``."""
    acme = Tenant(1, "Acme Corp", slug="acme")
    beta = Tenant(2, "Beta Labs", slug="beta")
    return (
        Tenancy()
        .tenants([acme, beta])
        .current(acme)
        .registration(True)
        .profile(True)
        .scope_using(
            lambda rows, tenant: [
                r
                for r in rows
                if not isinstance(r, dict)
                or "tenant_id" not in r
                or r.get("tenant_id") == tenant.id
            ]
        )
        .associate_using(
            lambda record, tenant: (
                {**record, "tenant_id": tenant.id}
                if isinstance(record, dict)
                else record
            )
        )
    )


def register_app_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("app")
        .default()
        .path("/")
        .brand_name("Orbit Admin")
        .brand_logo("images/almasix-light.svg")
        .brand_logo_dark("images/almasix-dark.svg")
        .brand_logo_height("2.25rem")
        .favicon("images/favicon.svg")
        .font("Outfit")
        .primary("#f1511b")
        .colors(danger="#ef4444", success="#22c55e", warning="#f59e0b", info="#3b82f6")
        .content_max_width("screen-2xl")
        .simple_page_max_content_width("md")
        .dark_mode()
        .theme_switcher()
        .default_theme_mode("system")
        .sidebar_collapsible()
        .login()
        .signup()
        .multi_factor_authentication(
            AppAuthentication(brand_name="Orbit Admin"),
            EmailAuthentication(),
        )
        .auth_guard("web")
        .middleware(["web"], replace=True)
        .tenant(_demo_tenancy())
        .tenant_registration(True)
        .tenant_profile(True)
        .plugin(BrandingPlugin())
        .boot_using(lambda p: None)
        .render_hook(
            "panels::head.end",
            lambda **_ctx: '  <meta name="orbit-panel-config" content="app" />\n',
        )
        .navigation_group(
            NavigationGroup.make("Content")
            .icon("heroicon-o-document-text")
            .sort(0)
        )
        .navigation_group(
            NavigationGroup.make("Columns")
            .icon("heroicon-o-view-columns")
            .sort(5)
        )
        .navigation_group(
            NavigationGroup.make("Infolists")
            .icon("heroicon-o-queue-list")
            .sort(6)
        )
        .navigation_group(
            NavigationGroup.make("Actions")
            .icon("heroicon-o-check")
            .sort(7)
        )
        .navigation_group(
            NavigationGroup.make("Navigation")
            .icon("heroicon-o-bars-3")
            .sort(8)
        )
        .navigation_group(
            NavigationGroup.make("Notifications")
            .icon("heroicon-o-bell")
            .sort(9)
        )
        .navigation_group(
            NavigationGroup.make("Tenancy")
            .icon("heroicon-o-building-office-2")
            .sort(10)
        )
        .navigation_group(
            NavigationGroup.make("Demos")
            .icon("heroicon-o-beaker")
            .sort(20)
        )
        .navigation_group(
            NavigationGroup.make("System")
            .icon("heroicon-o-cog-6-tooth")
            .sort(30)
        )
        .navigation_subgroup(
            NavigationSubgroup.make("Samples")
            .parent("Navigation")
            .icon("heroicon-o-squares-2x2")
            .sort(0)
        )
        .navigation_items(
            [
                NavigationItem.make("orbit-docs")
                .label("Orbit docs")
                .url("https://orbit.almasix.com")
                .icon("heroicon-o-book-open")
                .group("Navigation")
                .sort(50)
                .open_url_in_new_tab(),
            ]
        )
        .user_menu_items(
            [
                UserMenuItem.make("docs")
                .label("Documentation")
                .url("https://orbit.almasix.com")
                .icon("heroicon-o-book-open")
                .group("Help")
                .sort(10),
                UserMenuItem.make("status")
                .label("System status")
                .url("https://status.almasix.com")
                .icon("heroicon-o-signal")
                .group("Help")
                .sort(20),
            ]
        )
        .clusters([SettingsHubCluster])
        .pages([NavAccountPage, NavPreferencesPage])
        .database_notifications(
            [
                PanelNotification.make("Welcome to Orbit")
                .body("Database notifications are enabled on this panel.")
                .status("success")
                .id("seed-welcome")
                .created_at("2026-09-23T03:00:00Z"),
                PanelNotification.make("Deploy finished")
                .body("v1.4.2 is live on production.")
                .status("info")
                .id("seed-deploy")
                .created_at("2026-09-23T05:45:00Z"),
                PanelNotification.make("Backup complete")
                .body("Nightly backup finished without errors.")
                .status("success")
                .read()
                .id("seed-backup")
                .created_at("2026-09-22T22:10:00Z"),
            ]
        )
        .database_notifications_polling("30s")
        .sqlite_notifications("orbit-notifications.sqlite")
        .live_broadcasts(polling="2s")
        .tenant_billing(True)
        .spa()
        .widgets(
            [
                WelcomeWidget,
                OverviewStats,
                SignupsChart,
                RevenueApexChart,
                RecentPostsTable,
            ]
        )
        .resources(
            [
                TablesOverviewResource,
                ColumnsOverviewResource,
                InfolistsOverviewResource,
                ActionsOverviewResource,
                NavigationOverviewResource,
                NotificationsOverviewResource,
                TenancyOverviewResource,
                NavColorsResource,
                NavFontsResource,
                PostResource,
                AuthorResource,
                SettingsResource,
                TextColumnsResource,
                MediaColumnsResource,
                EditableColumnsResource,
                LayoutColumnsResource,
                GroupedPostsResource,
                ModalTasksResource,
                KitchenSinkResource,
                GeneratedPostResource,
            ]
        )
        .discover_panel_dirs()
    )
    registry.register(panel)
    return panel
