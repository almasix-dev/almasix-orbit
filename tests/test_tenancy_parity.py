"""Multi-tenancy parity — Tenancy API, Panel.tenant, switcher, scoping, HasTenants."""

from __future__ import annotations

from typing import Any

import pytest
from almasix.orbit.panels import (
    EditTenantProfile,
    HasTenants,
    ManageBilling,
    Panel,
    RegisterTenant,
    Resource,
    Tenancy,
    Tenant,
)
from almasix.orbit.panels.conduit.hosts import ListRecordsHost, OrbitPageHost
from almasix.orbit.panels.pages.tenancy import EditTenantProfile as EditTenantProfilePage
from almasix.orbit.panels.pages.tenancy import RegisterTenant as RegisterTenantPage
from almasix.orbit.tables import Table
from almasix.orbit.tables.columns import TextColumn


class _Team:
    def __init__(self, id: int, name: str, slug: str, avatar_url: str | None = None) -> None:
        self.id = id
        self.name = name
        self.slug = slug
        self.avatar_url = avatar_url


class _TenantUser:
    def __init__(self, teams: list[_Team]) -> None:
        self.teams = teams

    def get_tenants(self, panel: Any = None) -> list[_Team]:
        return list(self.teams)

    def can_access_tenant(self, tenant: Any) -> bool:
        tid = getattr(tenant, "id", tenant)
        return any(t.id == tid or getattr(tenant, "slug", None) == t.slug for t in self.teams)


class _PostResource(Resource):
    slug = "posts"
    records: list[dict[str, Any]] = []

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)


def test_tenant_basics_and_from_model() -> None:
    t = Tenant(1, "Acme", slug="acme", avatar_url="/a.png")
    assert t.to_dict() == {
        "id": 1,
        "name": "Acme",
        "slug": "acme",
        "avatar_url": "/a.png",
    }
    from_obj = Tenant.from_model(_Team(2, "Beta", "beta", "/b.png"))
    assert from_obj.slug == "beta"
    assert from_obj.avatar_url == "/b.png"
    from_dict = Tenant.from_model({"id": 3, "name": "Gamma", "slug": "gamma"})
    assert from_dict.id == 3


def test_has_tenants_protocol() -> None:
    user = _TenantUser([_Team(1, "Acme", "acme")])
    assert isinstance(user, HasTenants)
    assert user.get_tenants(None)[0].slug == "acme"
    assert user.can_access_tenant(Tenant(1, "Acme", slug="acme"))


def test_tenancy_fluent_surface() -> None:
    tenancy = (
        Tenancy()
        .model(_Team)
        .ownership_relationship("team")
        .slug_attribute("slug")
        .name_attribute("name")
        .avatar_attribute("avatar_url")
        .registration(True)
        .profile(True)
        .billing(False)
        .tenants([Tenant(1, "Acme", slug="acme"), Tenant(2, "Beta", slug="beta")])
        .current(Tenant(1, "Acme", slug="acme"))
        .menu_items([{"label": "Invite", "url": "/invite"}])
        .tenant_route_prefix(True)
        .unique_middleware_key("admin")
        .tenant_middleware(["EnsureTenant"], is_persistent=True)
        .scope_using(lambda q, t: [r for r in q if r.get("tenant_id") == t.id])
        .associate_using(lambda rec, t: {**rec, "team_id": t.id})
    )
    assert tenancy.is_enabled()
    assert tenancy.get_tenant_model() is _Team
    assert tenancy.get_ownership_relationship() == "team"
    assert tenancy.get_slug_attribute() == "slug"
    assert tenancy.get_name_attribute() == "name"
    assert tenancy.get_avatar_attribute() == "avatar_url"
    assert tenancy.registration_enabled()
    assert tenancy.profile_enabled()
    assert not tenancy.billing_enabled()
    assert tenancy.registration_page() is RegisterTenantPage
    assert tenancy.profile_page() is EditTenantProfilePage
    assert tenancy.billing_page() is None
    assert tenancy.find_by_slug("beta").name == "Beta"  # type: ignore[union-attr]
    assert tenancy.find_by_slug("missing") is None
    assert tenancy.scope_name() == "orbit.tenancy.admin"
    assert tenancy.get_unique_middleware_key() == "admin"
    assert tenancy.get_tenant_middleware() == ["EnsureTenant"]
    assert tenancy.tenant_middleware_is_persistent()
    assert tenancy.get_tenant_route_prefix() is True
    assert tenancy.path_prefix_for("acme") == "acme"
    assert tenancy.route_prefix_segment() == ""
    rows = tenancy.scope_query([{"tenant_id": 1}, {"tenant_id": 2}])
    assert rows == [{"tenant_id": 1}]
    associated = tenancy.associate_record({"title": "Hi"})
    assert associated == {"title": "Hi", "team_id": 1}
    data = tenancy.to_dict()
    assert data["enabled"] is True
    assert data["model"] == "_Team"
    assert data["current"]["slug"] == "acme"


