"""Tests for shell + Conduit + smith + stacked_on_mobile."""

from __future__ import annotations

from pathlib import Path

from almasix.framework.application import Application
from almasix.orbit.forms import Field, Form, TextInput
from almasix.orbit.panels.commands import (
    ORBIT_COMMANDS,
    MakeOrbitFieldCommand,
    MakeOrbitPanelCommand,
    MakeOrbitResourceCommand,
    MakeOrbitUserCommand,
    OrbitInstallCommand,
)
from almasix.orbit.panels.conduit.hosts import CreateRecordHost, ListRecordsHost
from almasix.orbit.panels.navigation import normalize_nav_layout
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.routing import mount_panel
from almasix.orbit.panels.users import OrbitUser
from almasix.orbit.tables import Table, TextColumn


class PostResource(Resource):
    model = type("Post", (), {})
    navigation_label = "Posts"
    navigation_group = "Content"
    records_mutable = True
    records = [{"id": 1, "title": "Hello", "status": "draft"}]

    @classmethod
    def get_records(cls):
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title").required()])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")]).stacked_on_mobile()


def test_apps_layout_normalizes() -> None:
    assert normalize_nav_layout("apps") == "sidebar_topbar"
    assert normalize_nav_layout("sidebar") == "sidebar"


def test_shell_contains_topbar_chrome() -> None:
    panel = (
        Panel.make("admin")
        .path("admin")
        .navigation_layout("apps")
        .user(OrbitUser.make().name("Ada Lovelace").email("ada@orbit.test"))
        .database_notifications([{"title": "Hi", "body": "There"}])
        .resources([PostResource])
    )
    shell = panel.render_shell("<p>x</p>", user=panel.get_panel_user(), active_path="/admin/posts")
    assert 'x-data="orbitShell"' in shell
    assert "or-theme-toggle" in shell
    assert "or-theme-icons" in shell
    assert "or-notify" in shell
    assert "or-notify-btn" in shell
    assert "or-user-menu" in shell
    assert "or-topbar-end" in shell
    assert 'class="or-icon"' in shell or "or-icon " in shell
    assert "Ada" in shell


def test_stacked_on_mobile_renders_cards() -> None:
    html = (
        Table.make("t")
        .columns([TextColumn.make("title")])
        .records([{"title": "Hello"}])
        .stacked_on_mobile()
        .render()
    )
    assert "or-table-stacked" in html
    assert "or-table-record-card" in html
    assert "or-table-desktop" in html


def test_kanban_layout_explicit() -> None:
    html = (
        Table.make("t")
        .columns([TextColumn.make("title")])
        .records([{"title": "A", "status": "draft"}, {"title": "B", "status": "done"}])
        .layout("kanban")
        .kanban_status("status")
        .render()
    )
    assert "or-kanban" in html
    assert "draft" in html and "done" in html


def test_conduit_list_host_renders() -> None:
    panel = Panel.make("admin").path("admin").resources([PostResource])
    host_cls = ListRecordsHost.bind(panel=panel, resource=PostResource)
    host = host_cls()
    host.mount()
    html = host.render()
    assert "or-page-list" in html
    assert "Hello" in html or "Posts" in html


def test_conduit_create_host_and_custom_field() -> None:
    panel = Panel.make("admin").path("admin").resources([PostResource])
    host_cls = CreateRecordHost.bind(panel=panel, resource=PostResource)
    host = host_cls(data={"title": "New"})
    host.mount(data={"title": "New"})
    html = host.render()
    assert "or-page-create" in html
    assert 'wire:submit="create"' in html

    class MoneyInput(Field):
        def render(self, state=None, **ctx):
            name = self.get_name() or "amount"
            return self.wrap_field(name, f'<input class="or-input" name="{name}" />', **ctx)

    field = MoneyInput.make("amount")
    assert "or-input" in field.render(10)


def test_mount_panel_registers_prefixed_routes() -> None:
    from almasix.routing.router import Router

    router = Router()
    panel = Panel.make("admin").path("admin").middleware([], replace=True).resources([PostResource]).login()
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert any(u == "/admin" or u.startswith("/admin/") for u in uris)
    assert any("post" in u for u in uris)
    assert any(u.endswith("/login") or u == "/admin/login" for u in uris)

    # Host / left alone: no catch-all
    assert "/" not in uris or all(r.uri != "/" or "orbit" not in (r.route_name or "") for r in router.routes)


