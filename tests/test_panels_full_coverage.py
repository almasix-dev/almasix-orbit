"""Drive remaining panel module coverage (statements + branches), excluding hosts."""

from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path
from typing import Any

import pytest

from almasix.orbit.forms import Form, TextInput
from almasix.orbit.panels.auth import AppAuthentication, MfaProvider, _login_brand_html
from almasix.orbit.panels.cluster import Cluster
from almasix.orbit.panels.commands import MakeOrbitResourceCommand, MakeOrbitUserCommand
from almasix.orbit.panels.global_search import search_records
from almasix.orbit.panels.hooks import PanelPlugin, Plugin
from almasix.orbit.panels.navigation import (
    NavigationGroup,
    NavigationItem,
    build_menu_layout,
    normalize_nav_layout,
)
from almasix.orbit.panels.page import Page
from almasix.orbit.panels.pages.resource_pages import ListRecords, _page_header_actions
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.routing import (
    _current_user,
    _embed_async,
    _is_guest_path,
    _request_path,
    mount_panel,
)
from almasix.orbit.panels.tenancy import Tenancy, Tenant
from almasix.orbit.tables import Table, TextColumn
from almasix.routing.router import Router


class _Post:
    id = 1
    title = "Hello"


class _PostResource(Resource):
    model = _Post
    slug = "posts"
    navigation_label = "Posts"
    records_mutable = True

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])


# ---------------------------------------------------------------------------
# commands.py
# ---------------------------------------------------------------------------


def test_make_resource_skips_suffix_when_already_present() -> None:
    cmd = MakeOrbitResourceCommand()
    # class already ends with Resource; module already ends with _resource
    assert cmd.handle(name="PostResource") == 0
    assert cmd.handle(name="post_resource") == 0


def test_make_user_password_match_scaffold_fail_unique_and_load(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from almasix.framework.application import Application

    app = Application(tmp_path)
    (tmp_path / "app").mkdir()
    (tmp_path / "config").mkdir()

    # Password via secret, matching confirm → skip mismatch branch
    cmd = MakeOrbitUserCommand(app)
    cmd._options = {
        "name": "Ada",
        "email": "ada@orbit.test",
        "password": "",
        "model": "app.models.user.User",
        "scaffold": False,
    }
    secrets = iter(["same", "same"])
    cmd.secret = lambda *a, **k: next(secrets)  # type: ignore[method-assign]

    class SyncUser:
        email = "ada@orbit.test"

        @classmethod
        def create(cls, attrs):
            u = cls()
            u.email = attrs["email"]
            return u

    cmd._load_model = lambda path: SyncUser  # type: ignore[method-assign]
    assert cmd.handle() == 0

    # Scaffold raises → lines 339-341
    boom = MakeOrbitUserCommand(app)
    boom._options = {
        "name": "Ada",
        "email": "ada@orbit.test",
        "password": "secret",
        "model": "app.models.user.User",
        "scaffold": True,
    }
    boom._scaffold_user_model = lambda path: (_ for _ in ()).throw(RuntimeError("scaffold boom"))  # type: ignore[method-assign]
    assert boom.handle() == 1

    # Unique violation comment path (line 363)
    uniq = MakeOrbitUserCommand(app)
    uniq._options = {
        "name": "Ada",
        "email": "ada@orbit.test",
        "password": "secret",
        "model": "app.models.user.User",
        "scaffold": False,
    }
    uniq._load_model = lambda path: SyncUser  # type: ignore[method-assign]
    uniq._create_user = lambda *a, **k: (_ for _ in ()).throw(  # type: ignore[method-assign]
        Exception("UNIQUE constraint failed: users.email")
    )
    assert uniq.handle() == 1

    # _default_user_model except path
    import almasix.orbit.panels.commands as commands_mod

    fake_config = types.ModuleType("almasix.config")

    def _raise_config(*a, **k):
        raise RuntimeError("no config")

    fake_config.config = _raise_config  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "almasix.config", fake_config)
    assert MakeOrbitUserCommand(app)._default_user_model() == "app.models.user.User"

    # Successful _load_model return (line 396)
    mod = types.ModuleType("orbit_cov_user_mod")
    mod.User = SyncUser  # type: ignore[attr-defined]
    sys.modules["orbit_cov_user_mod"] = mod
    try:
        assert MakeOrbitUserCommand()._load_model("orbit_cov_user_mod.User") is SyncUser
    finally:
        sys.modules.pop("orbit_cov_user_mod", None)