def test_tenancy_route_prefix_string_and_default_associate() -> None:
    tenancy = (
        Tenancy()
        .tenants([Tenant(9, "Zed", slug="zed")])
        .current(Tenant(9, "Zed", slug="zed"))
        .tenant_route_prefix("team")
        .ownership_relationship("org")
    )
    assert tenancy.path_prefix_for() == "team/zed"
    assert tenancy.route_prefix_segment() == "team"
    assert tenancy.associate_record({"x": 1}) == {"x": 1, "org_id": 9}
    obj = type("Rec", (), {})()
    tenancy.associate_record(obj)
    assert obj.org_id == 9  # type: ignore[attr-defined]


def test_tenancy_resolve_from_has_tenants() -> None:
    tenancy = Tenancy().model(_Team)
    user = _TenantUser([_Team(1, "Acme", "acme"), _Team(2, "Beta", "beta")])
    resolved = tenancy.resolve_tenants(user=user, panel=Panel.make("admin"))
    assert [t.slug for t in resolved] == ["acme", "beta"]


def test_render_switcher_and_menu() -> None:
    tenancy = (
        Tenancy()
        .tenants(
            [
                Tenant(1, "Acme", slug="acme", avatar_url="/a.png"),
                Tenant(2, "Beta", slug="beta"),
            ]
        )
        .current(Tenant(1, "Acme", slug="acme", avatar_url="/a.png"))
        .registration()
        .profile()
        .billing(True)
        .menu_items([{"label": "Members", "url": "/members"}])
    )
    panel = Panel.make("admin").path("admin")
    html = tenancy.render_switcher(panel=panel)
    assert "or-tenant-switcher" in html
    assert "or-tenant-switcher-btn" in html
    assert "or-tenant-menu" in html
    assert "or-tenant-option" in html
    assert "wire:model.live=\"tenant\"" in html
    assert "setTenant(" in html
    assert "Acme" in html
    assert 'src="/a.png"' in html
    menu = tenancy.render_menu(panel=panel)
    assert "Register" in menu
    assert "Tenant profile" in menu
    assert "Billing" in menu
    assert "Members" in menu
    assert tenancy.render_switcher() != ""
    empty = Tenancy()
    assert empty.render_switcher() == ""
    assert empty.render_menu() == ""


def test_panel_tenant_wiring() -> None:
    tenancy = (
        Tenancy()
        .model(_Team)
        .tenants([Tenant(1, "Acme", slug="acme")])
        .current(Tenant(1, "Acme", slug="acme"))
        .tenant_route_prefix(True)
    )
    panel = (
        Panel.make("admin")
        .path("admin")
        .tenant(tenancy)
        .tenant_registration(True)
        .tenant_profile(True)
        .tenant_billing(False)
        .tenant_middleware(["TenantGate"], is_persistent=True)
    )
    assert panel.get_tenancy() is tenancy
    assert panel.get_tenant().slug == "acme"  # type: ignore[union-attr]
    assert "TenantGate" in panel.get_middleware()
    assert panel.get_tenant_middleware() == ["TenantGate"]
    assert panel.to_dict()["tenancy"]["enabled"] is True

    panel2 = Panel.make("ops").tenant(_Team, ownership_relationship="org", slug_attribute="slug")
    assert panel2.get_tenancy().get_tenant_model() is _Team  # type: ignore[union-attr]
    assert panel2.get_tenancy().get_ownership_relationship() == "org"  # type: ignore[union-attr]

    panel3 = Panel.make("off").tenant(False)
    assert panel3.get_tenancy() is None
    assert panel3.get_tenant() is None


def test_panel_shell_includes_switcher() -> None:
    tenancy = (
        Tenancy()
        .tenants([Tenant(1, "Acme", slug="acme")])
        .current(Tenant(1, "Acme", slug="acme"))
    )
    panel = Panel.make("admin").path("admin").tenant(tenancy).brand_name("Orbit")
    shell = panel.render_shell("<div>hi</div>", user=_TenantUser([_Team(1, "Acme", "acme")]))
    assert "or-tenant-switcher" in shell

    panel_no_top = (
        Panel.make("side")
        .path("side")
        .tenant(tenancy)
        .topbar(False)
        .sidebar_navigation()
    )
    shell2 = panel_no_top.render_shell("<div>hi</div>", user=None)
    assert "or-tenant-switcher" in shell2 or "or-tenant-switcher-sidebar" in shell2


