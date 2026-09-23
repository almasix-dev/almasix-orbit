"""Orbit panel: demo (Orbit Records music catalog)."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.navigation import NavigationGroup
from almasix.orbit.panels.users import PanelNotification

from app.orbit.demo.auth.demo_login import DemoLogin
from app.orbit.demo.pages.catalog_insights import CatalogInsightsPage
from app.orbit.demo.resources.album_resource import AlbumResource
from app.orbit.demo.resources.artist_resource import ArtistResource
from app.orbit.demo.resources.track_resource import TrackResource
from app.orbit.demo.widgets import (
    CatalogStats,
    RecentAlbumsTable,
    ReleasesChart,
    StreamsChart,
    WelcomeWidget,
)


def register_demo_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("demo")
        .path("/")
        .brand_name("Orbit Demo")
        .brand_logo("images/almasix-light.svg")
        .brand_logo_dark("images/almasix-dark.svg")
        .brand_logo_height("2.25rem")
        .favicon("images/favicon.svg")
        .font("Outfit")
        .primary("#F1511B")
        .colors(danger="#ef4444", success="#22c55e", warning="#f59e0b", info="#0ea5e9")
        .dark_mode()
        .theme_switcher()
        .default_theme_mode("system")
        .sidebar_collapsible(False)
        .apps_navigation()
        .login(DemoLogin)
        .navigation_group(
            NavigationGroup.make("Catalog")
            .icon("heroicon-o-musical-note")
            .sort(0)
        )
        .resources([ArtistResource, AlbumResource, TrackResource])
        .pages([CatalogInsightsPage])
        .widgets(
            [
                WelcomeWidget,
                CatalogStats,
                ReleasesChart,
                StreamsChart,
                RecentAlbumsTable,
            ]
        )
        .database_notifications(
            [
                PanelNotification.make("Welcome to Orbit Records")
                .body("Explore Artists, Albums, Tracks, and Insights.")
                .status("success")
                .id("seed-welcome")
                .created_at("2026-09-23T04:30:00Z"),
                PanelNotification.make("New release window")
                .body("Draft albums are ready for review in the catalog.")
                .status("info")
                .id("seed-release")
                .created_at("2026-09-23T06:15:00Z"),
            ]
        )
        .database_notifications_polling("30s")
        .sqlite_notifications("orbit-notifications.sqlite")
        .spa()
        .discover_panel_dirs()
    )
    registry.register(panel)
    return panel
