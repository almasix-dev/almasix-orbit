from __future__ import annotations

from almasix.orbit.panels.navigation import NavigationGroup, NavigationItem
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.routing import _current_user, make_panel_page_action
from almasix.orbit.panels.users import OrbitUser, PanelNotification, UserMenuItem


def test_orbit_user_fluent_and_panel_default() -> None:
    user = OrbitUser.make().name("Ada").email("ada@test").admin()
    assert user.name == "Ada"
    assert user.email == "ada@test"
    assert user.is_admin is True
    assert user.can("anything")
    assert str(user.name) == "Ada"

    panel = Panel.make("admin").user(user)
    assert _current_user(panel) is user

    panel2 = Panel.make("admin").default_user()
    u2 = _current_user(panel2)
    assert u2 is not None
    assert u2.email == "admin@orbit.test"


def test_fluent_nav_and_menu_items() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .navigation_group(
            NavigationGroup.make("Content")
            .icon("heroicon-o-document-text")
            .items(
                [
                    NavigationItem.make("reports")
                    .label("Reports")
                    .url("/admin/reports")
                    .icon("heroicon-o-document-text"),
                ]
            )
        )
        .navigation_item(
            NavigationItem.make("help").label("Help").url("/admin/help").group("System")
        )
        .user_menu_item(UserMenuItem.make("profile").label("Profile").url("/admin/profile"))
        .notification(PanelNotification.make("Hi").body("There"))
    )
    items = panel.navigation_items()
    labels = [i["label"] for i in items]
    assert "Reports" in labels
    assert "Help" in labels
    assert any(i["group"] == "Content" for i in items if i["label"] == "Reports")
    assert panel._user_menu_items[0]["label"] == "Profile"
    assert panel._database_notifications[0]["title"] == "Hi"


def test_no_user_means_none() -> None:
    panel = Panel.make("admin").login()
    assert _current_user(panel) is None


def test_login_gate_redirects_without_user() -> None:
    from almasix.http import Request
    from almasix.routing.router import Router
    from almasix.orbit.panels.routing import mount_panel
    from almasix.orbit.panels.resource import Resource
    from almasix.orbit.tables import Table
    from almasix.orbit.tables.columns import TextColumn

    class PostResource(Resource):
        @classmethod
        def get_model_label(cls) -> str:
            return "Post"

        @classmethod
        def get_slug(cls) -> str:
            return "posts"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

        @classmethod
        def get_records(cls):
            return []

    panel = Panel.make("admin").path("admin").middleware([], replace=True).resources([PostResource]).login()
    assert _current_user(panel) is None

    router = Router()
    mount_panel(router, panel)
    home = next(r for r in router.routes if r.route_name == "orbit.admin.home")

    import asyncio

    class _Url:
        path = "/admin"

    class _Req:
        url = _Url()

    result = asyncio.run(home.action(_Req()))
    status = getattr(result, "status_code", None) or getattr(result, "status", None)
    headers = getattr(result, "headers", {}) or {}
    location = headers.get("location") or headers.get("Location") or getattr(result, "url", None)
    assert status in (302, 303, 307) or location
    assert location is None or str(location).endswith("/login")
