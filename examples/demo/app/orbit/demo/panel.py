"""Orbit panel: demo (Orbit Records music catalog)."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.navigation import NavigationGroup

from app.orbit.demo.auth.demo_login import DemoLogin
from app.orbit.demo.pages.catalog_insights import CatalogInsightsPage
from app.orbit.demo.resources.album_resource import AlbumResource
from app.orbit.demo.resources.artist_resource import ArtistResource
from app.orbit.demo.resources.track_resource import TrackResource
from app.orbit.demo.widgets import (
    CatalogStats,
    FormatsChart,
    PlaysTrendChart,
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
                PlaysTrendChart,
                FormatsChart,
                StreamsChart,
                RecentAlbumsTable,
            ]
        )
        # Framework ``notifications`` table (smith notifications:table). Seeds
        # for demo@orbit.test come from NotificationSeeder; catalog edits notify live.
        .database_notifications(True)
        .database_notifications_polling("30s")
        .database_notifications_using_almasix()
        .spa()
        .discover_panel_dirs()
    )
    registry.register(panel)
    return panel