def test_resource_scope_to_tenant_flag() -> None:
    assert _PostResource.is_scoped_to_tenant is True
    assert _PostResource.is_tenant_scoped() is True
    _PostResource.scope_to_tenant(False)
    assert _PostResource.is_scoped_to_tenant is False
    assert _PostResource.is_tenant_scoped() is False
    _PostResource.scope_to_tenant(True)


def test_list_host_applies_scope_query() -> None:
    _PostResource.records = [
        {"id": 1, "title": "A", "tenant_id": 1},
        {"id": 2, "title": "B", "tenant_id": 2},
    ]
    tenancy = (
        Tenancy()
        .tenants([Tenant(1, "Acme", slug="acme")])
        .current(Tenant(1, "Acme", slug="acme"))
        .scope_using(lambda q, t: [r for r in q if r.get("tenant_id") == t.id])
    )
    panel = Panel.make("admin").tenant(tenancy)
    host_cls = ListRecordsHost.bind(panel=panel, resource=_PostResource)
    host = host_cls()
    host.setTenant("acme")
    host.mount()
    assert host.records == [{"id": 1, "title": "A", "tenant_id": 1}]
    host.setTenant("acme")
    assert panel.get_tenant().slug == "acme"  # type: ignore[union-attr]
    host.updatedTenant("acme")
    host.setTenant("beta")
    assert [row["id"] for row in host.records] == [1]
    beta = Tenant(2, "Beta", slug="beta")
    tenancy.tenants([Tenant(1, "Acme", slug="acme"), beta])
    host.page = 3
    host.selected = ["1"]
    host.setTenant("beta")
    assert [row["id"] for row in host.records] == [2]
    assert host.page == 1
    assert host.selected == []

    _PostResource.scope_to_tenant(False)
    host2 = host_cls()
    host2.mount()
    assert len(host2.records) == 2
    _PostResource.scope_to_tenant(True)
    _PostResource.records = []


def test_register_and_profile_page_stubs() -> None:
    assert issubclass(RegisterTenant, RegisterTenantPage) or RegisterTenant is RegisterTenantPage
    html = RegisterTenant.render()
    assert "or-page-tenant-register" in html
    assert RegisterTenant.get_label() == "Register tenant"

    class CustomReg(RegisterTenant):
        @classmethod
        def handle_registration(cls, data: dict[str, Any], **ctx: Any) -> Any:
            return Tenant(99, data.get("name", "X"), slug="x")

    assert CustomReg.handle_registration({"name": "X"}).id == 99

    with pytest.raises(NotImplementedError):
        RegisterTenant.handle_registration({})

    html2 = EditTenantProfile.render(tenant=Tenant(1, "Acme", slug="acme"))
    assert "or-page-tenant-profile" in html2
    assert "Acme" in html2

    class CustomProfile(EditTenantProfile):
        @classmethod
        def handle_save(cls, data: dict[str, Any], **ctx: Any) -> Any:
            return data

    assert CustomProfile.handle_save({"name": "N"}) == {"name": "N"}
    with pytest.raises(NotImplementedError):
        EditTenantProfile.handle_save({})


def test_resource_tenant_path_prefix() -> None:
    class R(Resource):
        slug = "items"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

    R._panel_path = "/admin"  # type: ignore[attr-defined]
    R._tenant_path = "acme"  # type: ignore[attr-defined]
    assert R.get_url_path_prefix() == "/admin/acme"
    pages = R.get_pages()
    assert pages["index"] == "/admin/acme/items"


def test_orbit_page_host_set_tenant() -> None:
    tenancy = Tenancy().tenants([Tenant(1, "Acme", slug="acme")]).current(None)
    panel = Panel.make("admin").tenant(tenancy)

    class _Host(OrbitPageHost):
        pass

    host = _Host.bind(panel=panel, resource=_PostResource)()
    host.setTenant("acme")
    assert tenancy.get_current().slug == "acme"  # type: ignore[union-attr]
    host._sync_tenant_from_panel()
    assert host.tenant == "acme"