def test_mounted_actions_are_almasix_bindable() -> None:
    """Almasix's kernel treats ``**kwargs`` as a required parameter (e.g. ``_e``)."""
    import inspect
    import re
    from typing import Any, get_type_hints

    from almasix.http.request import Request
    from almasix.routing.router import Router

    router = Router()
    panel = Panel.make("admin").path("admin").resources([PostResource]).login()
    mount_panel(router, panel)
    skip = {str, int, float, bool, bytes, dict, list, tuple, set, type(None), Any}
    home = None
    for route in router.routes:
        action = route.action
        name = getattr(route, "route_name", None) or route.get_name()
        if name == "orbit.admin.home":
            home = action
        sig = inspect.signature(action)
        try:
            hints = get_type_hints(action)
        except Exception:
            hints = {}
        path_names = set(re.findall(r"\{([^{}:]+)", str(route.uri)))
        for pname, param in sig.parameters.items():
            if pname == "self":
                continue
            assert param.kind not in (
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            ), f"{name} has catch-all {pname!r}"
            annotation = hints.get(pname, param.annotation)
            if annotation is Request or pname in {"request", "req"}:
                continue
            if pname in path_names:
                continue
            if param.default is not inspect.Parameter.empty:
                continue
            if (
                annotation is not inspect.Parameter.empty
                and isinstance(annotation, type)
                and annotation not in skip
            ):
                continue
            raise AssertionError(f"Cannot resolve {pname!r} for {name} {action!r}")
    assert home is not None
    assert "tenant" in inspect.signature(home).parameters


def test_mount_root_panel_opt_in() -> None:
    from almasix.routing.router import Router

    router = Router()
    panel = Panel.make("root").path("/").middleware([], replace=True).resources([PostResource])
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert any("post" in u for u in uris)


def test_smith_commands_and_aliases(tmp_path: Path) -> None:
    app = Application(tmp_path)
    (tmp_path / "app").mkdir()
    (tmp_path / "config").mkdir()
    (tmp_path / "public").mkdir()

    names = {cls.name() for cls in ORBIT_COMMANDS}
    assert "orbit:install" in names
    assert "make:orbit-resource" in names
    assert "make:orbit-panel" in names
    assert "make:orbit-page" in names
    assert "make:orbit-widget" in names
    assert "make:orbit-field" in names
    assert "make:orbit-user" in names

    aliases = {a for cls in ORBIT_COMMANDS for a in cls.aliases}
    assert "orbit:resource" in aliases
    assert "orbit:panel" in aliases
    assert "orbit:page" in aliases
    assert "orbit:widget" in aliases
    assert "orbit:field" in aliases
    assert "orbit:user" in aliases

    resource_cmd = MakeOrbitResourceCommand(app)
    resource_cmd._arguments = {"name": "Blog/Post"}
    resource_cmd._options = {"force": True, "panel": "admin"}
    assert resource_cmd.handle() == 0
    assert (
        tmp_path / "app" / "orbit" / "admin" / "resources" / "blog" / "post_resource.py"
    ).is_file()

    panel_cmd = MakeOrbitPanelCommand(app)
    panel_cmd._arguments = {"name": "ops"}
    panel_cmd._options = {"path": "ops", "force": True}
    assert panel_cmd.handle() == 0
    assert (tmp_path / "app" / "orbit" / "ops" / "panel.py").is_file()

    field_cmd = MakeOrbitFieldCommand(app)
    field_cmd._arguments = {"name": "MoneyInput"}
    field_cmd._options = {"force": True}
    assert field_cmd.handle() == 0
    assert (tmp_path / "app" / "orbit" / "shared" / "fields" / "money_input.py").is_file()

    # dry / no-app still validates name
    assert MakeOrbitResourceCommand().handle(name="Post") == 0
    assert MakeOrbitResourceCommand().handle() == 2


def test_login_host_authenticate_requires_credentials() -> None:
    import asyncio

    from almasix.orbit.panels.conduit.hosts import LoginHost
    from almasix.orbit.panels.panel import Panel

    panel = Panel.make("admin").path("admin")
    host_cls = type("LoginHost_t", (LoginHost,), {"panel_id": "admin", "_panel": panel})
    host = host_cls()
    asyncio.run(host.authenticate())
    assert host.error == "Email and password are required."