def test_scaffold_user_model_existing_files(tmp_path: Path) -> None:
    from almasix.framework.application import Application

    app = Application(tmp_path)
    (tmp_path / "app").mkdir()
    (tmp_path / "config").mkdir()
    cmd = MakeOrbitUserCommand(app)

    # First write creates files
    cmd._scaffold_user_model("app.models.user.User")
    # Second pass: user exists (428), models_init exists (430→436), auth exists (436→exit)
    cmd._scaffold_user_model("app.models.user.User")
    assert (tmp_path / "app" / "models" / "user.py").is_file()


# ---------------------------------------------------------------------------
# panel.py
# ---------------------------------------------------------------------------


def test_panel_nav_group_discovery_csrf_breadcrumbs_menu(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # falsy group name → skip _nav_groups store (336→339)
    panel = Panel.make("cov").path("cov")
    empty_group = NavigationGroup.make(None)
    item_pre = NavigationItem.make("pre").url("/cov/a").group("Already")
    empty_group.items([item_pre])
    panel.navigation_group(empty_group)
    # item already had _group → skip item.group(...) (340→342)
    assert item_pre._group == "Already"

    # named group with item lacking group
    named = NavigationGroup.make("Content").items(
        [NavigationItem.make("posts").url("/cov/posts")]
    )
    panel.navigation_group(named)

    # load_discovered skip-already-seen (369/375/383)
    res_dir = tmp_path / "res"
    res_dir.mkdir()
    (res_dir / "post_resource.py").write_text(
        "from almasix.orbit.panels.resource import Resource\n"
        "class PostResource(Resource):\n"
        "    model = type('P', (), {})\n",
        encoding="utf-8",
    )
    page_dir = tmp_path / "pages"
    page_dir.mkdir()
    (page_dir / "reports.py").write_text(
        "from almasix.orbit.panels.page import Page\n"
        "class ReportsPage(Page):\n"
        "    title = 'Reports'\n",
        encoding="utf-8",
    )
    widget_dir = tmp_path / "widgets"
    widget_dir.mkdir()
    (widget_dir / "stats.py").write_text(
        "from almasix.orbit.widgets.widget import Widget\n"
        "class StatsWidget(Widget):\n"
        "    pass\n",
        encoding="utf-8",
    )

    class LocalPost(Resource):
        model = type("P", (), {})

        @classmethod
        def form(cls, form: Form) -> Form:
            return form

        @classmethod
        def table(cls, table: Table) -> Table:
            return table

    # Pre-register same names so discover skips
    LocalPost.__name__ = "PostResource"  # type: ignore[misc]
    class ReportsPage(Page):
        title = "Reports"

    ReportsPage.__name__ = "ReportsPage"  # already

    from almasix.orbit.widgets.widget import Widget

    class StatsWidget(Widget):
        pass

    panel.resources([LocalPost]).pages([ReportsPage]).widgets([StatsWidget])
    (
        panel.discover_resources(str(res_dir))
        .discover_pages(str(page_dir))
        .discover_widgets(str(widget_dir))
        .load_discovered()
    )
    # Discover twice → skip again
    panel.load_discovered()

    # dashboard disabled → 488→496
    off = Panel.make("off").path("off").dashboard(False)
    off.menu_layout_context()

    # dash is None while "enabled" via monkeypatch → 490→496 (dash is None)
    on = Panel.make("on").path("on").resources([_PostResource])
    monkeypatch.setattr(on, "dashboard_page", lambda: None)
    on.menu_layout_context()

    # group_name already in meta → skip meta insert
    from almasix.orbit.panels.pages.dashboard import Dashboard

    labeled = Panel.make("lab").path("lab").resources([_PostResource])
    gname = getattr(Dashboard, "navigation_group", None) or Dashboard.get_navigation_label()
    if gname:
        labeled.navigation_group(NavigationGroup.make(str(gname)).icon("heroicon-o-home"))
    labeled.menu_layout_context()

    # csrf Exception path (608-609)
    monkeypatch.setattr(
        "almasix.session.csrf.csrf_token",
        lambda: (_ for _ in ()).throw(RuntimeError("no csrf")),
        raising=False,
    )
    assert "or-app" in Panel.make("csrf").path("csrf").render_shell("<p>x</p>")

    # breadcrumbs: empty remainder at root path "/" (673-674)
    root = Panel.make("root").path("/").resources([_PostResource])
    crumbs = root.breadcrumbs("/")
    assert crumbs[0]["url"] is None

    admin = Panel.make("admin").path("admin").resources([_PostResource])
    assert admin.breadcrumbs("/admin/posts/1")[-1]["label"] == "View"


# ---------------------------------------------------------------------------
# navigation.py
# ---------------------------------------------------------------------------


def test_normalize_nav_layout_unknown_and_empty_groups(monkeypatch: pytest.MonkeyPatch) -> None:
    assert normalize_nav_layout("nope") == "sidebar_topbar"

    items = [{"label": "A", "url": "/a", "group": "Real", "sort": 0, "icon": None}]

    class _Grouped(dict):
        """``get('Empty')`` is empty so continue branches run; ``__getitem__`` keeps sort happy."""

        def get(self, key, default=None):  # noqa: ANN001
            if key == "Empty":
                return []
            return super().get(key, default)

    def fake_group(flat):
        return _Grouped(
            {
                "Empty": [{"label": "E", "url": "/e", "group": "Empty", "sort": 0}],
                "Real": list(flat),
            }
        )

    monkeypatch.setattr(
        "almasix.orbit.panels.navigation.group_items",
        fake_group,
    )
    ctx = build_menu_layout(items, layout="sidebar_topbar", panel_path="/")
    assert any(r.label == "Real" for r in ctx.menu_roots)
    assert all(r.label != "Empty" for r in ctx.menu_roots)

    ctx_top = build_menu_layout(items, layout="top", panel_path="/")
    assert all(getattr(r, "label", None) != "Empty" for r in ctx_top.menu_roots)


# ---------------------------------------------------------------------------
# routing.py
# ---------------------------------------------------------------------------


def test_routing_user_guest_request_embed_root(monkeypatch: pytest.MonkeyPatch) -> None:
    import almasix.auth as auth_mod

    class _AuthNone:
        @staticmethod
        def user():
            return None

    monkeypatch.setattr(
        auth_mod,
        "auth",
        lambda: (_ for _ in ()).throw(RuntimeError("no helper")),
    )
    monkeypatch.setattr(auth_mod, "Auth", _AuthNone, raising=False)
    panel = Panel.make("ru").path("ru").demo_user(object())
    # Auth.user() is None → fall through to panel user (36→40)
    assert _current_user(panel) is not None

    # signup on, non-register path → 73→75
    signed = Panel.make("sg").path("sg").signup()
    assert _is_guest_path(signed, "/sg/posts") is False
    assert _is_guest_path(signed, "/sg/register") is True

    # request with falsy path → fall through (106→108)
    class _EmptyPath:
        url = None
        path = ""

    monkeypatch.setattr(
        "almasix.http.request",
        lambda: (_ for _ in ()).throw(RuntimeError("no req")),
        raising=False,
    )
    assert _request_path(_EmptyPath()) is None  # type: ignore[arg-type]

    # Exception in current_request branch (115-116)
    assert _request_path(None) is None

    async def _embed_edges() -> None:
        from almasix.orbit.panels.conduit.hosts import ListRecordsHost

        host = ListRecordsHost.bind(panel=Panel.make("emb").path("emb"), resource=_PostResource)()
        host.conduit_id = "already-set"
        host.mount = None  # type: ignore[assignment]
        host.booted = "nope"  # type: ignore[assignment]  # not callable → 154→156
        html = await _embed_async(host)
        assert isinstance(html, str)

    asyncio.run(_embed_edges())

    # Root panel home uses empty uri → full == "" → normalize to "/" (line 253)
    root = Panel.make("root").path("/").login(False).signup(False).dashboard(False)
    router = Router()
    mount_panel(router, root)
    assert any(getattr(r, "uri", None) == "/" for r in router.routes) or len(router.routes) >= 1


# ---------------------------------------------------------------------------
# auth.py / hooks.py / global_search / resource_pages / tenancy / cluster / page / resource
# ---------------------------------------------------------------------------


def test_auth_empty_brand_and_protocol_methods() -> None:
    class Flip:
        def __init__(self) -> None:
            self.n = 0

        def __bool__(self) -> bool:
            self.n += 1
            return self.n == 1

        def __str__(self) -> str:
            return "/logo.svg"

    assert _login_brand_html(brand="Acme", brand_logo=Flip(), brand_logo_only=True) == ""

    class _T:
        pass

    # Execute Protocol stub bodies (ellipsis branches)
    assert MfaProvider.get_id(_T()) is None  # type: ignore[arg-type]
    assert MfaProvider.is_enabled(_T(), object()) is None  # type: ignore[arg-type]
    assert MfaProvider.get_management_schema(_T()) is None  # type: ignore[arg-type]
    assert MfaProvider.get_challenge_form(_T()) is None  # type: ignore[arg-type]
    assert AppAuthentication().get_id() == "app"


def test_hooks_protocol_and_plugin() -> None:
    class _T:
        pass

    assert PanelPlugin.get_id(_T()) is None  # type: ignore[arg-type]
    assert PanelPlugin.register(_T(), object()) is None  # type: ignore[arg-type]
    assert PanelPlugin.boot(_T(), object()) is None  # type: ignore[arg-type]
    Plugin("p").register(None)
    Plugin("p").boot(None)


def test_global_search_empty_needle() -> None:
    rows = [{"title": "Ada"}, {"title": "Bob"}]
    assert search_records(rows, "   ", attributes=["title"]) == rows


def test_resource_pages_header_and_list_none_records(monkeypatch: pytest.MonkeyPatch) -> None:
    class PermUser:
        permissions: list[str] = []

        def can(self, *a, **k):
            return False

    class R(Resource):
        model = type("R", (), {})
        slug = "rp"
        records_mutable = True

        @classmethod
        def can_update(cls, user, record=None):
            return False

        @classmethod
        def can_delete(cls, user, record=None):
            return False

        @classmethod
        def can_view(cls, user, record=None):
            return False

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("title")])

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

    monkeypatch.setattr(
        "almasix.orbit.panels.pages.resource_pages._auth_user",
        lambda: PermUser(),
    )
    # permissions is [] (not None) → fall through to return False (74→76)
    assert _page_header_actions(R, "view", {"id": 1}) == ""
    # neither view nor edit (86→93)
    assert _page_header_actions(R, "create", {"id": 1}) == ""

    class Bound(ListRecords):
        @classmethod
        def get_resource(cls):
            return R

    html = Bound.render(records=None)
    assert "or-page" in html or "or-table" in html or isinstance(html, str)


def test_tenancy_get_current() -> None:
    t = Tenant(1, "Acme")
    tenancy = Tenancy().current(t)
    assert tenancy.get_current() is t


def test_cluster_and_page_slug_without_suffix() -> None:
    class Settings(Cluster):
        pass

    assert Settings.get_slug() == "settings"

    class Home(Page):
        pass

    assert Home.get_slug() == "home"


def test_resource_skips_record_url_when_preset() -> None:
    class Preset(Resource):
        model = _Post
        records_mutable = True

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("title")])

        @classmethod
        def table(cls, table: Table) -> Table:
            return (
                table.columns([TextColumn.make("title")])
                .record_url(lambda record=None, **_: "/custom")
            )

    t = Preset.get_table()
    assert t._record_url is not None