def test_tenancy_disable_and_billing_custom_page() -> None:
    class BillingPage(EditTenantProfile):
        slug = "billing"
        title = "Billing"

    tenancy = Tenancy().billing(BillingPage)
    assert tenancy.billing_enabled()
    assert tenancy.billing_page() is BillingPage
    tenancy.disable()
    assert not tenancy.is_enabled()


def test_package_exports() -> None:
    from almasix.orbit import panels as panels_pkg

    assert panels_pkg.Tenancy is Tenancy
    assert panels_pkg.Tenant is Tenant
    assert panels_pkg.HasTenants is HasTenants
    assert panels_pkg.RegisterTenant is RegisterTenant
    assert panels_pkg.EditTenantProfile is EditTenantProfile
    assert panels_pkg.ManageBilling is ManageBilling
    assert panels_pkg.ManageBilling is ManageBilling


def test_tenancy_edge_branches() -> None:
    from almasix.orbit.panels.tenancy import _avatar_html, _resolve_tenancy_page

    assert Tenancy().find_by_slug("") is None
    assert Tenancy().find_by_slug(None) is None
    assert Tenancy().path_prefix_for("x") == ""
    assert Tenancy().associate_record({"a": 1}) == {"a": 1}
    assert Tenancy().billing(True).billing_page() is ManageBilling
    assert Tenancy().billing("nope").billing_page() is ManageBilling  # type: ignore[arg-type]
    assert Tenancy().registration(False).registration_page() is None
    assert _resolve_tenancy_page(False, default_cls=RegisterTenant) is None
    assert _resolve_tenancy_page(True, default_cls=RegisterTenant) is RegisterTenant
    assert _resolve_tenancy_page(RegisterTenant, default_cls=EditTenantProfile) is RegisterTenant
    assert _resolve_tenancy_page("x", default_cls=RegisterTenant) is RegisterTenant  # type: ignore[arg-type]
    assert _avatar_html(None).startswith('<span class="or-tenant-avatar"')
    assert "?" in _avatar_html(Tenant(1, "", slug="x"))

    class _NoPanelUser:
        def get_tenants(self) -> list[Tenant]:
            return [Tenant(1, "Solo", slug="solo")]

        def can_access_tenant(self, tenant: Any) -> bool:
            return False

    resolved = Tenancy().resolve_tenants(user=_NoPanelUser())
    assert resolved == []
    assert Tenancy().resolve_tenants(user=object()) == []
    assert Tenancy().resolve_tenants(user=None) == []

    class _Renderable:
        def render(self) -> str:
            return '<a class="or-tenant-menu-item">Custom</a>'

    menu = (
        Tenancy()
        .menu_items([_Renderable(), "plain"])
        .render_menu()
    )
    assert "Custom" in menu
    assert "plain" in menu

    switcher = (
        Tenancy()
        .tenants([Tenant(1, "Acme", slug="acme")])
        .render_switcher()
    )
    assert "Acme" in switcher

    class _Frozen:
        __slots__ = ()

    frozen = _Frozen()
    tenancy = Tenancy().current(Tenant(1, "A", slug="a")).ownership_relationship("team")
    assert tenancy.associate_record(frozen) is frozen


def test_page_form_render_branches() -> None:
    class _Form:
        def render(self, state: Any = None, **ctx: Any) -> str:
            return '<form id="f"></form>'

    class WithForm(RegisterTenant):
        @classmethod
        def form(cls, form: Any = None) -> Any:
            return _Form()

    assert "id=\"f\"" in WithForm.render()
    assert "id=\"f\"" in RegisterTenant.render(form=_Form())
    assert "hello" in RegisterTenant.render(form="hello")
    assert EditTenantProfile.get_label() == "Tenant profile"
    assert "id=\"f\"" in EditTenantProfile.render(form=_Form())
    assert "x" in EditTenantProfile.render(form="x")
    assert "Acme" in EditTenantProfile.render(tenant={"name": "Acme"})
    assert "or-page-tenant-profile" in EditTenantProfile.render(tenant=object())


