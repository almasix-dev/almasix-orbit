"""Tests for almasix.orbit.panels."""

from __future__ import annotations

import sys
import types
from typing import Any

from almasix.orbit.forms.components import TextInput
from almasix.orbit.forms.form import Form
from almasix.orbit.infolists.infolist import Infolist
from almasix.orbit.panels.commands import MakeOrbitResourceCommand
from almasix.orbit.panels.page import Page
from almasix.orbit.panels.panel import Panel, PanelRegistry
from almasix.orbit.panels.relation_manager import RelationManager
from almasix.orbit.panels.resource import Resource
from almasix.orbit.tables.columns import TextColumn
from almasix.orbit.tables.table import Table
from almasix.orbit.testing import LiveResource


class User:
    def __init__(
        self,
        *,
        permissions: set[str] | list[str] | None = None,
        is_admin: bool = False,
    ) -> None:
        self.permissions = set(permissions or [])
        self.is_admin = is_admin

    def can(self, ability: str, record: Any = None) -> bool:
        if self.is_admin or "*" in self.permissions:
            return True
        return ability in self.permissions


class Post:
    id = 1
    title = "Hello"


class PostResource(Resource):
    model = Post
    navigation_label = "Posts"
    navigation_group = "Content"
    navigation_sort = 1
    permission_prefix = "posts"
    records_mutable = True

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title").required()])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title").searchable()])

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist


class DashboardPage(Page):
    title = "Dashboard"
    navigation_sort = 0
    permission = "dashboard.view"


class CommentsRelationManager(RelationManager):
    relationship = "comments"
    title = "Comments"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("body")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("body")])


def test_panel_registry_and_shell() -> None:
    panel = (
        Panel.make("admin")
        .path("orbit")
        .brand_name("Almasix Orbit")
        .brand_logo("/logo.svg")
        .font("Outfit")
        .colors(primary="#f1511b", danger="#ef4444")
        .resources([PostResource])
        .pages([DashboardPage])
        .widgets([])
        .middleware(["auth"], replace=True)
        .login()
        .auth_guard("web")
        .dark_mode(False)
        .sidebar_collapsible()
        .discover_resources("app/resources")
        .discover_pages("app/pages")
        .discover_widgets("app/widgets")
        .plugin(lambda p: p)
    )
    assert panel.get_path() == "/orbit"
    assert PostResource in panel.get_resources()
    assert DashboardPage in panel.get_pages()
    assert panel.get_middleware() == ["auth"]
    nav = panel.navigation_items()
    assert any(i["label"] == "Posts" for i in nav)
    assert any(i["label"] == "Dashboard" for i in nav)
    shell = panel.render_shell("<p>Hi</p>", user=User(is_admin=True))
    assert "or-app" in shell and "Almasix Orbit" in shell and "Hi" in shell
    assert 'src="/logo.svg"' in shell and "or-brand-name" in shell
    logo_only = (
        Panel.make("branded")
        .brand_name("Acme")
        .brand_logo("/logo.svg", dark="/logo-dark.svg")
        .brand_logo_only()
    )
    brand = logo_only._brand_html()
    assert "or-brand-logo-only" in brand
    assert "or-brand-name" not in brand
    assert 'alt="Acme"' in brand

    from almasix.orbit.support.urls import resolve_public_url

    assert resolve_public_url("https://cdn.example.com/a.svg") == "https://cdn.example.com/a.svg"
    assert resolve_public_url("//cdn.example.com/a.svg") == "//cdn.example.com/a.svg"
    resolved = resolve_public_url("images/logo.svg")
    assert resolved is not None and resolved.endswith("/images/logo.svg")

    d = panel.to_dict()
    assert d["id"] == "admin" and "PostResource" in d["resources"]

    registry = PanelRegistry()
    registry.register(panel)
    assert registry.get("admin") is panel
    assert registry.all() == [panel]


