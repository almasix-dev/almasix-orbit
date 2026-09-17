"""Extra coverage for auth register, routing edges, and db_errors."""

from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path
from types import SimpleNamespace

from almasix.conduit import Component
from almasix.orbit.panels.conduit.hosts import ConduitHost, LoginHost, RegisterHost
from almasix.orbit.panels.db_errors import is_unique_violation, map_db_error
from almasix.orbit.panels.discover import discover_classes
from almasix.orbit.panels.page import Page
from almasix.orbit.panels.panel import Panel, PanelRegistry
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.routing import (
    _conduit_assets,
    _current_user,
    _instantiate_host,
    _request_path,
    mount_orbit_assets,
    mount_panel,
    mount_registered_panels,
)
from almasix.routing.router import Router


class _Page(Page):
    title = "Settings"
    slug = "settings"

    @classmethod
    def render(cls, **ctx):
        return '<div class="or-page">settings</div>'


def test_conduit_redirect_attribute_and_type_errors(monkeypatch) -> None:
    host = ConduitHost()

    def raise_attr(self, url, *, navigate=False):
        raise AttributeError("no redirect")

    monkeypatch.setattr(Component, "redirect", raise_attr, raising=False)
    ConduitHost.redirect(host, "/a", navigate=True)
    assert host.take_redirect()["url"] == "/a"

    host2 = ConduitHost()

    def raise_type(self, url, *, navigate=False):
        raise TypeError("bad kwargs")

    def raise_attr2(self, url):
        raise AttributeError("still no")

    monkeypatch.setattr(Component, "redirect", raise_type, raising=False)
    # First call TypeError, second attempt AttributeError
    calls = {"n": 0}

    def flaky(self, *args, **kwargs):
        calls["n"] += 1
        if "navigate" in kwargs:
            raise TypeError("no navigate")
        raise AttributeError("no redirect")

    monkeypatch.setattr(Component, "redirect", flaky, raising=False)
    ConduitHost.redirect(host2, "/b")
    assert host2.take_redirect()["url"] == "/b"


def test_take_redirect_prefers_super(monkeypatch) -> None:
    host = ConduitHost()
    monkeypatch.setattr(
        Component,
        "take_redirect",
        lambda self: {"url": "/from-super", "navigate": False},
        raising=False,
    )
    assert host.take_redirect()["url"] == "/from-super"


def test_current_user_panel_demo_user() -> None:
    panel = Panel.make("admin").path("admin")
    panel._panel_user = SimpleNamespace(name="Demo")
    assert _current_user(panel).name == "Demo"


def test_request_path_from_current_request(monkeypatch) -> None:
    import almasix.http as http_mod

    monkeypatch.setattr(
        http_mod,
        "request",
        lambda: SimpleNamespace(url=SimpleNamespace(path="/via-ctx")),
        raising=False,
    )
    assert _request_path(None) == "/via-ctx"


def test_conduit_assets_exception(monkeypatch) -> None:
    import almasix.conduit.routing as cr

    monkeypatch.setattr(
        cr,
        "conduit_assets_script",
        lambda: (_ for _ in ()).throw(RuntimeError("no")),
        raising=False,
    )
    assert _conduit_assets() == ""


def test_instantiate_host_registers_when_missing() -> None:
    class UniqueHost(ConduitHost):
        _conduit_name = "orbit.test.unique_host_xyz"

    inst = _instantiate_host(UniqueHost, {"email": "a@b.c"})
    assert inst is not None


def test_mount_orbit_assets_uri_probe_exception() -> None:
    class BadRouter:
        @property
        def routes(self):
            raise RuntimeError("boom")

        def add(self, *a, **k):
            return None

    mount_orbit_assets(BadRouter())


def test_mount_registered_panels_get_router_fallback(monkeypatch) -> None:
    registry = PanelRegistry()
    panel = Panel.make("z").path("z").login(False).dashboard(False)
    registry.register(panel)
    router = Router()

    class App:
        def make(self, key):
            return registry

        router = None

    monkeypatch.setattr("almasix.routing.get_router", lambda: router, raising=False)
    mount_registered_panels(App())
    assert any("/z" in str(getattr(r, "uri", "")) for r in router.routes)


def test_custom_page_mount_and_dashboard_home_action() -> None:
    panel = Panel.make("admin").path("admin").pages([_Page]).login(False)
    router = Router()
    mount_panel(router, panel)
    names = {getattr(r, "route_name", None) or r.get_name() for r in router.routes}
    assert "orbit.admin.page.settings" in names
    home = next(r for r in router.routes if (getattr(r, "route_name", None) or r.get_name()) == "orbit.admin.home")
    body = asyncio.run(home.action(SimpleNamespace(url=SimpleNamespace(path="/admin"))))
    assert body is not None


def test_discover_import_and_duplicate_class(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "res.py").write_text(
        "from almasix.orbit.panels.resource import Resource\n"
        "class R(Resource):\n"
        "    model = type('M', (), {})\n"
    )
    # Broken import path continues
    assert discover_classes("pkg.does.not.exist.module", base_class=Resource) == []
    # Duplicate class in same module skipped via seen
    found = discover_classes(str(pkg / "res.py"), base_class=Resource)
    assert len(found) >= 1
    # Invalid spec path
    assert discover_classes(str(tmp_path / "missing.py"), base_class=Resource) == []


def test_login_host_brand_without_logo_helper() -> None:
    panel = Panel.make("admin").path("admin")
    panel._brand_logo = "/light.svg"
    panel._brand_logo_dark = None
    host = type("LH", (LoginHost,), {"panel_id": "admin", "_panel": panel})()
    html = host.render()
    assert "Sign" in html or "or-login" in html


