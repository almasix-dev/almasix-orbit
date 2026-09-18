"""Register the Orbit music catalog panel."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.navigation import NavigationGroup
from almasix.providers import ServiceProvider
from app.orbit.resources.album_resource import AlbumResource
from app.orbit.resources.artist_resource import ArtistResource


class OrbitPanelProvider(ServiceProvider):
    def boot(self) -> None:
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
        )
        self.app.make(PanelRegistry).register(panel)
