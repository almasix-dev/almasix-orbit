"""Conduit-backed custom page mounting."""

from __future__ import annotations

from typing import Any, ClassVar

import pytest
from almasix.orbit.panels.page import Page
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.routing import mount_panel


class _StubHost:
    _conduit_name = "orbit.test.stub-host"
    _panel: ClassVar[Any] = None
    _page: ClassVar[Any] = None

    @classmethod
    def bind(cls, *, panel: Any, page: Any) -> type[_StubHost]:
        class Bound(_StubHost):
            pass

        Bound._panel = panel
        Bound._page = page
        Bound._conduit_name = f"orbit.{panel.id}.page.live"
        return Bound

    @classmethod
    def _public_property_names(cls) -> set[str]:
        return set()

    def mount(self, **kwargs: Any) -> None:
        return None

    def render(self) -> str:
        return '<div class="or-page" data-live="1">live</div>'


class LiveSettingsPage(Page):
    slug = "live-settings"
    title = "Live"

    @classmethod
    def get_conduit_host(cls) -> type[Any] | None:
        return _StubHost

    @classmethod
    def render(cls, **ctx: Any) -> str:
        return '<div class="or-page">static-fallback</div>'


class StaticPage(Page):
    slug = "static-page"
    title = "Static"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        return '<div class="or-page">static-only</div>'


def test_page_default_conduit_host_is_none() -> None:
    assert Page.get_conduit_host() is None
    assert StaticPage.get_conduit_host() is None
    assert LiveSettingsPage.get_conduit_host() is _StubHost


def test_mount_panel_registers_live_and_static_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    from almasix.orbit.panels import routing as routing_mod


    class FakeRouter:
        def __init__(self) -> None:
            self.routes: list[dict[str, Any]] = []

        def add(self, methods: Any, path: str, endpoint: Any = None, **kwargs: Any) -> None:
            self.routes.append(
                {"methods": methods, "path": path, "endpoint": endpoint, **kwargs}
            )

    monkeypatch.setattr(
        routing_mod,
        "_instantiate_host",
        lambda host_cls, extras=None: type(
            "Inst",
            (),
            {
                "render": lambda self: '<div data-live="1">live</div>',
                "_orbit_redirect": None,
            },
        )(),
    )

    async def fake_embed(instance: Any) -> str:
        return instance.render()

    monkeypatch.setattr(routing_mod, "_embed_async", fake_embed)
    monkeypatch.setattr(routing_mod, "_current_user", lambda panel=None: None)
    monkeypatch.setattr(routing_mod, "_auth_gate", lambda *a, **k: None)
    monkeypatch.setattr(routing_mod, "_apply_tenant_slug", lambda *a, **k: None)
    monkeypatch.setattr(routing_mod, "_request_path", lambda request=None: "/admin/live-settings")
    monkeypatch.setattr(routing_mod, "_conduit_assets", lambda: "")
    monkeypatch.setattr(
        routing_mod,
        "_html_response",
        lambda body: type("R", (), {"body": body})(),
    )

    panel = (
        Panel.make("admin")
        .path("/admin")
        .pages([LiveSettingsPage, StaticPage])
    )
    router = FakeRouter()
    mount_panel(router, panel)

    paths = {r["path"] for r in router.routes}
    assert any("live-settings" in p for p in paths)
    assert any("static-page" in p for p in paths)

    live_route = next(r for r in router.routes if "live-settings" in r["path"])
    # Invoke the action and ensure Conduit host path is used (live marker).
    import asyncio

    response = asyncio.run(live_route["endpoint"](request=None))
    assert "data-live" in response.body
    assert "static-fallback" not in response.body

    static_route = next(r for r in router.routes if "static-page" in r["path"])
    static_response = asyncio.run(static_route["endpoint"](request=None))
    assert "static-only" in static_response.body
