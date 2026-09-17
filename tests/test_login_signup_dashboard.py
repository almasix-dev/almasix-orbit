"""Tests for extendable login, signup, and dashboard panel APIs."""

from __future__ import annotations

from almasix.orbit.panels.auth import Login, Register
from almasix.orbit.panels.conduit.hosts import LoginHost, RegisterHost
from almasix.orbit.panels.pages.dashboard import Dashboard
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.routing import mount_panel
from almasix.routing.router import Router


class PostResource(Resource):
    model = type("Post", (), {})
    navigation_label = "Posts"
    navigation_group = "Content"

    @classmethod
    def get_slug(cls) -> str:
        return "posts"


class CustomLogin(Login):
    title = "Custom Sign In"

    @classmethod
    def render(cls, **ctx):  # type: ignore[no-untyped-def]
        return '<div class="custom-login">CUSTOM_LOGIN</div>'


class CustomSignup(Register):
    title = "Join Us"

    @classmethod
    def render(cls, **ctx):  # type: ignore[no-untyped-def]
        return '<div class="custom-signup">CUSTOM_SIGNUP</div>'


class CustomDashboard(Dashboard):
    title = "Home Base"

    @classmethod
    def render(cls, **ctx):  # type: ignore[no-untyped-def]
        return '<div class="custom-dash">CUSTOM_DASH</div>'


def test_login_accepts_custom_page_class() -> None:
    panel = Panel.make("admin").path("admin").login(CustomLogin)
    assert panel.login_enabled()
    assert panel.login_page() is CustomLogin

    host = type(
        "H",
        (LoginHost,),
        {"_panel": panel, "_page_cls": CustomLogin, "panel_id": "admin"},
    )()
    assert "CUSTOM_LOGIN" in host.render()


def test_signup_mounts_register_and_login_footer_link() -> None:
    router = Router()
    panel = Panel.make("admin").path("admin").login().signup().resources([PostResource])
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert "/admin/register" in uris
    assert "/admin/login" in uris

    host = type(
        "H",
        (LoginHost,),
        {"_panel": panel, "_page_cls": Login, "panel_id": "admin"},
    )()
    html = host.render()
    assert "Sign up" in html
    assert 'href="/admin/register"' in html

    off = Panel.make("x").path("x").login().signup(False)
    host_off = type(
        "H2",
        (LoginHost,),
        {"_panel": off, "_page_cls": Login, "panel_id": "x"},
    )()
    assert "Sign up" not in host_off.render()


def test_signup_custom_page_and_register_footer() -> None:
    panel = Panel.make("admin").path("admin").signup(CustomSignup)
    assert panel.signup_page() is CustomSignup
    host = type(
        "H",
        (RegisterHost,),
        {"_panel": panel, "_page_cls": CustomSignup, "panel_id": "admin"},
    )()
    assert "CUSTOM_SIGNUP" in host.render()

    default_host = type(
        "H2",
        (RegisterHost,),
        {"_panel": panel, "_page_cls": Register, "panel_id": "admin"},
    )()
    html = default_host.render()
    assert "Sign in" in html
    assert 'href="/admin/login"' in html


def test_dashboard_is_default_home_even_with_resources() -> None:
    router = Router()
    panel = Panel.make("admin").path("admin").resources([PostResource]).login(False)
    mount_panel(router, panel)
    names = {getattr(r, "route_name", None) or r.get_name() for r in router.routes}
    assert "orbit.admin.home" in names
    uris = {r.uri for r in router.routes}
    assert "/admin" in uris
    assert "/admin/posts" in uris

    nav = panel.navigation_items()
    assert any(i["label"] == "Dashboard" and i["url"] == "/admin" for i in nav)


def test_dashboard_false_uses_first_resource_home() -> None:
    router = Router()
    panel = (
        Panel.make("admin")
        .path("admin")
        .dashboard(False)
        .resources([PostResource])
        .login(False)
    )
    mount_panel(router, panel)
    assert panel.dashboard_enabled() is False
    nav = panel.navigation_items()
    assert not any(i.get("label") == "Dashboard" for i in nav)


def test_custom_dashboard_page() -> None:
    panel = Panel.make("admin").path("admin").dashboard(CustomDashboard)
    assert panel.dashboard_page() is CustomDashboard
    assert "CUSTOM_DASH" in CustomDashboard.render()


def test_root_panel_auth_urls_with_signup() -> None:
    router = Router()
    panel = Panel.make("root").path("/").login().signup()
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert "/login" in uris
    assert "/register" in uris
    assert "/logout" in uris
    assert panel.url("register") == "/register"


def test_dashboard_nav_root_named_and_first() -> None:
    panel = Panel.make("root").path("/").resources([PostResource]).login(False)
    ctx = panel.menu_layout_context(active_path="/")
    labels = [r.label for r in ctx.menu_roots]
    assert labels[0] == "Dashboard"
    assert "Menu" not in labels
    assert "Content" in labels
    dash = next(r for r in ctx.menu_roots if r.label == "Dashboard")
    assert dash.active is True
    content = next(r for r in ctx.menu_roots if r.label == "Content")
    assert content.active is False


def test_root_panel_dashboard_active_not_content() -> None:
    panel = Panel.make("root").path("/").resources([PostResource]).login(False)
    home = panel.menu_layout_context(active_path="/")
    assert home.menu_active_root is not None
    assert home.menu_active_root.label == "Dashboard"
    dash_item = next(i for i in home.flat_items if i["label"] == "Dashboard")
    assert dash_item["active"] is True
    posts = next(i for i in home.flat_items if i["label"] == "Posts")
    assert posts["active"] is False

    nested = panel.menu_layout_context(active_path="/posts")
    assert nested.menu_active_root is not None
    assert nested.menu_active_root.label == "Content"
    posts2 = next(i for i in nested.flat_items if i["label"] == "Posts")
    assert posts2["active"] is True
    dash2 = next(i for i in nested.flat_items if i["label"] == "Dashboard")
    assert dash2["active"] is False
