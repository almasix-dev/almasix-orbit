"""Register the Orbit admin panel (Panel Configuration showcase)."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.navigation import NavigationGroup
from almasix.providers import ServiceProvider
from app.orbit.plugins import BrandingPlugin
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
        registry = self.app.make(PanelRegistry)

        panel = (
            Panel.make("app")
            .default()
            .path("/")
            .brand_name("Orbit Admin")
            .brand_name_font_size("1.35rem")
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
            .auth_guard("web")
            .middleware(["web"], replace=True)
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
            # Discovery still merges any extra classes under these packages.
            .discover_pages("app.orbit.pages")
            .discover_widgets("app.orbit.widgets")
        )
        registry.register(panel)

        # Second panel — minimal guest “docs” shell for multi-panel demos.
        docs = (
            Panel.make("docs")
            .path("docs")
            .brand_name("Orbit Docs")
            .font("Outfit")
            .primary("#3b82f6")
            .login(False)
            .dashboard(False)
            .dark_mode()
            .theme_switcher(False)
            .default_theme_mode("light")
            .breadcrumbs_enabled(False)
        )
        registry.register(docs)