def test_panel_ensure_tenancy_and_stamp() -> None:
    panel = Panel.make("ensure").tenant_registration(True)
    assert panel.get_tenancy() is not None
    assert panel.get_tenant_middleware() == []
    panel2 = Panel.make("mw-none")
    assert panel2.get_tenant_middleware() == []

    tenancy = (
        Tenancy()
        .tenants([Tenant(1, "Acme", slug="acme")])
        .current(Tenant(1, "Acme", slug="acme"))
        .tenant_route_prefix("team")
        .tenant_middleware(["web"], is_persistent=False)
    )
    panel3 = (
        Panel.make("stamp")
        .path("admin")
        .resources([_PostResource])
        .pages([RegisterTenant])
        .tenant(tenancy)
    )
    panel3._stamp_tenant_paths(Tenant(1, "Acme", slug="acme"))
    assert getattr(_PostResource, "_tenant_path", "") == "team/acme"
    assert "web" in panel3.get_middleware()

    shell = (
        Panel.make("side2")
        .path("side2")
        .tenant(tenancy)
        .topbar(False)
        .sidebar_navigation()
        .render_shell("<div>x</div>")
    )
    assert "or-tenant-switcher-sidebar" in shell

    empty_html = Panel.make("empty-sw").tenant(Tenancy().model(_Team))._render_topbar_end()
    assert "or-tenant-switcher" not in empty_html


def test_resource_and_page_url_prefix_root() -> None:
    class R(Resource):
        slug = "items"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

    R._panel_path = "/"  # type: ignore[attr-defined]
    R._tenant_path = ""  # type: ignore[attr-defined]
    # Root panel path is normalized to empty prefix (same as pre-tenancy).
    assert R.get_url_path_prefix() == ""

    class P(RegisterTenant):
        pass

    P._panel_path = "/admin"  # type: ignore[attr-defined]
    P._tenant_path = "acme"  # type: ignore[attr-defined]
    assert P.get_url_path_prefix() == "/admin/acme"
    P._panel_path = "/"  # type: ignore[attr-defined]
    P._tenant_path = ""  # type: ignore[attr-defined]
    assert P.get_url_path_prefix() == ""


def test_host_bind_tenant_path_and_create_associate() -> None:
    from almasix.orbit.panels.conduit.hosts import CreateRecordHost

    tenancy = (
        Tenancy()
        .tenants([Tenant(1, "Acme", slug="acme")])
        .current(Tenant(1, "Acme", slug="acme"))
        .tenant_route_prefix(True)
        .associate_using(lambda rec, t: {**rec, "tenant_id": t.id})
    )
    panel = Panel.make("assoc").tenant(tenancy)
    _PostResource.records = []
    _PostResource.records_mutable = True  # type: ignore[attr-defined]
    host_cls = CreateRecordHost.bind(panel=panel, resource=_PostResource)
    assert getattr(_PostResource, "_tenant_path", "") == "acme"
    host = host_cls()
    host.mount(tenant="acme", data={"title": "T"})
    host.create()
    assert any(r.get("tenant_id") == 1 for r in _PostResource.records)
    _PostResource.records = []

    # Host without panel tenancy
    bare = OrbitPageHost.bind(panel=Panel.make("bare"), resource=_PostResource)()
    bare.setTenant("nope")
    bare._sync_tenant_from_panel()
    assert bare._apply_tenant_scope([{"id": 1}]) == [{"id": 1}]

    class _NoScoped(Resource):
        slug = "ns"
        is_scoped_to_tenant = False
        records = [{"id": 1, "tenant_id": 9}]

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

        @classmethod
        def get_records(cls):
            return list(cls.records)

    scoped_panel = Panel.make("ns").tenant(
        Tenancy()
        .current(Tenant(1, "A", slug="a"))
        .scope_using(lambda q, t: [r for r in q if r["tenant_id"] == t.id])
    )
    h = ListRecordsHost.bind(panel=scoped_panel, resource=_NoScoped)()
    h.mount()
    assert len(h.records) == 1