def test_resource_permissions_and_crud_config() -> None:
    assert PostResource.get_slug() == "posts"
    assert PostResource.get_navigation_label() == "Posts"
    assert PostResource.get_model() is Post
    assert PostResource.get_permission_prefix() == "posts"
    admin = User(is_admin=True)
    assert PostResource.can_view_any(admin)
    assert PostResource.can_view(admin, Post())
    assert PostResource.can_create(admin)
    assert PostResource.can_update(admin, Post())
    assert PostResource.can_delete(admin, Post())
    limited = User(permissions={"posts.view_any"})
    assert PostResource.can_view_any(limited)
    assert not PostResource.can_create(limited)
    assert not PostResource.can_view_any(None)
    assert not PostResource.can_view_any(User(permissions=set()))

    form = PostResource.get_form()
    assert form.get_components()[0].get_name() == "title"
    table = PostResource.get_table()
    assert table._columns[0].get_name() == "title"
    assert table._actions and table._bulk_actions and table._header_actions
    assert "index" in PostResource.get_pages()
    assert PostResource.get_relations() == []
    assert PostResource.get_infolist().get_name() == "infolist"

    class NoModel(Resource):
        pass

    try:
        NoModel.get_model()
        raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass

    class CustomSlug(Resource):
        slug = "things"

    assert CustomSlug.get_slug() == "things"

    class AuthorResource(Resource):
        model = type("Author", (), {})

    assert AuthorResource.get_slug() == "authors"

    class SettingsResource(Resource):
        model = type("Settings", (), {})

    assert SettingsResource.get_slug() == "settings"


def test_panel_breadcrumbs() -> None:
    panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .resources([PostResource])
        .pages([DashboardPage])
    )
    home = panel.breadcrumbs("/admin")
    assert len(home) == 1 and home[0]["label"] == "Orbit" and home[0]["url"] is None

    index = panel.breadcrumbs("/admin/posts")
    assert [c["label"] for c in index] == ["Orbit", "Posts"]
    assert index[0]["url"] == "/admin"
    assert index[1]["url"] is None

    create = panel.breadcrumbs("/admin/posts/create")
    assert [c["label"] for c in create] == ["Orbit", "Posts", "Create"]
    assert create[1]["url"] == "/admin/posts"
    assert create[2]["url"] is None

    edit = panel.breadcrumbs("/admin/posts/1/edit")
    assert [c["label"] for c in edit] == ["Orbit", "Posts", "Edit"]

    page = panel.breadcrumbs("/admin/dashboard")
    assert [c["label"] for c in page] == ["Orbit", "Dashboard"]

    shell = panel.render_shell("<p>x</p>", user=User(is_admin=True), active_path="/admin/posts/create")
    assert 'aria-label="Breadcrumb"' in shell
    assert "or-breadcrumbs-link" in shell
    assert "Create" in shell

    user = User(permissions={"dashboard.view"})
    assert DashboardPage.get_slug() == "dashboard"
    assert DashboardPage.get_title() == "Dashboard"
    assert DashboardPage.can_access(user)
    assert not DashboardPage.can_access(User(permissions=set()))
    assert "or-page-title" in DashboardPage.render()

    class OpenPage(Page):
        pass

    assert OpenPage.can_access(User(is_admin=True))
    assert not OpenPage.can_access(None)

    class SluggedPage(Page):
        slug = "custom-slug"

    assert SluggedPage.get_slug() == "custom-slug"

    rm = CommentsRelationManager
    assert rm.get_title() == "Comments"
    assert rm.get_form().get_components()[0].get_name() == "body"
    assert rm.get_table()._columns[0].get_name() == "body"
    assert rm.can_view_for_record(user, Post())
    assert not rm.can_view_for_record(None, Post())

    class BareRelation(RelationManager):
        relationship = "items"

    assert BareRelation.get_form().get_name() == "items_form"
    assert BareRelation.get_table().get_name() == "items_table"
    assert BareRelation.get_title() == "Items"

    live = LiveResource(PostResource)
    live.assert_form_has_field("title")
    live.assert_table_has_column("title")
    errors = live.fill_form({})
    assert "title" in errors

    cmd = MakeOrbitResourceCommand()
    assert cmd.handle(name="Post") == 0
    assert cmd.handle("Post") == 0
    assert cmd.handle() == 2


def test_resource_defaults_and_preset_actions() -> None:
    class EmptyResource(Resource):
        model = Post

        @classmethod
        def table(cls, table: Table) -> Table:
            from almasix.orbit.actions.action import CreateAction, DeleteAction

            return (
                table.columns([TextColumn.make("title")])
                .actions([DeleteAction.make()])
                .bulk_actions([DeleteAction.make("bulk")])
                .header_actions([CreateAction.make()])
            )

    t = EmptyResource.get_table()
    assert len(t._actions) == 1
    assert EmptyResource.form(Form.make("f")).get_name() == "f"
    assert EmptyResource.infolist(Infolist.make("i")).get_name() == "i"
    assert EmptyResource.table(Table.make("t")).get_name() == "t"