def test_login_host_authenticate_redirects_on_success(monkeypatch) -> None:
    import asyncio

    import almasix.auth as auth_mod
    from almasix.orbit.panels.conduit.hosts import LoginHost
    from almasix.orbit.panels.panel import Panel

    class _Auth:
        async def attempt(self, credentials, *, remember=False):
            assert credentials["email"] == "ada@orbit.test"
            assert remember is False
            return True

    class _Session:
        def put(self, *args, **kwargs):
            return None

        def regenerate(self):
            return None

    monkeypatch.setattr(auth_mod, "auth", lambda: _Auth())
    monkeypatch.setattr(
        "almasix.session.store.get_session",
        lambda: _Session(),
    )
    panel = Panel.make("admin").path("admin")
    host_cls = type("LoginHost_t2", (LoginHost,), {"panel_id": "admin", "_panel": panel})
    host = host_cls(email="ada@orbit.test", password="password")
    asyncio.run(host.authenticate())
    assert host.error == ""
    assert host.data.get("password") == ""
    redirect = host.take_redirect()
    assert redirect is not None
    assert redirect.get("url") == "/admin"


def test_mount_panel_registers_logout_route() -> None:
    from almasix.routing.router import Router

    router = Router()
    panel = Panel.make("admin").path("admin").resources([PostResource]).login()
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert "/admin/logout" in uris
    assert "/admin/login" in uris


def test_root_panel_path_logout_and_nav_urls() -> None:
    from almasix.routing.router import Router

    panel = Panel.make("root").path("/").resources([PostResource]).login()
    assert panel.url() == "/"
    assert panel.url("logout") == "/logout"
    assert panel.url("login") == "/login"
    assert not panel.url("logout").startswith("//")

    nav = panel.navigation_items()
    posts = next(i for i in nav if i["label"] == "Posts")
    assert posts["url"] == "/posts"

    shell = panel.render_shell("<p>Hi</p>", user=object())
    assert 'href="/logout"' in shell
    assert 'href="//logout"' not in shell

    router = Router()
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert "/logout" in uris
    assert "/login" in uris


def test_make_orbit_user_creates_with_options(tmp_path: Path) -> None:

    created: dict[str, object] = {}

    class FakeUser:
        @classmethod
        async def create(cls, attrs):
            created.update(attrs)
            user = cls()
            user.email = attrs["email"]
            return user

    app = Application(tmp_path)
    cmd = MakeOrbitUserCommand(app)
    cmd._options = {
        "name": "Ada",
        "email": "ada@orbit.test",
        "password": "secret123",
        "model": None,
    }
    cmd._load_model = lambda path: FakeUser  # type: ignore[method-assign]
    cmd._default_user_model = lambda: "fake.User"  # type: ignore[method-assign]
    assert cmd.handle() == 0
    assert created["name"] == "Ada"
    assert created["email"] == "ada@orbit.test"
    assert created["password"] != "secret123"  # hashed
    assert len(str(created["password"])) > 20


def test_make_orbit_user_scaffolds_model(tmp_path: Path) -> None:

    app = Application(tmp_path)
    (tmp_path / "app").mkdir()
    (tmp_path / "config").mkdir()
    cmd = MakeOrbitUserCommand(app)
    cmd._options = {
        "name": "Ada",
        "email": "ada@orbit.test",
        "password": "secret123",
        "scaffold": True,
        "model": None,
    }

    class FakeUser:
        @classmethod
        async def create(cls, attrs):
            user = cls()
            user.email = attrs["email"]
            return user

    cmd._create_user = lambda model, **kw: FakeUser()  # type: ignore[method-assign]
    # After scaffold, load real written module path — stub load to FakeUser
    original_scaffold = cmd._scaffold_user_model

    def scaffold_and_stub(path: str) -> None:
        original_scaffold(path)
        cmd._load_model = lambda p: FakeUser  # type: ignore[method-assign]

    cmd._scaffold_user_model = scaffold_and_stub  # type: ignore[method-assign]
    assert cmd.handle() == 0
    assert (tmp_path / "app" / "models" / "user.py").is_file()
    assert (tmp_path / "config" / "auth.py").is_file()


def test_orbit_install_writes_config(tmp_path: Path) -> None:
    app = Application(tmp_path)
    (tmp_path / "app" / "providers").mkdir(parents=True)
    (tmp_path / "config").mkdir()
    (tmp_path / "public").mkdir()
    cmd = OrbitInstallCommand(app)
    cmd._options = {"path": "admin", "panel": "admin", "force": True}
    # vendor:publish may fail without full boot — install should still write files
    result = cmd.handle()
    assert result == 0
    assert (tmp_path / "config" / "orbit.py").is_file()
    assert (tmp_path / "app" / "providers" / "orbit_panel_provider.py").is_file()
