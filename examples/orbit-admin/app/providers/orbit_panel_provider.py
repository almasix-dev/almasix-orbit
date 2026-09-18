"""Register the Orbit admin panel."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.navigation import NavigationGroup
from almasix.providers import ServiceProvider
from app.orbit.resources.author_resource import AuthorResource
from app.orbit.resources.editable_columns_resource import EditableColumnsResource
from app.orbit.resources.grouped_posts_resource import GroupedPostsResource
from app.orbit.resources.kitchen_sink_resource import KitchenSinkResource
from app.orbit.resources.layout_columns_resource import LayoutColumnsResource
from app.orbit.resources.media_columns_resource import MediaColumnsResource
from app.orbit.resources.modal_tasks_resource import ModalTasksResource
from app.orbit.resources.post_resource import PostResource
from app.orbit.resources.settings_resource import SettingsResource
from app.orbit.resources.text_columns_resource import TextColumnsResource


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
                NavigationGroup.make("Columns")
                .icon("heroicon-o-view-columns")
                .sort(5)
            )
            .navigation_group(
                NavigationGroup.make("Demos")
                .icon("heroicon-o-beaker")
                .sort(8)
            )
            .navigation_group(
                NavigationGroup.make("System")
                .icon("heroicon-o-cog-6-tooth")
                .sort(10)
            )
            .resources(
                [
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
                ]
            )
        )
        self.app.make(PanelRegistry).register(panel)