def test_can_with_alternate_user_apis() -> None:
    from almasix.orbit.panels.resource import _can

    class HasPerm:
        def has_permission(self, ability: str) -> bool:
            return ability == "x.view"

    class HasPermissionTo:
        def hasPermissionTo(self, ability: str, record: Any = None) -> bool:
            return ability.startswith("y")

    class Super:
        is_super_admin = True

    class StarPerms:
        permissions = ["*"]

    class StrictCan:
        def can(self, ability: str) -> bool:
            return ability == "only"

    assert _can(HasPerm(), "x.view")
    assert not _can(HasPerm(), "x.edit")
    assert _can(HasPermissionTo(), "y.view", record=1)
    assert _can(Super(), "anything")
    assert _can(StarPerms(), "z")
    assert not _can(object(), "z")
    # TypeError path: can() rejects record kw/arg
    assert _can(StrictCan(), "only", record=object())
    assert not _can(StrictCan(), "no", record=object())


def test_orbit_service_provider_with_stub() -> None:
    providers = types.ModuleType("almasix.providers")

    class ServiceProvider:
        def __init__(self) -> None:
            self.app = types.SimpleNamespace(
                config=types.SimpleNamespace(
                    has=lambda *_: False,
                    set=lambda *a, **k: None,
                ),
                container=types.SimpleNamespace(
                    bound=lambda *_: False,
                    instance=lambda *a, **k: None,
                ),
                path=lambda *parts: "/".join(parts),
                make=lambda *_: None,
            )
            self._published: dict = {}
            self._commands: list = []

        def publishes(self, mapping: dict, tag: str) -> None:
            self._published[tag] = mapping

        def commands(self, cmds: list) -> None:
            self._commands.extend(cmds)

    providers.ServiceProvider = ServiceProvider
    sys.modules["almasix.providers"] = providers
    if "almasix" not in sys.modules:
        sys.modules["almasix"] = types.ModuleType("almasix")

    # First boot: prism missing → directives skipped
    sys.modules.pop("almasix.orbit.provider", None)
    from almasix.orbit.provider import OrbitServiceProvider

    sp = OrbitServiceProvider()
    sp.register()
    # config already set / registry already bound branches
    sp.app.config.has = lambda *_: True
    sp.app.container.bound = lambda *_: True
    sp.register()
    sp.boot()
    assert "orbit-assets" in sp._published
    assert sp._commands

    # Directives path with stub Engine
    prism_pkg = types.ModuleType("almasix.prism")
    prism_engine = types.ModuleType("almasix.prism.engine")
    directives: dict[str, Any] = {}

    class Engine:
        def directive(self, name: str, fn: Any) -> None:
            directives[name] = fn

    engine = Engine()
    prism_engine.Engine = Engine
    sys.modules["almasix.prism"] = prism_pkg
    sys.modules["almasix.prism.engine"] = prism_engine
    sp.app.container.bound = lambda typ: typ is Engine
    sp.app.make = lambda typ: engine
    sp._register_directives()
    assert "orbitStyles" in directives
    assert "orbitScripts" in directives
    assert "orbit" in directives["orbitStyles"]("")
    assert "orbit" in directives["orbitScripts"]("")

    # Engine not bound
    sp.app.container.bound = lambda *_: False
    sp._register_directives()


def test_infolist_falls_back_to_readonly_form_fields() -> None:
    infolist = PostResource.get_infolist()
    names = [c.get_name() for c in infolist.get_components()]
    assert "title" in names
    html = infolist.render({"title": "Hello"})
    assert "Hello" in html and "or-infolist" in html


def test_default_table_actions_use_page_urls() -> None:
    table = PostResource.get_table()
    html = table.records([{"id": 7, "title": "X"}]).render()
    assert "/posts/7" in html
    assert "/posts/7/edit" in html
    header = "".join(a.render() for a in table._header_actions)
    assert "/posts/create" in header
    assert 'data-action="view"' in html
    assert 'data-action="edit"' in html


def test_split_navigation_uses_resource_groups_without_panel_meta() -> None:
    """Group labels come from resources/pages even when no NavigationGroup is registered."""
    panel = (
        Panel.make("admin")
        .path("orbit")
        .resources([PostResource])
        .pages([DashboardPage])
        .apps_navigation()
    )
    assert panel._nav_groups == {}
    ctx = panel.menu_layout_context(active_path="/orbit/posts")
    assert any(r.label == "Content" for r in ctx.menu_roots)


def test_panel_default_middleware_is_web_and_appends() -> None:
    panel = Panel.make("admin")
    assert panel.get_middleware() == ["web"]
    panel.middleware(["auth"])
    assert panel.get_middleware() == ["web", "auth"]
    panel.middleware(["auth"])  # dedupe
    assert panel.get_middleware() == ["web", "auth"]


