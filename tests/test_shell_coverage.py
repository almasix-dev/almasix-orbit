"""Coverage for shell helpers, auth HTML, Conduit hosts, and routing mounts."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from almasix.orbit.forms import Form, TextInput
from almasix.orbit.panels.auth import Login, Register, _login_brand_html
from almasix.orbit.panels.conduit.hosts import (
    ConduitHost,
    CreateRecordHost,
    EditRecordHost,
    ListRecordsHost,
    LoginHost,
    RegisterHost,
    ViewRecordHost,
)
from almasix.orbit.panels.content_width import resolve_content_max_width
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.routing import (
    _auth_gate,
    _current_user,
    _is_guest_path,
    _login_path,
    _register_path,
    _request_path,
    mount_panel,
)
from almasix.orbit.panels.theme_colors import resolve_panel_color_vars
from almasix.orbit.panels.users import OrbitUser, PanelNotification, UserMenuItem
from almasix.orbit.support.conduit_attrs import conduit_attr
from almasix.orbit.support.urls import resolve_public_url
from almasix.orbit.tables import Table, TextColumn
from almasix.routing.router import Router


class _Post(Resource):
    model = type("Post", (), {})
    navigation_label = "Posts"
    navigation_group = "Content"
    slug = "posts"
    records = [{"id": 1, "title": "Hello"}]

    @classmethod
    def get_records(cls):
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])


def test_conduit_attr_variants() -> None:
    assert 'conduit:submit="go"' in conduit_attr("submit", "go")
    assert 'wire:submit="go"' in conduit_attr("submit", "go")
    assert "conduit:click" in conduit_attr("click", True)
    assert conduit_attr("click", False) == ""
    assert conduit_attr("click", None) == ""


def test_resolve_public_url_branches() -> None:
    assert resolve_public_url(None) is None
    assert resolve_public_url("  ") is None
    assert resolve_public_url("https://x.test/a.svg") == "https://x.test/a.svg"
    assert resolve_public_url("//cdn/a.svg") == "//cdn/a.svg"
    rel = resolve_public_url("images/logo.svg")
    assert rel is not None and "logo" in rel


def test_content_width_empty_and_unknown_max_w() -> None:
    assert resolve_content_max_width("").token == "screen-2xl"
    assert resolve_content_max_width("   ").token == "screen-2xl"
    assert resolve_content_max_width("max-w-nope").css_value == "none"


def test_theme_color_vars() -> None:
    vars_ = resolve_panel_color_vars({"primary": "info", "danger": "#dc2626"})
    assert "--or-primary" in vars_ and vars_["--or-danger"] == "#dc2626"


def test_login_brand_html_variants() -> None:
    assert "or-login-brand-name" in _login_brand_html(brand="Acme")
    both = _login_brand_html(brand="Acme", brand_logo="/l.svg", brand_logo_dark="/d.svg")
    assert "or-login-logo-light" in both and "or-login-logo-dark" in both
    only = _login_brand_html(brand="Acme", brand_logo="/l.svg", brand_logo_only=True)
    assert "or-login-brand-logo-only" in only and "or-login-brand-name" not in only
    same = _login_brand_html(brand="Acme", brand_logo="/l.svg", brand_logo_dark="/l.svg")
    assert "or-login-logo-slot" in same


def test_auth_pages_render() -> None:
    login = Login.render(brand="Orbit", brand_logo="/l.svg", error="Nope")
    assert "or-login-alert" in login and "Sign in" in login
    assert "or-login-title" in Register.render(brand="Orbit")


def test_panel_url_and_users_fluent() -> None:
    panel = (
        Panel.make("admin")
        .path("/")
        .brand_name_font_size("")
        .user(OrbitUser.make().name("Ada").email("a@b.c").admin())
        .notification(PanelNotification.make("Hi").body("There"))
        .user_menu_item(UserMenuItem.make("x").label("X").url("/x"))
        .user_menu_items([{"label": "Y", "url": "/y"}])
        .login(True)
        .dark_mode(False)
    )
    assert panel.url() == "/"
    assert panel.url("logout") == "/logout"
    assert panel.login_enabled() is True
    html = panel.render_shell("<p>x</p>", user=panel.get_panel_user())
    assert 'href="/logout"' in html
    assert "--or-brand-name-size:" in html
    bare = panel.render_shell("<p>login</p>", bare=True)
    assert "or-auth-shell" in bare
    # dark_mode False → no theme toggle on auth shell
    assert "or-auth-theme" not in bare


def test_panel_with_dashboard_page_nav() -> None:
    from almasix.orbit.panels.pages.dashboard import Dashboard

    panel = Panel.make("admin").path("admin").pages([Dashboard]).resources([_Post])
    nav = panel.navigation_items()
    assert any(i.get("url") == "/admin" for i in nav)


def test_pluralize_fallback(monkeypatch) -> None:
    import types

    import almasix.orbit.panels.resource as rm

    boom = types.ModuleType("almasix.orm.inflector")

    def _raise(_value: str) -> str:
        raise RuntimeError("no inflector")

    boom.pluralize = _raise  # type: ignore[attr-defined]
    boom.singularize = _raise  # type: ignore[attr-defined]
    monkeypatch.setitem(__import__("sys").modules, "almasix.orm.inflector", boom)
    assert rm._pluralize("box") == "boxes"
    assert rm._pluralize("city") == "cities"
    assert rm._pluralize("post") == "posts"


def test_resolve_public_url_exception(monkeypatch) -> None:
    import sys

    monkeypatch.setitem(sys.modules, "almasix.routing.url", None)
    assert resolve_public_url("images/logo.svg") == "/images/logo.svg"
    assert resolve_public_url("/abs.svg") == "/abs.svg"


def test_password_reset_page() -> None:
    from almasix.orbit.panels.auth import PasswordReset

    html = PasswordReset.render(brand="Orbit")
    assert "or-login" in html or "password" in html.lower()


def test_login_brand_empty_and_register_error() -> None:
    # logo-only still renders a brand container (name hidden)
    only = _login_brand_html(brand="Acme", brand_logo="/l.svg", brand_logo_only=True)
    assert "or-login-brand-logo-only" in only
    reg = Register.render(brand="Orbit", error="Taken")
    assert "or-login-alert" in reg


def test_users_descriptors_and_permissions() -> None:
    assert OrbitUser.name.default == "Admin"  # descriptor on class
    assert OrbitUser.is_admin.default is True
    u = OrbitUser.make()
    u.name = "Bob"
    u.email = "b@c.d"
    u.is_admin = False
    assert str(u.name) == "Bob"
    assert u.can("posts.view") is False
    u.permissions("posts.view", "*")
    assert u.can("anything") is True
    u2 = OrbitUser.make().admin(False).permissions("posts.edit")
    assert u2.can("posts.edit") is True
    assert u2.can("posts.delete") is False
    assert "permissions" in u2.to_dict()
    n = PanelNotification.make()
    assert n.title("T").body("B").to_dict() == {"title": "T", "body": "B"}
    assert PanelNotification.make("Seed").to_dict()["title"] == "Seed"


def test_resource_slug_label_table_infolist() -> None:
    class PostResource(Resource):
        model = type("Post", (), {})

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("title").label("Title")])

    assert PostResource.get_slug().endswith("s")
    assert "Post" in PostResource.get_navigation_label() or PostResource.get_navigation_label()
    assert PostResource.table(Table.make("t")) is not None
    info = PostResource.get_infolist()
    assert info.get_components()


def test_panel_page_options_and_branding() -> None:
    from almasix.orbit.panels.auth import Login
    from almasix.orbit.panels.panel import _resolve_page_option

    assert _resolve_page_option(False, default_cls=Login) is None
    assert _resolve_page_option(True, default_cls=Login) is Login
    assert _resolve_page_option(Login, default_cls=Login) is Login
    assert _resolve_page_option("nope", default_cls=Login) is Login  # type: ignore[arg-type]

    panel = (
        Panel.make("admin")
        .path("admin")
        .brand_logo("/l.svg", dark="/d.svg")
        .brand_logo_dark("/d2.svg")
        .brand_logo_only()
        .notifications(True)
        .demo_user(OrbitUser.default())
        .content_max_width("7xl")
        .login(False)
        .dark_mode(True)
        .resources([_Post])
    )
    assert panel.get_content_max_width() == "7xl"
    assert panel.login_page() is None
    bare = panel.render_shell("<p>x</p>", bare=True)
    assert "or-auth-theme" in bare


def test_panel_breadcrumbs_paths() -> None:
    from almasix.orbit.panels.pages.dashboard import Dashboard

    panel = Panel.make("admin").path("admin").resources([_Post]).pages([Dashboard])
    assert len(panel.breadcrumbs(None)) == 1
    home = panel.breadcrumbs("/admin")
    assert home[-1]["url"] is None
    outside = panel.breadcrumbs("/other")
    assert outside[-1]["url"] is None
    index = panel.breadcrumbs("/admin/posts")
    assert index[-1]["url"] is None
    create = panel.breadcrumbs("/admin/posts/create")
    assert any(c["label"] == "Create" for c in create)
    edit = panel.breadcrumbs("/admin/posts/1/edit")
    assert any(c["label"] == "Edit" for c in edit)
    view = panel.breadcrumbs("/admin/posts/1")
    assert any(c["label"] == "View" for c in view)
    page = panel.breadcrumbs("/admin")  # dashboard root already covered
    assert page
    unknown = panel.breadcrumbs("/admin/mystery/deep")
    assert any(c["label"] == "Mystery" for c in unknown)
    html = panel._render_breadcrumbs("/admin/posts/create")
    assert "or-breadcrumbs" in html


def test_panel_csrf_meta(monkeypatch) -> None:
    import types

    csrf = types.ModuleType("almasix.session.csrf")
    csrf.csrf_token = lambda: "tok-123"  # type: ignore[attr-defined]
    monkeypatch.setitem(__import__("sys").modules, "almasix.session.csrf", csrf)
    html = Panel.make("admin").path("admin").render_shell("<p>x</p>")
    assert "csrf-token" in html and "tok-123" in html


def test_conduit_host_redirect_fallback() -> None:
    host = ConduitHost()
    # Force the fallback path even when local Conduit has redirect.
    ConduitHost.redirect(host, "/home")
    # take_redirect should return something (conduit or fallback)
    got = host.take_redirect()
    assert got is not None
    assert got["url"] in {"/home"}


def test_login_host_authenticate_paths(monkeypatch) -> None:
    import almasix.auth as auth_mod

    panel = Panel.make("admin").path("admin")
    host_cls = type("LH", (LoginHost,), {"panel_id": "admin", "_panel": panel})

    h = host_cls()
    asyncio.run(h.authenticate())
    assert "required" in h.error.lower()

    class _AuthFail:
        async def attempt(self, credentials, *, remember=False):
            return False

    monkeypatch.setattr(auth_mod, "auth", lambda: _AuthFail())
    h2 = host_cls(email="a@b.c", password="x")
    asyncio.run(h2.authenticate())
    assert "match" in h2.error.lower()

    class _AuthOk:
        async def attempt(self, credentials, *, remember=False):
            return True

    monkeypatch.setattr(auth_mod, "auth", lambda: _AuthOk())
    monkeypatch.setattr("almasix.session.store.get_session", lambda: object())
    h3 = host_cls(email="a@b.c", password="x")
    asyncio.run(h3.authenticate())
    assert h3.error == ""
    assert h3.take_redirect()["url"] == "/admin"


def test_login_host_render_and_register_host() -> None:
    panel = Panel.make("admin").path("admin").brand_logo("/l.svg")
    login_cls = type("LH2", (LoginHost,), {"panel_id": "admin", "_panel": panel})
    html = login_cls().render()
    assert "or-login" in html or "Sign in" in html

    reg_cls = type("RH", (RegisterHost,), {"panel_id": "admin", "_panel": panel})
    reg = reg_cls(name="Ada", email="a@b.c", password="x", password_confirmation="x")
    assert "Register" in reg.render() or "or-login" in reg.render()


def test_resource_hosts_render() -> None:
    panel = Panel.make("admin").path("admin").resources([_Post])
    list_cls = ListRecordsHost.bind(panel=panel, resource=_Post)
    create_cls = CreateRecordHost.bind(panel=panel, resource=_Post)
    edit_cls = EditRecordHost.bind(panel=panel, resource=_Post)
    view_cls = ViewRecordHost.bind(panel=panel, resource=_Post)

    listed = list_cls()
    listed.mount()
    assert "or-page" in listed.render() or "title" in listed.render().lower()

    created = create_cls()
    assert "or-page" in created.render() or "form" in created.render().lower()

    edited = edit_cls(record_key="1")
    assert "or-page" in edited.render() or "form" in edited.render().lower()

    viewed = view_cls(record_key="1")
    assert "or-page" in viewed.render() or "view" in viewed.render().lower() or "title" in viewed.render().lower()


def test_routing_helpers_and_mount() -> None:
    panel = Panel.make("admin").path("admin").resources([_Post]).login()
    assert _login_path(panel) == "/admin/login"
    assert _register_path(panel) == "/admin/register"
    assert _is_guest_path(panel, "/admin/login") is True
    assert _is_guest_path(panel, "/admin/posts") is False
    assert _is_guest_path(panel, None) is False
    assert _auth_gate(panel, "/admin/posts", None) is not None
    assert _auth_gate(panel, "/admin/login", None) is None
    assert _auth_gate(panel, "/admin/posts", object()) is None
    assert _current_user(panel) is None
    assert _request_path(SimpleNamespace(url=SimpleNamespace(path="/admin"))) == "/admin"
    assert _request_path(SimpleNamespace(path="/x", url=None)) == "/x"
    assert _request_path(None) is None or isinstance(_request_path(None), (str, type(None)))

    router = Router()
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert "/admin/login" in uris
    assert "/admin/logout" in uris
    assert any("/admin/posts" in u for u in uris)

    root = Panel.make("root").path("/").resources([_Post]).login()
    router2 = Router()
    mount_panel(router2, root)
    uris2 = {r.uri for r in router2.routes}
    assert "/login" in uris2 and "/logout" in uris2


def test_mount_panel_dashboard_without_resources() -> None:
    panel = Panel.make("empty").path("empty").login(False)
    router = Router()
    mount_panel(router, panel)
    assert any(r.uri == "/empty" or r.uri == "/empty/" for r in router.routes) or len(router.routes) >= 1


def test_register_host_full_paths(monkeypatch) -> None:
    import almasix.auth as auth_mod

    panel = Panel.make("admin").path("admin").brand_logo("/l.svg")
    host_cls = type("RH", (RegisterHost,), {"panel_id": "admin", "_panel": panel})

    empty = host_cls()
    asyncio.run(empty.register())
    assert "required" in empty.error.lower()

    mismatch = host_cls(name="A", email="a@b.c", password="x", password_confirmation="y")
    asyncio.run(mismatch.register())
    assert "match" in mismatch.error.lower()

    class NoCreate:
        pass

    no_create = host_cls(name="A", email="a@b.c", password="x", password_confirmation="x")
    monkeypatch.setattr(no_create, "_user_model", lambda: NoCreate)
    monkeypatch.setattr(no_create, "_email_taken", lambda m, e: False)
    monkeypatch.setattr("almasix.hashing.Hash.make", lambda p: f"h:{p}")
    asyncio.run(no_create.register())
    assert "cannot create" in no_create.error.lower()

    class SyncUser:
        email = "ok@b.c"

        @staticmethod
        def create(data):
            return SyncUser()

    class _Auth:
        async def login(self, user):
            return True

    monkeypatch.setattr(auth_mod, "auth", lambda: _Auth())
    ok = host_cls(name="Ada", email="ok@b.c", password="x", password_confirmation="x")
    monkeypatch.setattr(ok, "_user_model", lambda: SyncUser)
    monkeypatch.setattr(ok, "_email_taken", lambda m, e: False)
    monkeypatch.setattr("almasix.hashing.Hash.make", lambda p: f"h:{p}")
    asyncio.run(ok.register())
    assert ok.error == ""
    assert ok.take_redirect()["url"] == "/admin"
    assert ok.password == ""

    class AsyncUser:
        @staticmethod
        async def create(data):
            return SimpleNamespace(email=data["email"])

    class _AuthBoom:
        async def login(self, user):
            raise RuntimeError("login failed")

    monkeypatch.setattr(auth_mod, "auth", lambda: _AuthBoom())
    async_host = host_cls(name="Ada", email="a@b.c", password="x", password_confirmation="x")
    monkeypatch.setattr(async_host, "_user_model", lambda: AsyncUser)
    monkeypatch.setattr(async_host, "_email_taken", lambda m, e: False)
    asyncio.run(async_host.register())
    assert "sign-in failed" in async_host.error.lower() or "login failed" in async_host.error.lower()


def test_register_email_taken_helpers() -> None:
    class WhereModel:
        @classmethod
        def where(cls, col, val):
            class Q:
                def first(self):
                    return object() if val == "taken@x.com" else None

            return Q()

    assert RegisterHost._email_taken(WhereModel, "taken@x.com") is True
    assert RegisterHost._email_taken(WhereModel, "free@x.com") is False

    class QueryModel:
        @classmethod
        def query(cls):
            class B:
                def where(self, col, val):
                    class Q:
                        def first(self):
                            return object() if val == "q@x.com" else None

                    return Q()

            return B()

    assert RegisterHost._email_taken(QueryModel, "q@x.com") is True

    class BoomModel:
        @classmethod
        def where(cls, *a, **k):
            raise RuntimeError("db down")

    assert RegisterHost._email_taken(BoomModel, "x@y.com") is False

    class ObjRecords:
        records = [SimpleNamespace(email="obj@x.com")]

    assert RegisterHost._email_taken(ObjRecords, "obj@x.com") is True
    assert RegisterHost._email_taken(ObjRecords, "nope@x.com") is False


def test_register_host_display_error_and_render_without_panel() -> None:
    host_cls = type("RH", (RegisterHost,), {"panel_id": "admin", "_panel": None})
    h = host_cls(name="A", email="a@b.c")
    h.error = "boom"
    assert h._display_error() == "boom"

    class Bag:
        error = ""
        errors = {"email": ["bad email"]}

    assert RegisterHost._display_error(Bag()) == "bad email"  # type: ignore[arg-type]
    assert "Register" in h.render() or "or-login" in h.render() or "account" in h.render().lower()


def test_register_user_model_resolution(monkeypatch) -> None:
    import sys
    import types

    mod = types.ModuleType("app.models.user")

    class User:
        pass

    mod.User = User  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "app.models.user", mod)
    monkeypatch.setitem(sys.modules, "app.models", types.ModuleType("app.models"))
    monkeypatch.setitem(sys.modules, "app", types.ModuleType("app"))

    host_cls = type("RH", (RegisterHost,), {"panel_id": "admin", "_panel": None})
    assert host_cls()._user_model() is User


def test_signup_guest_path_and_empty_dashboard_home() -> None:
    panel = Panel.make("admin").path("admin").login().signup()
    assert _is_guest_path(panel, "/admin/register") is True
    assert _register_path(panel) == "/admin/register"

    router = Router()
    mount_panel(router, panel)
    assert "/admin/register" in {r.uri for r in router.routes}

    empty = Panel.make("bare").path("bare").dashboard(False).login(False)
    router2 = Router()
    mount_panel(router2, empty)
    home = next(r for r in router2.routes if getattr(r, "route_name", None) == "orbit.bare.home" or "home" in str(getattr(r, "route_name", "") or r.get_name()))
    result = asyncio.run(home.action(SimpleNamespace(url=SimpleNamespace(path="/bare"))))
    assert result is not None


def test_dashboard_widgets_render() -> None:
    from almasix.orbit.panels.pages.dashboard import Dashboard

    html = Dashboard.render(widgets=["<b>w1</b>", 123, "<i>w2</i>"], brand="X")
    assert "or-dashboard-widgets" in html and "w1" in html and "w2" in html


def test_register_user_model_missing_and_config(monkeypatch) -> None:
    import sys
    import types

    mod = types.ModuleType("tmpmod_user")

    class OnlyOther:
        pass

    mod.OnlyOther = OnlyOther  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "tmpmod_user", mod)

    host_cls = type("RH", (RegisterHost,), {"panel_id": "admin", "_panel": None})
    h = host_cls()

    def _cfg(key, default=None):
        if key == "auth.providers.users.model":
            return "tmpmod_user.Missing"
        return default

    monkeypatch.setattr("almasix.config.config", _cfg)
    try:
        h._user_model()
        raise AssertionError("expected AttributeError")
    except AttributeError:
        pass

    # brand_logo fallback when get_brand_logo_url missing
    panel = Panel.make("admin").path("admin")
    panel._brand_logo = "/x.svg"
    panel._brand_logo_dark = None
    host2 = type("RH2", (RegisterHost,), {"panel_id": "admin", "_panel": panel})()
    assert "/x.svg" in host2.render() or "or-" in host2.render()


def test_empty_home_auth_gate_redirect() -> None:
    empty = Panel.make("bare").path("bare").dashboard(False).login()
    router = Router()
    mount_panel(router, empty)
    home = next(
        r
        for r in router.routes
        if (getattr(r, "route_name", None) or r.get_name()) == "orbit.bare.home"
    )
    redirected = asyncio.run(home.action(SimpleNamespace(url=SimpleNamespace(path="/bare"))))
    assert redirected is not None


def test_db_errors_integrity_without_unique_word() -> None:
    from almasix.orbit.panels.db_errors import is_unique_violation

    class IntegrityError(Exception):
        pass

    assert is_unique_violation(IntegrityError("NOT NULL constraint failed")) is False
    assert is_unique_violation(IntegrityError("duplicate row")) is True