def test_routing_tenant_helpers_and_mount() -> None:
    import asyncio

    from almasix.orbit.panels.routing import (
        _apply_tenant_slug,
        _tenant_path_prefix,
        make_panel_page_action,
        mount_panel,
    )
    from almasix.routing.router import Router

    tenancy = (
        Tenancy()
        .tenants([Tenant(1, "Acme", slug="acme"), Tenant(2, "Beta", slug="beta")])
        .current(Tenant(1, "Acme", slug="acme"))
        .tenant_route_prefix(True)
        .registration(True)
        .profile(True)
    )
    panel = (
        Panel.make("tenroute")
        .path("admin")
        .login(False)
        .tenant(tenancy)
        .resources([_PostResource])
        .pages([EditTenantProfile])
    )
    user = _TenantUser([_Team(1, "Acme", "acme"), _Team(2, "Beta", "beta")])
    _apply_tenant_slug(panel, None, user)
    _apply_tenant_slug(panel, "beta", user)
    assert panel.get_tenant().slug == "beta"  # type: ignore[union-attr]

    class _DenyUser(_TenantUser):
        def can_access_tenant(self, tenant: Any) -> bool:
            return False

    before = panel.get_tenant()
    _apply_tenant_slug(panel, "acme", _DenyUser([_Team(1, "Acme", "acme")]))
    assert panel.get_tenant() is before

    panel_no = Panel.make("no-t")
    assert _tenant_path_prefix(panel_no) == ""
    assert _tenant_path_prefix(panel) == "{tenant}"

    # Resolve via HasTenants when find_by_slug misses configured list
    tenancy2 = Tenancy().model(_Team)
    panel_u = Panel.make("u").tenant(tenancy2)
    _apply_tenant_slug(panel_u, "acme", user)
    assert panel_u.get_tenant().slug == "acme"  # type: ignore[union-attr]
    _apply_tenant_slug(panel_u, "missing", user)

    router = Router()
    mount_panel(router, panel)
    uris = [getattr(r, "uri", "") for r in router.routes]
    assert any("{tenant}" in u for u in uris)
    assert any(u.endswith("/new") or "/new" in u for u in uris)

    class _Req:
        def __init__(self, path: str) -> None:
            self.url = type("U", (), {"path": path})()
            self.path = path

    host_cls = ListRecordsHost.bind(panel=panel, resource=_PostResource)
    action = make_panel_page_action(panel, host_cls)

    async def _run_actions() -> None:
        await action(_Req("/admin/acme/posts"), tenant="acme")
        edit = make_panel_page_action(panel, host_cls, pass_record_id=True)
        await edit(_Req("/admin/acme/posts/1"), "1", tenant="acme")
        # Invoke registered tenant register/profile actions
        for route in router.routes:
            name = str(getattr(route, "route_name", "") or "")
            fn = getattr(route, "action", None)
            if not callable(fn):
                continue
            if name.endswith("tenant.register") or name.endswith("tenant.profile"):
                await fn(_Req("/admin/new"), tenant="acme")
            if name.endswith("home.tenant"):
                await fn(_Req("/admin/acme"), tenant="acme")
            if ".page." in name:
                await fn(_Req("/admin/acme/profile"), tenant="acme")

    asyncio.run(_run_actions())