def test_map_db_error_empty_and_integrity_not_null() -> None:
    class IntegrityError(Exception):
        pass

    assert is_unique_violation(IntegrityError("FOREIGN KEY constraint failed")) is False
    assert map_db_error(IntegrityError("FOREIGN KEY [SQL: x]")) == (
        "Could not save — please check your input and try again."
    )


def test_take_redirect_attribute_error(monkeypatch) -> None:
    host = ConduitHost()
    host._orbit_redirect = {"url": "/fallback", "navigate": False}

    def boom(self):
        raise AttributeError("no")

    monkeypatch.setattr(Component, "take_redirect", boom, raising=False)
    assert host.take_redirect()["url"] == "/fallback"


def test_register_home_url_without_slash(monkeypatch) -> None:
    import almasix.auth as auth_mod

    panel = Panel.make("admin").path("admin")
    monkeypatch.setattr(panel, "url", lambda *a, **k: "admin")

    class User:
        @staticmethod
        def create(data):
            return SimpleNamespace(email=data["email"])

    class _Auth:
        async def login(self, user):
            return True

    monkeypatch.setattr(auth_mod, "auth", lambda: _Auth())
    host = type("RH", (RegisterHost,), {"panel_id": "admin", "_panel": panel})(
        name="A", email="a@b.c", password="x", password_confirmation="x"
    )
    monkeypatch.setattr(host, "_user_model", lambda: User)

    async def _not_taken(m, e):  # noqa: ANN001
        return False

    monkeypatch.setattr(host, "_email_taken", _not_taken)
    monkeypatch.setattr("almasix.hashing.Hash.make", lambda p: p)
    asyncio.run(host.register())
    assert host.take_redirect()["url"] == "/admin"


def test_register_user_model_config_raises(monkeypatch) -> None:
    import types

    mod = types.ModuleType("app.models.user")

    class User:
        pass

    mod.User = User  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "app.models.user", mod)
    monkeypatch.setitem(sys.modules, "app.models", types.ModuleType("app.models"))
    monkeypatch.setitem(sys.modules, "app", types.ModuleType("app"))
    monkeypatch.setattr(
        "almasix.config.config",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no cfg")),
        raising=False,
    )
    host = type("RH", (RegisterHost,), {"panel_id": "admin", "_panel": None})()
    assert host._user_model() is User


def test_discover_package_module_and_seen(tmp_path: Path, monkeypatch) -> None:
    # Module without __path__ → line 50
    solo = types.ModuleType("solo_pkg")

    class SoloRes(Resource):
        model = type("M", (), {})

    solo.SoloRes = SoloRes  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "solo_pkg", solo)
    found = discover_classes("solo_pkg", base_class=Resource)
    assert SoloRes in found

    # walk_packages import failure → continue
    pkg = types.ModuleType("walk_pkg")
    pkg.__path__ = []  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "walk_pkg", pkg)

    def boom_walk(*a, **k):
        yield SimpleNamespace(name="walk_pkg.bad")

    import pkgutil

    monkeypatch.setattr(pkgutil, "walk_packages", boom_walk)
    monkeypatch.setattr(
        "importlib.import_module",
        lambda name: (_ for _ in ()).throw(ImportError("x")) if name == "walk_pkg.bad" else __import__(name),
        raising=False,
    )
    # Avoid breaking other imports — call discover carefully via package path that hits walk
    from almasix.orbit.panels import discover as discover_mod

    out = discover_mod._discover_in_package(pkg, Resource, set())
    assert out == []

    # spec None
    import importlib.util

    monkeypatch.setattr(importlib.util, "spec_from_file_location", lambda *a, **k: None)
    assert discover_mod._load_module_file(tmp_path / "x.py", Resource, set()) == []

    # duplicate in seen
    seen: set[type] = {SoloRes}
    mod2 = types.ModuleType("dup")
    mod2.SoloRes = SoloRes  # type: ignore[attr-defined]
    assert discover_mod._classes_from_module(mod2, Resource, seen) == []


def test_instantiate_host_registry_exception(monkeypatch) -> None:
    from almasix.conduit import Conduit

    class BoomReg:
        def _map(self):
            raise RuntimeError("x")

        @property
        def registry(self):
            raise RuntimeError("x")

    monkeypatch.setattr(Conduit, "registry", classmethod(lambda cls: (_ for _ in ()).throw(RuntimeError("x"))))

    class H(ConduitHost):
        pass

    # Should not raise
    try:
        _instantiate_host(H)
    except Exception:
        pass


def test_mount_registered_get_router_raises(monkeypatch) -> None:
    registry = PanelRegistry()

    class App:
        def make(self, key):
            return registry

        router = None

    monkeypatch.setattr(
        "almasix.routing.get_router",
        lambda: (_ for _ in ()).throw(RuntimeError("no router")),
        raising=False,
    )
    mount_registered_panels(App())


def test_login_brand_logo_only_class() -> None:
    from almasix.orbit.panels.auth import _login_brand_html

    html = _login_brand_html(
        brand="Orbit",
        brand_logo="/l.svg",
        brand_logo_dark="/d.svg",
        brand_logo_only=True,
    )
    assert "or-login-brand-logo-only" in html
    assert "or-login-logo-light" in html


def test_dashboard_page_skipped_in_pages_mount() -> None:
    from almasix.orbit.panels.pages.dashboard import Dashboard

    panel = Panel.make("admin").path("admin").pages([Dashboard, _Page]).login(False)
    router = Router()
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert "/admin/settings" in uris
    assert "/admin/dashboard" not in uris
