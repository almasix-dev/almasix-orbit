"""SPA mode, billing adapters, and multi-panel registry helpers."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

from almasix.orbit.panels import (
    BillingPlan,
    ManageBilling,
    MemoryBillingProvider,
    Panel,
    PanelRegistry,
    Tenancy,
    Tenant,
)
from almasix.orbit.panels.billing import tenant_key
from almasix.orbit.panels.mfa import AppAuthentication
from almasix.orbit.panels.routing import mount_panel
from almasix.orbit.panels.users import OrbitUser
from almasix.routing.router import Router


def run(coro: Any) -> Any:
    return asyncio.run(coro) if asyncio.iscoroutine(coro) else coro


def test_tenant_key_and_memory_billing_provider() -> None:
    assert tenant_key(None) == "default"
    assert tenant_key({"id": 9}) == "9"
    assert tenant_key({"slug": "acme"}) == "acme"
    assert tenant_key({}) == "default"
    obj = SimpleNamespace(id=3, slug="x")
    assert tenant_key(obj) == "3"
    assert tenant_key(SimpleNamespace(pk="p")) == "p"
    lonely = object()
    assert tenant_key(lonely) == str(lonely)

    free = BillingPlan("free", "Free")
    assert free.price_label() == "Free"
    paid = BillingPlan("pro", "Pro", 2900, description="All seats")
    assert "29.00" in paid.price_label()
    assert paid.to_dict()["id"] == "pro"

    provider = MemoryBillingProvider(portal_url="/billing/portal")
    tenant = Tenant(1, "Acme", slug="acme")
    assert len(provider.plans()) == 2
    assert provider.current_subscription(tenant=tenant) is None
    assert provider.subscribe("missing", tenant=tenant)["ok"] is False
    assert provider.subscribe("pro", tenant=tenant, user="ada")["ok"] is True
    sub = provider.current_subscription(tenant=tenant)
    assert sub is not None and sub["plan_id"] == "pro"
    provider._subs[tenant_key(tenant)] = "gone"
    assert provider.current_subscription(tenant=tenant) is None
    assert provider.portal_url() == "/billing/portal"


def test_manage_billing_render_and_subscribe() -> None:
    assert ManageBilling.handle_subscribe("pro")["ok"] is False
    panel = Panel.make("bill").path("admin").tenant_billing(True)
    html = ManageBilling.render(panel=panel, tenant=Tenant(1, "Acme", slug="acme"))
    assert "or-page-tenant-billing" in html
    assert "Starter" in html and "Pro" in html
    assert "No active subscription" in html
    result = ManageBilling.handle_subscribe(
        "pro", panel=panel, tenant=Tenant(1, "Acme", slug="acme"), user=OrbitUser.default()
    )
    assert result["ok"] is True
    html2 = ManageBilling.render(panel=panel, tenant=Tenant(1, "Acme", slug="acme"))
    assert "Current plan: Pro" in html2
    assert "Customer portal" not in html2

    class BoomProvider:
        def plans(self, *, tenant=None):
            raise RuntimeError("plans")

        def current_subscription(self, *, tenant=None):
            raise RuntimeError("sub")

        def portal_url(self, *, tenant=None):
            raise RuntimeError("portal")

        def subscribe(self, plan_id, *, tenant=None, user=None):
            raise RuntimeError("nope")

    boom = Panel.make("boom").path("b").billing_provider(BoomProvider())
    assert "No plans configured" in ManageBilling.render(panel=boom)
    assert ManageBilling.handle_subscribe("x", panel=boom)["ok"] is False

    class Mute:
        def plans(self, *, tenant=None):
            return None

        def current_subscription(self, *, tenant=None):
            return {"plan_id": "x"}

        def portal_url(self, *, tenant=None):
            return "/portal"

        def subscribe(self, plan_id, *, tenant=None, user=None):
            return "ok"

    mute = Panel.make("mute").path("m").billing_provider(Mute())
    html3 = ManageBilling.render(panel=mute)
    assert "Customer portal" in html3
    assert "Current plan: x" in html3
    assert ManageBilling.handle_subscribe("x", panel=mute)["ok"] is True

    class Empty:
        def get_billing_provider(self):
            return SimpleNamespace()

    assert ManageBilling.handle_subscribe("p", panel=Empty())["ok"] is False

    class DictPlans:
        def plans(self, *, tenant=None):
            return [{"id": "gold", "name": "Gold", "price_label": "USD 9", "description": "Nice"}]

        def current_subscription(self, *, tenant=None):
            return {"plan_id": "gold", "plan": {"name": "Gold"}}

        def portal_url(self, *, tenant=None):
            return None

    gold = Panel.make("gold").path("g").billing_provider(DictPlans())
    html4 = ManageBilling.render(panel=gold)
    assert "Gold" in html4 and "Current plan" in html4

    class WeirdPlans:
        def plans(self, *, tenant=None):
            return [SimpleNamespace(id="ns", name="Namespace")]

        def current_subscription(self, *, tenant=None):
            return {"plan": "Namespace"}

        def portal_url(self, *, tenant=None):
            return None

    weird = Panel.make("weird").path("w").billing_provider(WeirdPlans())
    html5 = ManageBilling.render(panel=weird)
    assert "Namespace" in html5

    class NamedCurrent:
        def plans(self, *, tenant=None):
            return []

        def current_subscription(self, *, tenant=None):
            return {"plan_id": "ns", "plan": "Namespace"}

        def portal_url(self, *, tenant=None):
            return None

    named = Panel.make("named").path("nm").billing_provider(NamedCurrent())
    assert "Current plan: ns" in ManageBilling.render(panel=named)

    empty_panel = Panel.make("none").path("n")
    assert "No plans configured" in ManageBilling.render(panel=empty_panel)
    assert ManageBilling.get_label() == "Billing"


def test_spa_mode_and_exceptions() -> None:
    panel = (
        Panel.make("admin")
        .path("admin")
        .login()
        .signup()
        .multi_factor_authentication(AppAuthentication())
        .spa()
        .spa_url_exceptions("/export", "/download")
        .spa_url_exceptions(["/print"])
    )
    assert panel.spa_enabled() is True
    exceptions = panel.spa_exceptions()
    assert "/admin/login" in exceptions
    assert "/admin/logout" in exceptions
    assert "/admin/register" in exceptions
    assert "/admin/mfa-challenge" in exceptions
    assert "/export" in exceptions and "/print" in exceptions
    shell = panel.render_shell("<p>Hi</p>", user=OrbitUser.default())
    assert 'data-orbit-spa="true"' in shell
    assert 'data-orbit-spa-root="/admin"' in shell
    assert panel.to_dict()["spa"] is True

    # SPA must swap breadcrumbs (sibling of main.or-content), not only main.
    from pathlib import Path

    spa_js = Path("packages/panels/src/almasix/orbit/resources/js/orbit.js").read_text(
        encoding="utf-8"
    )
    assert "_spaSwapBreadcrumbs" in spa_js
    assert 'nav.or-breadcrumbs' in spa_js

    off = Panel.make("off").path("/").login(False).spa(False)
    assert off.spa_enabled() is False
    assert 'data-orbit-spa="true"' not in off.render_shell("<p>x</p>")
    assert off.spa_exceptions() == []
    denied = Panel.make("no-bill").path("n").tenant_billing(False)
    assert denied.get_billing_provider() is None


def test_registry_lookup_by_path_and_domain() -> None:
    registry = PanelRegistry()
    admin = Panel.make("admin").path("admin").domain("admin.example.com")
    docs = Panel.make("docs").path("docs")
    root = Panel.make("root").path("/")
    registry.register(admin)
    registry.register(docs)
    registry.register(root)
    assert registry.get_by_path("admin") is admin
    assert registry.get_by_path("/admin/") is admin
    assert registry.get_by_path("docs") is docs
    assert registry.get_by_path("/") is root
    assert registry.get_by_path("missing") is None
    assert registry.get_by_path("") is root
    assert registry.get_by_domain("admin.example.com:443") is admin
    assert registry.get_by_domain("admin.example.com") is admin
    assert registry.get_by_domain("") is None
    assert registry.get_by_domain("other.test") is None


def test_mount_billing_route_get_and_post() -> None:
    panel = (
        Panel.make("admin")
        .path("admin")
        .middleware([], replace=True)
        .tenant(Tenancy().tenants([Tenant(1, "Acme", slug="acme")]).current(Tenant(1, "Acme", slug="acme")))
        .tenant_billing(True)
        .login(False)
    )
    router = Router()
    mount_panel(router, panel)
    route = next(r for r in router.routes if str(getattr(r, "route_name", "")).endswith("tenant.billing"))

    class _Req:
        def __init__(self, method: str = "GET", payload: dict | None = None, plan: str = "") -> None:
            self.method = method
            self.path = "/admin/billing"
            self.url = SimpleNamespace(path="/admin/billing")
            self._payload = payload or {}
            self._plan = plan

        def json(self) -> dict:
            return self._payload

        def input(self, name: str) -> str:
            return self._plan if name == "plan_id" else ""

    get_res = run(route.action(_Req()))
    body = getattr(get_res, "body", getattr(get_res, "content", get_res))
    raw = body.encode() if isinstance(body, str) else bytes(body)
    assert b"or-page-tenant-billing" in raw

    post_res = run(route.action(_Req(method="POST", payload={"plan_id": "pro"})))
    post_body = getattr(post_res, "body", getattr(post_res, "content", post_res))
    post_raw = post_body.encode() if isinstance(post_body, str) else bytes(post_body)
    assert b"Current plan" in post_raw

    run(route.action(_Req(method="POST", payload={})))
    run(route.action(_Req(method="POST", plan="starter")))

    class BoomPage(ManageBilling):
        @classmethod
        def handle_subscribe(cls, plan_id: str, **ctx: Any) -> dict[str, Any]:
            raise RuntimeError("boom")

    panel2 = (
        Panel.make("root")
        .path("/")
        .middleware([], replace=True)
        .tenant(True)
        .tenant_billing(BoomPage)
        .login(False)
    )
    router2 = Router()
    mount_panel(router2, panel2)
    route2 = next(r for r in router2.routes if str(getattr(r, "route_name", "")).endswith("tenant.billing"))
    run(route2.action(_Req(method="POST", payload={"plan": "pro"})))

    class AbsBill(ManageBilling):
        slug = "/billing"

    class EmptySlug(ManageBilling):
        @classmethod
        def get_slug(cls) -> str:
            return ""

    Panel.make("abs").path("admin").middleware([], replace=True).tenant(True).tenant_billing(AbsBill).login(
        False
    )
    abs_router = Router()
    mount_panel(
        abs_router,
        Panel.make("abs2").path("admin").middleware([], replace=True).tenant(True).tenant_billing(AbsBill).login(
            False
        ),
    )
    assert any("/billing" in str(r.uri or "") for r in abs_router.routes)

    empty_router = Router()
    mount_panel(
        empty_router,
        Panel.make("empty").path("/").middleware([], replace=True).tenant(True).tenant_billing(EmptySlug).login(
            False
        ),
    )
    assert any(str(r.uri or "") == "/" or str(r.uri or "").endswith("billing") for r in empty_router.routes)

    gated = (
        Panel.make("gated")
        .path("admin")
        .middleware([], replace=True)
        .login()
        .tenant(Tenancy().tenants([Tenant(1, "Acme", slug="acme")]))
        .tenant_billing(True)
    )
    gated_router = Router()
    mount_panel(gated_router, gated)
    gated_route = next(
        r for r in gated_router.routes if str(getattr(r, "route_name", "")).endswith("tenant.billing")
    )

    class _GateReq:
        def __init__(self) -> None:
            self.method = "GET"
            self.path = "/admin/billing"
            self.url = SimpleNamespace(path="/admin/billing")

    run(gated_route.action(_GateReq()))
