"""Register the Orbit admin panel."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.navigation import NavigationGroup
from almasix.orbit.panels.users import PanelNotification, UserMenuItem
from almasix.providers import ServiceProvider
from app.orbit.resources.author_resource import AuthorResource
from app.orbit.resources.post_resource import PostResource
from app.orbit.resources.settings_resource import SettingsResource


class OrbitPanelProvider(ServiceProvider):
    def boot(self) -> None:
        panel = (
            Panel.make("app")
            .path("/")
            .brand_name("Obit")
            .brand_name_font_size("2.3rem")
            .brand_logo("images/almasix-light.svg")
            .brand_logo_dark("images/almasix-dark.svg")
            .login()
            .signup()
            .navigation_group(
                NavigationGroup.make("Content")
                .icon("heroicon-o-document-text")
                .sort(0)
            )
            .navigation_group(
                NavigationGroup.make("System")
                .icon("heroicon-o-cog-6-tooth")
                .sort(10)
            )
            .resources([PostResource, AuthorResource, SettingsResource])
        )
        self.app.make(PanelRegistry).register(panel)