def test_remaining_coverage_branches() -> None:
    import asyncio

    from almasix.orbit.panels.conduit.hosts import CreateRecordHost
    from almasix.orbit.panels.routing import _apply_tenant_slug, mount_panel
    from almasix.orbit.panels.tenancy import _attr
    from almasix.routing.router import Router

    assert _attr({"a": 1}, None) is None

    html = Tenancy().current(Tenant(1, "Only", slug="only")).render_switcher()
    assert "Only" in html
    assert "or-tenant-option" not in html

    tenancy = Tenancy().current(Tenant(1, "A", slug="a")).ownership_relationship("tenant")
    assert tenancy.associate_record({"tenant_id": 99}) == {"tenant_id": 99}

    unbound = OrbitPageHost()
    unbound.setTenant("x")
    unbound._sync_tenant_from_panel()
    assert unbound._apply_tenant_scope([1]) == [1]

    tenancy2 = Tenancy().tenants([Tenant(1, "A", slug="a")])
    panel = Panel.make("edges").tenant(tenancy2)
    host = OrbitPageHost.bind(panel=panel, resource=_PostResource)()
    host.setTenant("missing")
    host.tenant = "a"
    host._sync_tenant_from_panel()
    assert tenancy2.get_current().slug == "a"  # type: ignore[union-attr]

    class _FlagOnly(Resource):
        slug = "flag"
        is_scoped_to_tenant = False
        records = [{"id": 1}]

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

        @classmethod
        def get_records(cls):
            return list(cls.records)

    h = ListRecordsHost.bind(
        panel=Panel.make("flag").tenant(
            Tenancy().current(Tenant(1, "A", slug="a")).scope_using(lambda q, t: [])
        ),
        resource=_FlagOnly,
    )()
    h.mount(tenant="a")
    assert h.records == [{"id": 1}]

    class WithProfileForm(EditTenantProfile):
        @classmethod
        def form(cls, form: Any = None) -> Any:
            class _F:
                def render(self, state=None, **ctx):
                    return "<form id='pf'></form>"

            return _F()

    assert "pf" in WithProfileForm.render()

    _PostResource.records = []
    _PostResource.records_mutable = True  # type: ignore[misc]
    t = (
        Tenancy()
        .tenants([Tenant(1, "A", slug="a")])
        .current(Tenant(1, "A", slug="a"))
    )
    p = Panel.make("cr").tenant(t)
    ch = CreateRecordHost.bind(panel=p, resource=_PostResource)()
    ch.mount(data={"title": "N"})
    ch.create()
    assert _PostResource.records[-1].get("tenant_id") == 1
    _PostResource.records = []

    _PostResource.scope_to_tenant(False)
    ch2 = CreateRecordHost.bind(panel=p, resource=_PostResource)()
    ch2.mount(data={"title": "N2"})
    ch2.create()
    assert "tenant_id" not in _PostResource.records[-1]
    _PostResource.scope_to_tenant(True)
    _PostResource.records = []

    p3 = Panel.make("kw").tenant(_Team, ownership_relationship="org", slug_attribute="slug")
    assert p3.get_tenancy().get_ownership_relationship() == "org"  # type: ignore[union-attr]
    assert p3.get_tenancy().get_slug_attribute() == "slug"  # type: ignore[union-attr]

    t4 = Tenancy().tenant_route_prefix(True).tenants([Tenant(7, "X", slug="x")])
    p4 = Panel.make("idfall").resources([_PostResource]).tenant(t4)
    p4._stamp_tenant_paths(type("T", (), {"id": 7})())
    assert "7" in getattr(_PostResource, "_tenant_path", "")

    t5 = (
        Tenancy()
        .tenants([Tenant(1, "Acme", slug="acme")])
        .current(Tenant(1, "Acme", slug="acme"))
    )
    shell = (
        Panel.make("sb")
        .path("sb")
        .tenant(t5)
        .topbar(False)
        .sidebar_navigation()
        .render_shell("<div/>")
    )
    assert "or-tenant-switcher-sidebar" in shell

    t6 = Tenancy().profile(True).tenants([Tenant(1, "A", slug="a")]).current(
        Tenant(1, "A", slug="a")
    )
    gated = Panel.make("gated").path("g").login(True).tenant(t6)
    router = Router()
    mount_panel(router, gated)

    class _Req:
        def __init__(self, path: str) -> None:
            self.url = type("U", (), {"path": path})()
            self.path = path

    async def _call() -> None:
        for route in router.routes:
            name = str(getattr(route, "route_name", "") or "")
            if name.endswith("tenant.profile"):
                await route.action(_Req("/g/profile"))

    asyncio.run(_call())

    t7 = Tenancy().registration(False).profile(False).model(_Team)
    mount_panel(Router(), Panel.make("noreg").path("nr").login(False).tenant(t7))

    class _NoStamp:
        def get_tenancy(self):
            return Tenancy().tenants([Tenant(1, "A", slug="a")])

        def get_tenant(self):
            return None

    # stamp attribute missing → skip callable stamp
    _apply_tenant_slug(_NoStamp(), "a")  # type: ignore[arg-type]


