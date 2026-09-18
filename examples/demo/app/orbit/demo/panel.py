"""Orbit panel: demo (music catalog)."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.navigation import NavigationGroup
from app.orbit.demo.resources.album_resource import AlbumResource
from app.orbit.demo.resources.artist_resource import ArtistResource


def register_demo_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("demo")
        .path("/")
        .brand_name("Orbit Demo")
        .brand_logo("images/almasix-light.svg")
        .brand_logo_dark("images/almasix-dark.svg")
        .login()
        .navigation_group(
            NavigationGroup.make("Catalog")
            .icon("heroicon-o-musical-note")
            .sort(0)
        )
        .resources([ArtistResource, AlbumResource])
        .discover_panel_dirs()
    )
    registry.register(panel)
    return panel