def test_sidebar_collapsible_defaults_off() -> None:
    panel = Panel.make("admin")
    assert panel._sidebar_collapsible is False
    panel.sidebar_collapsible()
    assert panel._sidebar_collapsible is True
    panel.sidebar_collapsible(False)
    assert panel._sidebar_collapsible is False


def test_split_navigation_menu_layout() -> None:
    from almasix.orbit.panels.navigation import NavigationGroup, NavigationItem

    panel = (
        Panel.make("admin")
        .path("orbit")
        .resources([PostResource])
        .pages([DashboardPage])
        .navigation_groups([NavigationGroup.make("Content").icon("heroicon-o-folder").sort(1)])
        .navigation_items(
            [
                NavigationItem.make("reports")
                .label("Reports")
                .url("/orbit/reports")
                .group("Content")
                .subgroup("Analytics")
                .sort(5)
            ]
        )
        .navigation_layout("sidebar_topbar")
    )
    ctx = panel.menu_layout_context(active_path="/orbit/posts")
    assert ctx.menu_roots
    assert any(r.label == "Content" for r in ctx.menu_roots)
    assert ctx.menu_secondary
    shell = panel.render_shell("<p>Hi</p>", active_path="/orbit/posts")
    assert "or-topnav" in shell and "or-action-modal-host" in shell
    assert "Content" in shell


def test_top_navigation_shows_groups_as_dropdowns() -> None:
    from almasix.orbit.panels.navigation import NavigationGroup, NavigationItem

    panel = (
        Panel.make("admin")
        .path("orbit")
        .resources([PostResource])
        .navigation_groups(
            [
                NavigationGroup.make("Content").sort(0),
                NavigationGroup.make("System").sort(10),
            ]
        )
        .navigation_items(
            [
                NavigationItem.make("settings")
                .label("Settings")
                .url("/orbit/settings")
                .group("System")
                .sort(1),
            ]
        )
        .top_navigation()
    )
    ctx = panel.menu_layout_context(active_path="/orbit/posts")
    assert ctx.layout == "top"
    assert not ctx.menu_roots
    labels = [i.label for i in ctx.menu_secondary]
    assert "Content" in labels
    assert "System" in labels
    content = next(i for i in ctx.menu_secondary if i.label == "Content")
    assert content.children
    assert any(c.label == "Posts" for c in content.children)
    shell = panel.render_shell("<p>Hi</p>", active_path="/orbit/posts")
    assert "or-topnav-dropdown" in shell
    assert ">Content<" in shell or "Content" in shell


def test_navigation_subgroup_sidebar_accordion_and_apps_dropdown() -> None:
    from almasix.orbit.panels.navigation import NavigationGroup, NavigationItem, NavigationSubgroup

    panel = (
        Panel.make("admin")
        .path("orbit")
        .resources([PostResource])
        .navigation_groups([NavigationGroup.make("Content").icon("heroicon-o-folder").sort(0)])
        .navigation_subgroups(
            [
                NavigationSubgroup.make("Writing")
                .parent("Content")
                .icon("heroicon-o-pencil")
                .sort(1)
            ]
        )
        .navigation_items(
            [
                NavigationItem.make("drafts")
                .label("Drafts")
                .url("/orbit/drafts")
                .group("Content")
                .sub_category("Writing")
                .sort(2),
                NavigationItem.make("reports")
                .label("Reports")
                .url("/orbit/reports")
                .group("Content")
                .sort(10),
            ]
        )
        .sidebar_navigation()
    )
    items = panel._collect_navigation_items()
    assert any(i.get("subgroup") == "Writing" for i in items if i["label"] == "Drafts")
    shell = panel.render_shell("<p>Hi</p>", active_path="/orbit/drafts")
    assert "or-nav-accordion" in shell
    assert "Writing" in shell
    assert "Drafts" in shell
    assert "Reports" in shell

    apps = panel.navigation_layout("apps")
    ctx = apps.menu_layout_context(active_path="/orbit/drafts")
    writing = next(i for i in ctx.menu_secondary if i.label == "Writing")
    assert writing.children
    assert any(c.label == "Drafts" for c in writing.children)
    assert any(i.label == "Reports" and not i.children for i in ctx.menu_secondary)
    apps_shell = apps.render_shell("<p>Hi</p>", active_path="/orbit/drafts")
    assert "or-topnav-dropdown" in apps_shell
    assert "Writing" in apps_shell