def test_final_branch_coverage() -> None:
    import asyncio
    from types import SimpleNamespace

    from almasix.orbit.panels.conduit.hosts import CreateRecordHost
    from almasix.orbit.panels.routing import mount_panel
    from almasix.routing.router import Router

    # is_tenant_scoped shadowed by bool → hit is_scoped_to_tenant ClassVar check
    class _Odd(Resource):
        slug = "odd"
        is_tenant_scoped = False  # type: ignore[assignment,misc]
        is_scoped_to_tenant = False
        records = [{"id": 1, "tenant_id": 9}]

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

        @classmethod
        def get_records(cls):
            return list(cls.records)

    h = ListRecordsHost.bind(
        panel=Panel.make("odd").tenant(
            Tenancy().current(Tenant(1, "A", slug="a")).scope_using(lambda q, t: [])
        ),
        resource=_Odd,
    )()
    h.mount()
    assert h.records == [{"id": 1, "tenant_id": 9}]

    # res is None path in _apply_tenant_scope
    host = OrbitPageHost.bind(panel=Panel.make("nr").tenant(Tenancy().current(Tenant(1, "A", slug="a"))), resource=_PostResource)()
    assert host._apply_tenant_scope([{"id": 1}], resource=None) == [{"id": 1}]

    # find_by_slug miss while syncing tenant string
    t = Tenancy().tenants([Tenant(1, "A", slug="a")])
    host2 = OrbitPageHost.bind(panel=Panel.make("miss").tenant(t), resource=_PostResource)()
    host2.tenant = "nope"
    host2._sync_tenant_from_panel()

    # stamp not callable
    class _Panelish:
        def get_tenancy(self):
            return None

    p = Panel.make("stampstr").tenant(Tenancy().tenants([Tenant(1, "A", slug="a")]))
    p._stamp_tenant_paths = "nope"  # type: ignore[method-assign,assignment]
    host3 = OrbitPageHost.bind(panel=p, resource=_PostResource)()
    host3.setTenant("a")

    # associate_record object already has FK set
    obj = SimpleNamespace(tenant_id=5)
    Tenancy().current(Tenant(1, "A", slug="a")).associate_record(obj)
    assert obj.tenant_id == 5

    # Panel.tenant without optional kwargs (false branches)
    assert Panel.make("plain").tenant(_Team).get_tenancy().get_tenant_model() is _Team

    # Stamp tenant with empty slug/id → path_prefix_for(None)
    t2 = Tenancy().tenant_route_prefix(True)
    p2 = Panel.make("emptyid").resources([_PostResource]).tenant(t2)
    p2._stamp_tenant_paths(SimpleNamespace(slug="", id=""))

    # Sidebar empty switcher branch
    shell = (
        Panel.make("empty-side")
        .path("es")
        .tenant(Tenancy().model(_Team))
        .topbar(False)
        .sidebar_navigation()
        .render_shell("<div/>")
    )
    assert "or-tenant-switcher-sidebar" not in shell

    # Auth-gated tenant register action (line 604)
    t3 = Tenancy().registration(True).profile(True)
    gated = Panel.make("reggate").path("rg").login(True).tenant(t3)
    router = Router()
    mount_panel(router, gated)

    class _Req:
        def __init__(self, path: str) -> None:
            self.url = type("U", (), {"path": path})()
            self.path = path

    async def _gate() -> None:
        for route in router.routes:
            name = str(getattr(route, "route_name", "") or "")
            if name.endswith("tenant.register"):
                result = await route.action(_Req("/rg/new"))
                assert result is not None

    asyncio.run(_gate())

    # ORM create associate path
    class _FakeModel:
        @classmethod
        async def create(cls, payload):
            return SimpleNamespace(id=1, **payload)

        @classmethod
        async def all(cls):
            return []

        @classmethod
        async def find(cls, pk):
            return None

    class _OrmRes(Resource):
        slug = "orms"
        model = _FakeModel
        records_mutable = True

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

        @classmethod
        def _uses_orm_model(cls) -> bool:
            return True

    async def _orm_create() -> None:
        panel = Panel.make("orm").tenant(
            Tenancy().current(Tenant(3, "O", slug="o")).ownership_relationship("tenant")
        )
        host = CreateRecordHost.bind(panel=panel, resource=_OrmRes)()
        host.data = {"title": "orm"}
        await host._create_orm(_FakeModel, _OrmRes)

    asyncio.run(_orm_create())


def test_last_partial_branches() -> None:
    import asyncio

    from almasix.orbit.panels.conduit.hosts import CreateRecordHost

    # sync with no current and empty tenant string
    t = Tenancy().tenants([Tenant(1, "A", slug="a")])
    host = OrbitPageHost.bind(panel=Panel.make("emptyt").tenant(t), resource=_PostResource)()
    host.tenant = ""
    host._sync_tenant_from_panel()

    # _apply_tenant_scope with no resource ClassVar
    panel = Panel.make("nors").tenant(Tenancy().current(Tenant(1, "A", slug="a")))
    bare = OrbitPageHost()
    type(bare)._panel = panel
    type(bare)._resource = None
    assert bare._apply_tenant_scope([{"x": 1}]) == [{"x": 1}]

    # ORM create when resource opts out of tenant scope
    class _FakeModel:
        @classmethod
        async def create(cls, payload):
            return type("R", (), {"id": 1, **payload})()

    class _OrmOptOut(Resource):
        slug = "ormout"
        model = _FakeModel
        records_mutable = True
        is_scoped_to_tenant = False

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

        @classmethod
        def is_tenant_scoped(cls) -> bool:
            return False

    async def _run() -> None:
        p = Panel.make("ormout").tenant(Tenancy().current(Tenant(3, "O", slug="o")))
        h = CreateRecordHost.bind(panel=p, resource=_OrmOptOut)()
        h.data = {"title": "x"}
        await h._create_orm(_FakeModel, _OrmOptOut)

    asyncio.run(_run())

    # stamp with tenant=None while route prefix enabled
    t2 = Tenancy().tenant_route_prefix(True).tenants([Tenant(1, "A", slug="a")])
    Panel.make("stampnone").resources([_PostResource]).tenant(t2)._stamp_tenant_paths(None)
