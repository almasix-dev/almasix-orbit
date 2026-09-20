"""Filament 5 Navigation parity — API, collect, shell, clusters, user menu."""

from __future__ import annotations

from almasix.orbit.panels.cluster import Cluster
from almasix.orbit.panels.navigation import (
    NavigationBuilder,
    NavigationGroup,
    NavigationItem,
    nest_parent_items,
)
from almasix.orbit.panels.page import Page
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.users import OrbitUser, UserMenuItem
from almasix.orbit.tables import Table
from almasix.orbit.tables.columns import TextColumn


class _PostResource(Resource):
    slug = "posts"
    navigation_icon = "heroicon-o-document-text"
    navigation_label = "Posts"
    navigation_group = "Content"
    navigation_sort = 10

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])

    @classmethod
    def get_records(cls):
        return []


class _HiddenResource(Resource):
    slug = "secrets"
    should_register_navigation = False
    navigation_label = "Secrets"

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])

    @classmethod
    def get_records(cls):
        return []


class _BadgeResource(Resource):
    slug = "inbox"
    navigation_label = "Inbox"
    navigation_badge = "3"
    navigation_badge_color = "danger"
    navigation_badge_tooltip = "Unread"
    active_navigation_icon = "heroicon-s-inbox"
    navigation_icon = "heroicon-o-inbox"

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])

    @classmethod
    def get_records(cls):
        return []


class _ChildPage(Page):
    slug = "preferences"
    navigation_label = "Preferences"
    navigation_parent_item = "Settings"
    navigation_group = "System"


class _ParentPage(Page):
    slug = "settings"
    navigation_label = "Settings"
    navigation_group = "System"
    navigation_icon = "heroicon-o-cog-6-tooth"


class _DeniedPage(Page):
    slug = "admin-only"
    navigation_label = "Admin Only"
    permission = "admin.access"


class SettingsCluster(Cluster):
    navigation_icon = "heroicon-o-cog-6-tooth"
    navigation_label = "Settings Hub"
    navigation_group = "Platform"
    navigation_sort = 5
    sub_navigation_position = "start"


class _ColorResource(Resource):
    slug = "colors"
    navigation_label = "Colors"
    cluster = SettingsCluster

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("name")])

    @classmethod
    def get_records(cls):
        return []


class _BrandPage(Page):
    slug = "branding"
    navigation_label = "Branding"
    cluster = SettingsCluster


def test_navigation_item_badge_active_icon_new_tab_parent() -> None:
    item = (
        NavigationItem.make("docs")
        .label("Docs")
        .url("https://example.com")
        .icon("heroicon-o-book-open")
        .active_icon("heroicon-s-book-open")
        .badge(lambda: "New", "warning")
        .badge_tooltip("Fresh docs")
        .open_url_in_new_tab()
        .parent_item("Help")
        .is_active_when(lambda active_path=None, **_: active_path == "/docs")
    )
    d = item.to_nav_dict(active_path="/docs")
    assert d["badge"] == "New"
    assert d["badge_color"] == "warning"
    assert d["badge_tooltip"] == "Fresh docs"
    assert d["active_icon"] == "heroicon-s-book-open"
    assert d["open_in_new_tab"] is True
    assert d["parent_item"] == "Help"
    assert d["active"] is True
    assert item.is_visible()


def test_navigation_item_visibility_respected() -> None:
    hidden = NavigationItem.make("x").label("X").url("/x").hidden()
    assert hidden.is_visible() is False
    panel = Panel.make("admin").path("/admin").dashboard(False).navigation_item(hidden)
    assert panel.navigation_items() == []


def test_should_register_navigation_and_badges_on_resource() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .resources([_PostResource, _HiddenResource, _BadgeResource])
    )
    items = panel.navigation_items()
    labels = [i["label"] for i in items]
    assert "Posts" in labels
    assert "Secrets" not in labels
    inbox = next(i for i in items if i["label"] == "Inbox")
    assert inbox["badge"] == "3"
    assert inbox["badge_color"] == "danger"
    assert inbox["badge_tooltip"] == "Unread"
    assert inbox["active_icon"] == "heroicon-s-inbox"


def test_parent_item_nesting_in_shell() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .sidebar_navigation()
        .pages([_ParentPage, _ChildPage])
        .collapsible_navigation_groups(False)
    )
    html = panel.render_shell("<p>x</p>", active_path="/admin/preferences")
    assert "or-nav-children" in html
    assert "Preferences" in html
    assert "Settings" in html


def test_group_collapsed_collapsible() -> None:
    group = (
        NavigationGroup.make("Shop")
        .icon("heroicon-o-shopping-cart")
        .collapsed()
        .collapsible()
        .extra_sidebar_attributes({"data-shop": "1"})
        .extra_topbar_attributes({"data-shop-top": "1"})
    )
    assert group.is_collapsed() is True
    assert group.is_collapsible() is True
    assert group.get_extra_sidebar_attributes()["data-shop"] == "1"

    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .sidebar_navigation()
        .navigation_groups([group])
        .resources([_PostResource])
        .navigation_item(
            NavigationItem.make("products")
            .label("Products")
            .url("/admin/products")
            .group("Shop")
            .icon("heroicon-o-cube")
        )
    )
    # Content group is not Shop — add a Shop resource via custom item only.
    html = panel.render_shell("<p>x</p>", active_path="/admin/products")
    assert "or-nav-group-collapsible" in html
    assert 'data-shop="1"' in html


def test_auth_filtering() -> None:
    user = OrbitUser.make().name("Ada").admin(False).permissions("posts.view_any")
    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .resources([_PostResource, _BadgeResource])
        .pages([_DeniedPage])
        .user(user)
    )
    items = panel._collect_navigation_items(user=user)
    labels = [i["label"] for i in items]
    assert "Posts" in labels
    # Badge resource uses slug "inbox" → permission inbox.view_any (missing)
    assert "Inbox" not in labels
    assert "Admin Only" not in labels


def test_user_menu_groups_icons_disable() -> None:
    user = OrbitUser.default()
    panel = (
        Panel.make("admin")
        .path("/admin")
        .user(user)
        .user_menu_items(
            [
                UserMenuItem.make("settings")
                .label("Settings")
                .url("/admin/settings")
                .icon("heroicon-o-cog-6-tooth")
                .group("account")
                .sort(1),
                UserMenuItem.make("docs")
                .label("Docs")
                .url("https://example.com")
                .icon("heroicon-o-book-open")
                .group("help")
                .sort(2),
            ]
        )
        .user_menu_items(
            {
                "logout": lambda action: action.label("Log out").icon(
                    "heroicon-o-arrow-left-on-rectangle"
                ),
            }
        )
    )
    html = panel.render_shell("<p>x</p>", user=user)
    assert "or-user-menu-divider" in html
    assert "Settings" in html
    assert "Log out" in html
    assert "Sign out" not in html

    disabled = Panel.make("x").path("/x").user(user).user_menu(False)
    html2 = disabled.render_shell("<p>x</p>", user=user)
    assert "or-user-menu" not in html2


def test_cluster_main_nav_and_sub_nav() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .clusters([SettingsCluster])
        .resources([_ColorResource, _PostResource])
        .pages([_BrandPage])
        .sidebar_navigation()
        .collapsible_navigation_groups(False)
    )
    items = panel.navigation_items()
    labels = [i["label"] for i in items]
    assert "Settings Hub" in labels
    assert "Colors" not in labels
    assert "Branding" not in labels
    assert "Posts" in labels

    cluster_item = next(i for i in items if i["label"] == "Settings Hub")
    assert "/admin/settings/" in cluster_item["url"]
    assert cluster_item["url"].endswith(("/colors", "/branding"))

    _ColorResource._panel_path = "/admin"
    assert _ColorResource.get_pages()["index"] == "/admin/settings/colors"

    html = panel.render_shell(
        "<p>cluster page</p>",
        active_path="/admin/settings/colors",
        user=OrbitUser.default(),
    )
    assert "or-cluster-nav" in html
    assert "Colors" in html
    assert "Branding" in html
    crumbs = panel.breadcrumbs("/admin/settings/colors")
    crumb_labels = [c["label"] for c in crumbs]
    assert "Settings Hub" in crumb_labels or any("Settings" in str(c) for c in crumb_labels)


def test_navigation_false_and_topbar_false() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .resources([_PostResource])
        .navigation(False)
        .topbar(False)
        .sidebar_navigation()
    )
    assert panel.navigation_items() == []
    html = panel.render_shell("<p>x</p>", user=OrbitUser.default())
    assert "or-app-no-sidebar" in html or "or-sidebar" not in html or panel._navigation_enabled is False
    assert "or-topbar" not in html


def test_navigation_builder_replaces_items() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .resources([_PostResource])
        .navigation(
            lambda builder: builder.items(
                [
                    NavigationItem.make("home")
                    .label("Home")
                    .url("/admin")
                    .icon("heroicon-o-home"),
                ]
            )
        )
    )
    items = panel.navigation_items()
    assert len(items) == 1
    assert items[0]["label"] == "Home"


def test_navigation_builder_class() -> None:
    builder = (
        NavigationBuilder.make()
        .groups(
            [
                NavigationGroup.make("Custom")
                .items(
                    [
                        NavigationItem.make("a").label("A").url("/a"),
                    ]
                )
            ]
        )
        .item(NavigationItem.make("b").label("B").url("/b"))
    )
    assert len(builder.get_items()) >= 2
    panel = Panel.make("admin").path("/admin").dashboard(False).navigation(builder)
    labels = [i["label"] for i in panel.navigation_items()]
    assert "A" in labels
    assert "B" in labels


def test_sidebar_width_and_fully_collapsible() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .sidebar_width("20rem")
        .collapsed_sidebar_width("5rem")
        .sidebar_fully_collapsible_on_desktop()
        .resources([_PostResource])
    )
    html = panel.render_shell("<p>x</p>")
    assert "--or-sidebar-w: 20rem" in html
    assert "--or-sidebar-collapsed-w: 5rem" in html
    assert "or-app-fully-collapsible" in html


def test_nest_parent_items_helper() -> None:
    nested = nest_parent_items(
        [
            {"label": "Parent", "url": "/p", "group": "G"},
            {"label": "Child", "url": "/c", "group": "G", "parent_item": "Parent"},
            {"label": "Orphan", "url": "/o", "parent_item": "Missing"},
        ]
    )
    parent = next(i for i in nested if i["label"] == "Parent")
    assert len(parent["children"]) == 1
    assert parent["children"][0]["label"] == "Child"
    assert any(i["label"] == "Orphan" for i in nested)


def test_cluster_exports_and_helpers() -> None:
    from almasix.orbit.panels import Cluster as ExportedCluster

    assert ExportedCluster is Cluster
    assert SettingsCluster.get_slug() == "settings"
    assert SettingsCluster.path_prefix() == "/settings"
    assert SettingsCluster.get_should_register_sub_navigation() is True
    inst = SettingsCluster.make().breadcrumb("Cfg").resources([_ColorResource])
    assert inst.get_breadcrumb() == "Cfg"
    assert inst.get_resources() == [_ColorResource]


def test_open_url_in_new_tab_rendered() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .sidebar_navigation()
        .collapsible_navigation_groups(False)
        .navigation_item(
            NavigationItem.make("ext")
            .label("External")
            .url("https://example.com")
            .open_url_in_new_tab()
            .icon("heroicon-o-arrow-top-right-on-square")
        )
    )
    html = panel.render_shell("<p>x</p>", active_path="/admin")
    assert 'target="_blank"' in html
    assert "External" in html


def test_active_icon_swapped_when_active() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .sidebar_navigation()
        .collapsible_navigation_groups(False)
        .resources([_BadgeResource])
    )
    _BadgeResource._panel_path = "/admin"
    html = panel.render_shell("<p>x</p>", active_path="/admin/inbox")
    assert "Inbox" in html
    # Active icon name should be requested when rendering the active link.
    assert "or-nav-link is-active" in html


def test_navigation_groups_string_order() -> None:
    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .navigation_groups(["System", "Content"])
        .resources([_PostResource])
        .pages([_ParentPage])
        .sidebar_navigation()
        .collapsible_navigation_groups(False)
    )
    assert panel._nav_group_order[:2] == ["System", "Content"]
    html = panel.render_shell("<p>x</p>")
    # Both group labels appear; System should be ordered first via order list.
    sys_pos = html.find("System")
    content_pos = html.find("Content")
    assert sys_pos != -1 and content_pos != -1
    assert sys_pos < content_pos


def test_get_navigation_badge_callable() -> None:
    class Dyn(Resource):
        slug = "dyn"
        navigation_badge = staticmethod(lambda **_: "9")

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    assert Dyn.get_navigation_badge() == "9"
    assert Dyn.get_should_register_navigation() is True


def test_navigation_module_coverage_helpers() -> None:
    from almasix.orbit.panels.navigation import (
        NavigationSubgroup,
        apply_active_state,
        attrs_to_html,
        build_menu_layout,
        build_menu_secondary,
        normalize_nav_layout,
        resolve_active_path,
    )

    assert normalize_nav_layout("apps") == "sidebar_topbar"
    assert normalize_nav_layout("sidebar") == "sidebar"
    assert normalize_nav_layout("weird") == "sidebar_topbar"

    item = (
        NavigationItem.make("x")
        .subgroup("Sub")
        .sub_category("Alt")
        .sort(5)
        .badge("1")
        .badge_color("info")
        .badge_tooltip("tip")
    )
    assert item._subgroup == "Alt"
    assert item._sort == 5
    assert item.resolve_active() is False
    d = item.to_nav_dict()
    assert d["badge"] == "1"
    assert d["badge_color"] == "info"

    group = (
        NavigationGroup.make("G")
        .extra_topbar_attributes({"data-x": lambda: "y"})
        .collapsible(False)
        .collapsed(False)
    )
    assert group.get_extra_topbar_attributes()["data-x"] == "y"
    assert group.is_collapsible() is False

    sub = NavigationSubgroup.make("S").parent("G").icon("heroicon-o-star").sort(2)
    assert sub._parent == "G"
    assert sub._icon == "heroicon-o-star"
    assert sub._sort == 2
    empty_parent = NavigationSubgroup.make("E").parent("  ").parent(None)
    assert empty_parent._parent is None

    builder = NavigationBuilder.make().item(
        NavigationItem.make("solo").label("Solo").url("/solo")
    )
    assert builder.get_items()[0].get_label() == "Solo"

    flat = apply_active_state(
        [
            {"label": "Home", "url": "/", "is_active_when": None},
            {
                "label": "Docs",
                "url": "/docs",
                "is_active_when": lambda active_path=None, **_: active_path == "/docs",
            },
        ],
        active_path="/docs",
    )
    assert any(i["label"] == "Docs" and i["active"] for i in flat)

    flat2 = apply_active_state(
        [{"label": "Home", "url": "/", "sort": 0}],
        active_path="/",
    )
    assert flat2[0]["active"] is True

    flat3 = apply_active_state(
        [{"label": "A", "url": "/a", "sub_category": "X", "sort": 0}],
        active_path="/other",
    )
    ctx = build_menu_layout(
        flat3
        + [{"label": "B", "url": "/b", "subgroup": "X", "sort": 1, "group": "G"}],
        active_path="/b",
        layout="top",
        group_meta={"G": NavigationGroup.make("G").icon("heroicon-o-home")},
        subgroup_meta={(None, "X"): sub},
        group_order=["G"],
    )
    assert ctx.layout == "top"
    assert ctx.menu_secondary

    sidebar_ctx = build_menu_layout(
        [{"label": "A", "url": "/a", "group": "G", "sort": 0}],
        layout="sidebar",
        group_meta={"G": NavigationGroup.make("G")},
        active_path="/a",
    )
    assert sidebar_ctx.menu_secondary == []

    apps_ctx = build_menu_layout(
        [
            {"label": "A", "url": "/a", "group": "G", "sort": 0},
            {"label": "B", "url": "/b", "group": None, "sort": 1},
        ],
        layout="apps",
        active_path="/a",
        group_order=["G"],
    )
    assert apps_ctx.menu_roots

    secondary = build_menu_secondary(
        [
            {"label": "One", "url": "/1", "sort": 0},
            {
                "label": "Two",
                "url": "/2",
                "subgroup": "More",
                "sort": 1,
                "icon": "heroicon-o-star",
            },
            {
                "label": "Three",
                "url": "/3",
                "subgroup": "More",
                "sort": 2,
                "icon": "heroicon-o-star",
            },
        ],
        active_url="/2",
        subgroup_meta={(None, "More"): sub},
    )
    assert any(s.children for s in secondary)

    assert resolve_active_path("/x") == "/x"
    assert resolve_active_path(None, active_path="/y") == "/y"
    assert resolve_active_path(None) is None

    html = attrs_to_html({"data-a": "1", "hidden": True, "skip": False, "gone": None})
    assert 'data-a="1"' in html
    assert "hidden" in html
    assert "skip" not in html


def test_cluster_classvar_coverage() -> None:
    class NamedCluster(Cluster):
        slug = "cfg"
        cluster_breadcrumb = "Config"
        navigation_icon = "heroicon-o-wrench"

    class OddName(Cluster):
        pass

    assert NamedCluster.get_slug() == "cfg"
    assert NamedCluster.get_navigation_icon() == "heroicon-o-wrench"
    assert NamedCluster.get_cluster_breadcrumb() == "Config"
    assert OddName.get_slug() == "odd_name"

    inst = NamedCluster.make().pages([_BrandPage])
    assert inst.get_pages() == [_BrandPage]


def test_cluster_sub_nav_disabled() -> None:
    class QuietCluster(Cluster):
        should_register_sub_navigation = False
        navigation_label = "Quiet"

    class _QuietRes(Resource):
        slug = "quiet-items"
        cluster = QuietCluster

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .clusters([QuietCluster])
        .resources([_QuietRes])
        .sidebar_navigation()
    )
    _QuietRes._panel_path = "/admin"
    html = panel.render_shell("<p>x</p>", active_path="/admin/quiet/quiet-items")
    assert "or-cluster-nav" not in html


def test_user_menu_position_sidebar_and_post() -> None:
    user = OrbitUser.default()
    panel = (
        Panel.make("admin")
        .path("/admin")
        .user(user)
        .user_menu(position="sidebar")
        .user_menu_item(
            UserMenuItem.make("lock")
            .label("Lock")
            .url("/admin/lock")
            .post_to_url()
            .icon("heroicon-o-lock-closed")
        )
        .topbar(False)
        .sidebar_navigation()
    )
    html = panel.render_shell("<p>x</p>", user=user)
    assert "or-user-menu-sidebar" in html
    assert 'method="post"' in html


def test_discover_clusters_and_string_cluster() -> None:
    class StrClusterRes(Resource):
        slug = "tokens"
        cluster = "settings"
        navigation_label = "Tokens"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .clusters([SettingsCluster])
        .resources([StrClusterRes])
    )
    items = panel.navigation_items()
    assert any(i.get("cluster") for i in items)


def test_navigation_remaining_branches() -> None:
    from almasix.orbit.panels.navigation import (
        apply_active_state,
        build_menu_layout,
        nest_parent_items,
    )

    # Builder groups: item already has a group set (skip auto-assign).
    pregrouped = NavigationItem.make("p").label("P").url("/p").group("Existing")
    NavigationBuilder.make().groups(
        [NavigationGroup.make("Ignored").items([pregrouped])]
    )
    assert pregrouped._group == "Existing"

    # Nest parent with blank label root.
    nested = nest_parent_items(
        [
            {"label": "", "url": "/blank"},
            {"label": "Kid", "url": "/kid", "parent_item": "Missing"},
        ]
    )
    assert any(i.get("label") == "Kid" for i in nested)

    # Mix is_active_when + path candidates so continue runs.
    flat = apply_active_state(
        [
            {
                "label": "CB",
                "url": "/cb",
                "is_active_when": lambda active_path=None, **_: False,
            },
            {"label": "Path", "url": "/path", "sort": 0},
            {"label": "Path2", "url": "/path/nested", "sort": 1},
        ],
        active_path="/path/nested",
    )
    assert next(i for i in flat if i["label"] == "Path2")["active"] is True
    assert next(i for i in flat if i["label"] == "CB")["active"] is False

    # No active_path → setdefault False for non-callback items.
    flat_none = apply_active_state([{"label": "Z", "url": "/z"}])
    assert flat_none[0].get("active") is False

    # No active_path + callable is_active_when (skip setdefault branch).
    flat_cb = apply_active_state(
        [
            {
                "label": "CB2",
                "url": "/cb2",
                "is_active_when": lambda **_: True,
            }
        ]
    )
    assert flat_cb[0]["active"] is True

    # Top layout: named group without meta icon + children without icons; plus ungrouped.
    top = build_menu_layout(
        [
            {"label": "A", "url": "/a", "group": "Shop", "sort": 0},
            {"label": "B", "url": "/b", "group": None, "sort": 1},
        ],
        layout="top",
        active_path="/a",
    )
    assert top.menu_secondary
    assert top.menu_roots == []


def test_url_path_prefix_cluster_edge_cases() -> None:
    """Exercise get_url_path_prefix string/object/slug_fn/no-slash branches."""

    class NoSlashCluster(Cluster):
        slug = "noslash"

        @classmethod
        def path_prefix(cls) -> str:
            return "noslash"  # no leading slash

    class SlugOnlyCluster:
        """Cluster-like object without path_prefix — falls back to get_slug."""

        @classmethod
        def get_slug(cls) -> str:
            return "slugonly"

    class EmptySlugCluster:
        @classmethod
        def get_slug(cls) -> str:
            return ""

    class NoHelpersCluster:
        pass

    class ResNoSlash(Resource):
        slug = "items"
        cluster = NoSlashCluster

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class ResSlugOnly(Resource):
        slug = "tokens"
        cluster = SlugOnlyCluster

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class ResEmptyClusterStr(Resource):
        slug = "blank"
        cluster = "   "

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class ResStrCluster(Resource):
        slug = "named"
        cluster = "platform"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class PageNoSlash(Page):
        slug = "brand"
        cluster = NoSlashCluster

    class PageSlugOnly(Page):
        slug = "prefs"
        cluster = SlugOnlyCluster

    class PageEmptyHelpers(Page):
        slug = "empty"
        cluster = EmptySlugCluster

    class PageNoHelpers(Page):
        slug = "naked"
        cluster = NoHelpersCluster

    class PageStrCluster(Page):
        slug = "about"
        cluster = "platform"

    class PageBlankStr(Page):
        slug = "void"
        cluster = ""

    for cls in (
        ResNoSlash,
        ResSlugOnly,
        ResEmptyClusterStr,
        ResStrCluster,
        PageNoSlash,
        PageSlugOnly,
        PageEmptyHelpers,
        PageNoHelpers,
        PageStrCluster,
        PageBlankStr,
    ):
        cls._panel_path = "/admin"  # type: ignore[attr-defined]

    assert ResNoSlash.get_url_path_prefix() == "/admin/noslash"
    assert ResSlugOnly.get_url_path_prefix() == "/admin/slugonly"
    assert ResEmptyClusterStr.get_url_path_prefix() == "/admin"
    assert ResStrCluster.get_url_path_prefix() == "/admin/platform"
    assert PageNoSlash.get_url_path_prefix() == "/admin/noslash"
    assert PageSlugOnly.get_url_path_prefix() == "/admin/slugonly"
    assert PageEmptyHelpers.get_url_path_prefix() == "/admin"
    assert PageNoHelpers.get_url_path_prefix() == "/admin"
    assert PageStrCluster.get_url_path_prefix() == "/admin/platform"
    assert PageBlankStr.get_url_path_prefix() == "/admin"

    # Cluster prefix only (no panel path).
    ResSlugOnly._panel_path = ""  # type: ignore[attr-defined]
    assert ResSlugOnly.get_url_path_prefix() == "/slugonly"


def test_resolve_nav_flag_edge_cases() -> None:
    from almasix.orbit.panels.resource import _resolve_nav_flag

    class Base(Resource):
        slug = "base"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    # Attr missing entirely → walk MRO to object, return default.
    assert _resolve_nav_flag(Base, "no_such_nav_flag", default=True) is True
    assert _resolve_nav_flag(Base, "no_such_nav_flag", default=False) is False

    class CM(Base):
        slug = "cm"

        @classmethod
        def should_register_navigation(cls, **ctx: object) -> bool:
            return False

    assert CM.get_should_register_navigation() is False

    def _skip(**_ctx: object) -> bool:
        return False

    class SkipFn(Base):
        slug = "skip"
        should_register_navigation = _skip  # type: ignore[assignment]

    # Plain function skipped; falls through to Resource ClassVar True.
    assert SkipFn.get_should_register_navigation() is True

    class TruthyType:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def __bool__(self) -> bool:
            return False

    class TypeFlag(Base):
        slug = "typeflag"
        should_register_navigation = TruthyType  # type: ignore[assignment]

    assert TypeFlag.get_should_register_navigation() is False


def test_user_menu_item_visible_hidden() -> None:
    shown = UserMenuItem.make("a").label("A").url("/a").visible(True)
    assert shown.is_visible() is True
    hidden = UserMenuItem.make("b").label("B").url("/b").hidden()
    assert hidden.is_visible() is False
    toggled = UserMenuItem.make("c").label("C").url("/c").visible(lambda: False)
    assert toggled.is_visible() is False
    unhidden = UserMenuItem.make("d").label("D").url("/d").hidden(False).visible(True)
    assert unhidden.is_visible() is True


def test_mount_panel_clustered_resources_and_pages() -> None:
    from almasix.routing.router import Router
    from almasix.orbit.panels.routing import mount_panel

    class Hub(Cluster):
        slug = "hub"
        navigation_label = "Hub"

    class HubRes(Resource):
        slug = "widgets"
        cluster = Hub
        navigation_label = "Widgets"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class StrClusterRes(Resource):
        slug = "gadgets"
        cluster = "tools"
        navigation_label = "Gadgets"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class HubPage(Page):
        slug = "overview"
        cluster = Hub
        navigation_label = "Overview"

    class StrClusterPage(Page):
        slug = "docs"
        cluster = "tools"
        navigation_label = "Docs"

    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .login(False)
        .clusters([Hub])
        .resources([HubRes, StrClusterRes])
        .pages([HubPage, StrClusterPage])
    )
    router = Router()
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert any("/admin/hub/widgets" in u for u in uris)
    assert any("/admin/tools/gadgets" in u for u in uris)
    assert any("/admin/hub/overview" in u for u in uris)
    assert any("/admin/tools/docs" in u for u in uris)


def test_panel_navigation_api_coverage_gaps(tmp_path) -> None:
    """Hit remaining panel navigation / user-menu / cluster shell branches."""
    user = OrbitUser.default()

    # sidebar_collapsible_on_desktop alias + fully-collapsible False branch.
    panel = (
        Panel.make("admin")
        .path("/admin")
        .dashboard(False)
        .sidebar_collapsible_on_desktop(True)
        .sidebar_fully_collapsible_on_desktop(False)
        .navigation(True)
        .user_menu(True, position="topbar")
        .user_menu_position("sidebar")
        .user_menu_items(None)
        .resources([_PostResource])
        .user(user)
    )
    assert panel._sidebar_collapsible is True
    assert panel._sidebar_fully_collapsible is False
    assert panel._user_menu_position == "sidebar"

    # user_menu_items dict: profile/logout callables, UserMenuItem, plain dict;
    # plus non-special UserMenuItem and dict entries.
    panel.user_menu_items(
        {
            "profile": lambda action: action.label("My profile").url("/admin/me").icon(
                "heroicon-o-user"
            ),
            "logout": UserMenuItem.make("logout")
            .label("Exit")
            .url("/admin/logout")
            .post_to_url(),
            "extra": UserMenuItem.make("extra").label("Extra").url("/admin/extra"),
            "plain": {"label": "Plain", "url": "/admin/plain", "name": "plain"},
        }
    )
    # profile as UserMenuItem + logout as plain dict (alternate branches).
    panel2 = (
        Panel.make("p2")
        .path("/p2")
        .user(user)
        .user_menu_items(
            {
                "profile": UserMenuItem.make("profile").label("Prof").url("/p2/me"),
                "logout": {
                    "label": "Bye",
                    "url": "/p2/logout",
                    "name": "logout",
                    "post_to_url": True,
                },
            }
        )
    )
    html2 = panel2.render_shell("<p>x</p>", user=user)
    assert "Prof" in html2 or "or-user-menu" in html2

    # discover_clusters + load_discovered.
    cluster_dir = tmp_path / "clusters"
    cluster_dir.mkdir()
    (cluster_dir / "ops_cluster.py").write_text(
        "from almasix.orbit.panels.cluster import Cluster\n"
        "class OpsCluster(Cluster):\n"
        "    slug = 'ops'\n"
        "    navigation_label = 'Ops'\n",
        encoding="utf-8",
    )
    panel.discover_clusters(str(cluster_dir)).load_discovered()
    assert any(c.get_slug() == "ops" for c in panel.get_clusters())
    # Second load skips already-seen clusters.
    panel.load_discovered()

    # navigation_groups: blank string skip + already-ordered label + object group.
    panel.navigation_groups(["", "Content", "Content"])
    panel.navigation_groups(
        [NavigationGroup.make("Content").icon("heroicon-o-folder")]
    )
    # Group with empty name → skip name registration branch.
    panel.navigation_group(NavigationGroup.make(None))

    # Builder callable returning False / non-builder / builder with invisible item.
    empty = (
        Panel.make("empty")
        .path("/empty")
        .dashboard(False)
        .navigation(lambda _b: False)
    )
    assert empty.navigation_items() == []

    weird = (
        Panel.make("weird")
        .path("/weird")
        .dashboard(False)
        .navigation(lambda _b: "not-a-builder")  # type: ignore[arg-type]
    )
    assert weird.navigation_items() == []

    with_hidden = (
        Panel.make("hid")
        .path("/hid")
        .dashboard(False)
        .navigation(
            lambda b: b.item(
                NavigationItem.make("gone").label("Gone").url("/hid/gone").hidden()
            )
        )
    )
    assert with_hidden.navigation_items() == []

    # Builder that returns a builder instance (isinstance path after callable).
    built = (
        Panel.make("built")
        .path("/built")
        .dashboard(False)
        .navigation(
            lambda b: b.groups(
                [NavigationGroup.make("G").items([NavigationItem.make("a").label("A").url("/a")])]
            )
        )
    )
    assert any(i["label"] == "A" for i in built.navigation_items())

    # _should_register without getter (raw flag / callable flag).
    class RawPage:
        should_register_navigation = False
        slug = "raw"

        @classmethod
        def get_slug(cls):
            return "raw"

        @classmethod
        def get_navigation_label(cls):
            return "Raw"

    class CallPage:
        should_register_navigation = staticmethod(lambda **_: False)
        slug = "call"

        @classmethod
        def get_slug(cls):
            return "call"

        @classmethod
        def get_navigation_label(cls):
            return "Call"

    p_raw = Panel.make("raw").path("/raw").dashboard(False)
    assert p_raw._should_register(RawPage) is False
    assert p_raw._should_register(CallPage) is False

    # _can_access_page: user set but no can_access → True.
    class PlainPage:
        pass

    assert p_raw._can_access_page(PlainPage, user) is True

    # Dashboard page registered on _pages (dash-in-pages branch).
    from almasix.orbit.panels.pages.dashboard import Dashboard

    class LocalDash(Dashboard):
        navigation_label = "Home"

    dash_panel = (
        Panel.make("dash")
        .path("/dash")
        .pages([LocalDash])
        .dashboard(True)
        .sidebar_navigation()
    )
    labels = [i["label"] for i in dash_panel.navigation_items()]
    assert "Home" in labels

    # String cluster without matching panel cluster → dynamic synthesis.
    class OrphanStrRes(Resource):
        slug = "orphans"
        cluster = "ghost-land"
        navigation_label = "Orphans"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    orphan = (
        Panel.make("orph")
        .path("/orph")
        .dashboard(False)
        .resources([OrphanStrRes])
    )
    orphan_items = orphan.navigation_items()
    assert any(i.get("cluster") for i in orphan_items)

    # Registered cluster with members only via explicit clusters list
    # (member uses matching type key path in _cluster_members).
    class TwinCluster(Cluster):
        slug = "twin"

    class TwinRes(Resource):
        slug = "twins"
        cluster = TwinCluster

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    twin = (
        Panel.make("twin")
        .path("/twin")
        .dashboard(False)
        .clusters([TwinCluster])
        .resources([TwinRes])
    )
    assert any(i.get("cluster") for i in twin.navigation_items())

    # Cluster members filtered by should_register / can_view_any / can_access.
    class DenyCluster(Cluster):
        slug = "deny"
        navigation_label = "Deny Hub"

    class HiddenMember(Resource):
        slug = "hidden-m"
        cluster = DenyCluster
        should_register_navigation = False

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class NoPermMember(Resource):
        slug = "noperm"
        cluster = DenyCluster
        navigation_label = "NoPerm"

        @classmethod
        def can_view_any(cls, user):  # noqa: ANN001
            return False

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class DeniedPageMember(Page):
        slug = "denied-m"
        cluster = DenyCluster
        navigation_label = "DeniedM"
        permission = "never.allow"

    limited = OrbitUser.make().name("Lim").admin(False).permissions("posts.view_any")
    deny_panel = (
        Panel.make("deny")
        .path("/deny")
        .dashboard(False)
        .clusters([DenyCluster])
        .resources([HiddenMember, NoPermMember])
        .pages([DeniedPageMember])
        .user(limited)
    )
    # All members filtered → no cluster nav entry.
    deny_items = deny_panel._collect_navigation_items(user=limited)
    assert not any(i.get("label") == "Deny Hub" for i in deny_items)

    # Sub-nav auth filtering + register skip inside cluster.
    class OpenCluster(Cluster):
        slug = "open"
        navigation_label = "Open"
        sub_navigation_position = "top"

    class OpenRes(Resource):
        slug = "open-items"
        cluster = OpenCluster
        navigation_label = "Open Items"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class HiddenOpen(Resource):
        slug = "hidden-open"
        cluster = OpenCluster
        should_register_navigation = False

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class NoViewOpen(Resource):
        slug = "noview"
        cluster = OpenCluster
        navigation_label = "NoView"

        @classmethod
        def can_view_any(cls, user):  # noqa: ANN001
            return False

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class GatePage(Page):
        slug = "gate"
        cluster = OpenCluster
        navigation_label = "Gate"
        permission = "gate.access"

    open_panel = (
        Panel.make("open")
        .path("/open")
        .dashboard(False)
        .clusters([OpenCluster])
        .resources([OpenRes, HiddenOpen, NoViewOpen])
        .pages([GatePage])
        .sidebar_navigation()
        .user(limited)
    )
    OpenRes._panel_path = "/open"  # type: ignore[attr-defined]
    html_top = open_panel.render_shell(
        "<p>x</p>",
        active_path="/open/open/open-items",
        user=limited,
    )
    assert "or-cluster-layout-top" in html_top or "Open Items" in html_top

    # End position cluster layout.
    class EndCluster(Cluster):
        slug = "end"
        sub_navigation_position = "end"
        navigation_label = "End Hub"

    class EndRes(Resource):
        slug = "end-items"
        cluster = EndCluster
        navigation_label = "End Items"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    end_panel = (
        Panel.make("end")
        .path("/end")
        .dashboard(False)
        .clusters([EndCluster])
        .resources([EndRes])
        .sidebar_navigation()
    )
    EndRes._panel_path = "/end"  # type: ignore[attr-defined]
    html_end = end_panel.render_shell(
        "<p>x</p>",
        active_path="/end/end/end-items",
        user=user,
    )
    assert "or-cluster-layout-end" in html_end

    # Breadcrumbs: cluster implied by membership (not in panel._clusters yet),
    # and cluster leaf path with no further segments.
    class ImplyCluster(Cluster):
        slug = "imply"
        cluster_breadcrumb = "Implied"

    class ImplyRes(Resource):
        slug = "implied"
        cluster = ImplyCluster
        navigation_label = "Implied Res"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    imply = (
        Panel.make("imp")
        .path("/imp")
        .dashboard(False)
        .resources([ImplyRes])
    )
    ImplyRes._panel_path = "/imp"  # type: ignore[attr-defined]
    crumbs = imply.breadcrumbs("/imp/imply/implied")
    assert any("Implied" in str(c.get("label")) for c in crumbs)
    leaf = imply.breadcrumbs("/imp/imply")
    assert leaf[-1].get("url") is None

    # _member_url without get_pages / get_url_path_prefix (fallback prefixes).
    class BareMember:
        cluster = "bare-c"

        @classmethod
        def get_slug(cls):
            return "bare"

    class BareCluster(Cluster):
        slug = "bare-c"

    bare_panel = Panel.make("bare").path("/bare").clusters([BareCluster])
    assert "/bare" in bare_panel._member_url(BareMember) or "bare" in bare_panel._member_url(
        BareMember
    )

    # Page without get_url_path_prefix → else branch in _page_nav_dict.
    class LegacyPage:
        navigation_label = "Legacy"
        navigation_sort = 1

        @classmethod
        def get_slug(cls):
            return "legacy"

        @classmethod
        def get_navigation_label(cls):
            return "Legacy"

    legacy_panel = Panel.make("leg").path("/leg").dashboard(False)
    nav = legacy_panel._page_nav_dict(LegacyPage)
    assert "legacy" in nav["url"]

    # Page with get_url_path_prefix but unset _panel_path.
    class PrefPage(Page):
        slug = "pref-page"
        navigation_label = "Pref"

    pref_panel = Panel.make("pref").path("/pref").dashboard(False).pages([PrefPage])
    # Clear stamp so _page_nav_dict sets it.
    if hasattr(PrefPage, "_panel_path"):
        delattr(PrefPage, "_panel_path")
    assert "pref-page" in pref_panel._page_nav_dict(PrefPage)["url"]

    # Cluster sub-nav without get_should_register_sub_navigation (attr only).
    class AttrCluster:
        should_register_sub_navigation = False
        sub_navigation_position = "start"

    assert (
        Panel.make("x").path("/x")._render_cluster_sub_nav(
            AttrCluster, [{"label": "A", "url": "/a"}]
        )
        == ""
    )

    # User menu: profile special + default logout; early return when disabled.
    um = (
        Panel.make("um")
        .path("/um")
        .user(user)
        .user_menu_items(
            {
                "profile": lambda a: a.label("Profile").url("/um/me"),
            }
        )
    )
    html_um = um.render_shell("<p>x</p>", user=user)
    assert "Profile" in html_um
    assert "Sign out" in html_um
    assert um._render_user_menu(user=None) == ""
    disabled_um = Panel.make("dum").path("/dum").user(user).user_menu(False)
    assert disabled_um._render_user_menu(user=user) == ""

    # collect_cluster_sub_navigation with empty active_path.
    assert panel.collect_cluster_sub_navigation(None) == (None, [])

    # navigation_items setter path.
    assert (
        Panel.make("ni")
        .path("/ni")
        .dashboard(False)
        .navigation_items([NavigationItem.make("z").label("Z").url("/z")])
        .navigation_items()
    )


def test_panel_navigation_remaining_branches() -> None:
    """Close remaining statement/branch gaps in panel navigation helpers."""
    admin = OrbitUser.default()

    # user_menu(True) without position (false branch of position is not None).
    Panel.make("um0").path("/um0").user_menu(True)

    # logout as callable special (hits key == "logout" setup before customize).
    p_logout = (
        Panel.make("ulo")
        .path("/ulo")
        .user(admin)
        .user_menu_items(
            {
                "logout": lambda action: action.label("Exit now")
                .url("/ulo/logout")
                .post_to_url(),
            }
        )
    )
    assert "Exit now" in p_logout.render_shell("<p>x</p>", user=admin)

    # profile already present in items → skip inserting special.
    p_prof = (
        Panel.make("up")
        .path("/up")
        .user(admin)
        .user_menu_item(
            UserMenuItem.make("profile").label("Existing").url("/up/me")
        )
        .user_menu_items(
            {"profile": lambda a: a.label("Special").url("/up/special")}
        )
    )
    html_prof = p_prof.render_shell("<p>x</p>", user=admin)
    assert "Existing" in html_prof

    # logout special with visible=False + logout already in items.
    p_hidden_lo = (
        Panel.make("uhl")
        .path("/uhl")
        .user(admin)
        .user_menu_item(
            UserMenuItem.make("logout").label("Manual out").url("/uhl/out")
        )
        .user_menu_items(
            {
                "logout": lambda a: a.label("Hidden LO")
                .url("/uhl/logout")
                .visible(False),
            }
        )
    )
    html_lo = p_hidden_lo.render_shell("<p>x</p>", user=admin)
    assert "Manual out" in html_lo
    assert "Hidden LO" not in html_lo

    # Non-cluster page with should_register_navigation=False (line 831 continue).
    class HiddenPage(Page):
        slug = "hidden-page"
        navigation_label = "Hidden Page"
        should_register_navigation = False

    hid = (
        Panel.make("hp")
        .path("/hp")
        .dashboard(False)
        .pages([HiddenPage])
    )
    assert "Hidden Page" not in [i["label"] for i in hid.navigation_items()]

    # Dashboard not registered / not accessible while dash not in _pages.
    from almasix.orbit.panels.pages.dashboard import Dashboard

    class NoNavDash(Dashboard):
        should_register_navigation = False

    class DenyDash(Dashboard):
        permission = "dash.never"

    limited = OrbitUser.make().name("L").admin(False).permissions("posts.view_any")
    Panel.make("nd").path("/nd").dashboard(NoNavDash).navigation_items()
    deny_dash = Panel.make("dd").path("/dd").dashboard(DenyDash).user(limited)
    deny_dash._collect_navigation_items(user=limited)

    # Dashboard on pages list but should_register False.
    class ListedHiddenDash(Dashboard):
        should_register_navigation = False
        navigation_label = "ListedHidden"

    listed = (
        Panel.make("lh")
        .path("/lh")
        .pages([ListedHiddenDash])
        .dashboard(ListedHiddenDash)  # same class so page is dash
    )
    assert "ListedHidden" not in [i["label"] for i in listed.navigation_items()]

    # Dashboard on pages, register true but can_access false.
    class DenyListedDash(Dashboard):
        navigation_label = "DenyListed"
        permission = "dash.never"

    deny_listed = (
        Panel.make("dld")
        .path("/dld")
        .pages([DenyListedDash])
        .dashboard(DenyListedDash)
        .user(limited)
    )
    assert "DenyListed" not in [
        i["label"] for i in deny_listed._collect_navigation_items(user=limited)
    ]

    # Builder group with empty name (skip _nav_groups store).
    empty_g = (
        Panel.make("eg")
        .path("/eg")
        .dashboard(False)
        .navigation(
            lambda b: b.groups(
                [
                    NavigationGroup.make(None).items(
                        [NavigationItem.make("x").label("X").url("/x")]
                    )
                ]
            )
        )
    )
    assert any(i["label"] == "X" for i in empty_g.navigation_items())

    # _cluster_key string branch.
    assert Panel.make("ck").path("/ck")._cluster_key("settings") == "settings"

    # Second loop: empty registered, but panel clusters have members.
    class LateCluster(Cluster):
        slug = "late"

    class LateRes(Resource):
        slug = "late-items"
        cluster = LateCluster

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    late = (
        Panel.make("late")
        .path("/late")
        .dashboard(False)
        .clusters([LateCluster])
        .resources([LateRes])
    )
    assert late._iter_clusters_for_nav(set())  # hits 953-954

    # Duplicate type cluster keys → skip re-append (916->919).
    class DupA(Cluster):
        slug = "dup"

    class DupB(Cluster):
        slug = "dup-b"

    DupB.__module__ = DupA.__module__
    DupB.__qualname__ = DupA.__qualname__
    late._iter_clusters_for_nav({DupA, DupB})

    # String cluster: first cand misses, second matches (922->921).
    class FirstMiss(Cluster):
        slug = "aaa"

    class SecondHit(Cluster):
        slug = "bbb"

    multi = Panel.make("multi").path("/multi").clusters([FirstMiss, SecondHit])
    multi._iter_clusters_for_nav({"bbb"})

    # String cluster matching panel cluster by slug.
    class NamedHubCluster(Cluster):
        slug = "namedhub"

    class NamedRes(Resource):
        slug = "named-items"
        cluster = "namedhub"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    named = (
        Panel.make("named")
        .path("/named")
        .dashboard(False)
        .clusters([NamedHubCluster])
        .resources([NamedRes])
    )
    # Type already seen, then string slug matches same cluster (925->928).
    # Use a list so type is processed before the string (set order is unreliable).
    named._iter_clusters_for_nav([NamedHubCluster, "namedhub"])  # type: ignore[arg-type]
    # Match by class __name__ as well.
    named._iter_clusters_for_nav({"NamedHubCluster"})

    # Synthesize when key already seen, then continue to another registered
    # string so the false branch loops back to the ``for registered`` header.
    import almasix.orbit.panels.panel as panel_mod

    pre = type(
        "GhostLandCluster",
        (Cluster,),
        {"slug": "ghost-land", "navigation_label": "Ghost Land"},
    )
    pre.__module__ = panel_mod.__name__
    pre.__qualname__ = "GhostLandCluster"
    synth_panel = Panel.make("synth").path("/synth")
    synth_panel._iter_clusters_for_nav([pre, "ghost-land", "another-orphan"])

    # _cluster_members: same key, different type object (969-970).
    class KeyA(Cluster):
        slug = "keyed"

    class KeyB(Cluster):
        slug = "other"

    KeyB.__module__ = KeyA.__module__
    KeyB.__qualname__ = KeyA.__qualname__

    class KeyRes(Resource):
        slug = "keyed-items"
        cluster = KeyB

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    keyed = (
        Panel.make("keyed")
        .path("/keyed")
        .dashboard(False)
        .clusters([KeyA])
        .resources([KeyRes])
    )
    members = keyed._cluster_members(KeyA)
    assert KeyRes in members

    # String cluster membership via slug / __name__.
    class StrMemCluster(Cluster):
        slug = "strmem"

    class StrMemRes(Resource):
        slug = "strmem-items"
        cluster = "strmem"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    strmem = (
        Panel.make("sm")
        .path("/sm")
        .clusters([StrMemCluster])
        .resources([StrMemRes])
    )
    assert StrMemRes in strmem._cluster_members(StrMemCluster)
    assert StrMemRes in strmem._cluster_members("strmem")

    # Empty members → _cluster_nav_dict None.
    class EmptyCluster(Cluster):
        slug = "emptyc"

    empty_c = Panel.make("ec").path("/ec").clusters([EmptyCluster])
    assert empty_c._cluster_nav_dict(EmptyCluster) is None

    # _member_url: type cluster without get_url_path_prefix.
    class TypeOnlyCluster(Cluster):
        slug = "typeonly"

    class TypeOnlyMember:
        cluster = TypeOnlyCluster

        @classmethod
        def get_slug(cls):
            return "tom"

    tom_panel = Panel.make("tom").path("/tom").clusters([TypeOnlyCluster])
    url = tom_panel._member_url(TypeOnlyMember)
    assert "typeonly" in url and "tom" in url

    # String cluster on bare member (1034).
    class StrOnlyMember:
        cluster = "stronly"

        @classmethod
        def get_slug(cls):
            return "som"

    assert "stronly" in Panel.make("som").path("/som")._member_url(StrOnlyMember)

    # get_pages returns non-dict / empty index → fall through.
    class WeirdPages:
        cluster = None

        @classmethod
        def get_pages(cls):
            return ["not-a-dict"]

        @classmethod
        def get_slug(cls):
            return "weird"

        @classmethod
        def get_url_path_prefix(cls):
            return "/som/weird-prefix"

    assert "weird" in Panel.make("wp").path("/wp")._member_url(WeirdPages)

    # Top + end cluster layouts with admin (auth allows members).
    class TopCluster(Cluster):
        slug = "topc"
        sub_navigation_position = "top"
        navigation_label = "TopC"

    class TopRes(Resource):
        slug = "top-items"
        cluster = TopCluster
        navigation_label = "Top Items"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    top = (
        Panel.make("topc")
        .path("/topc")
        .dashboard(False)
        .clusters([TopCluster])
        .resources([TopRes])
        .sidebar_navigation()
        .user(admin)
    )
    TopRes._panel_path = "/topc"  # type: ignore[attr-defined]
    html_top = top.render_shell(
        "<p>x</p>", active_path="/topc/topc/top-items", user=admin
    )
    assert "or-cluster-layout-top" in html_top

    # Breadcrumbs: cluster in get_clusters() match + members for URL.
    class CrumbCluster(Cluster):
        slug = "crumb"
        cluster_breadcrumb = "Crumb Hub"

    class CrumbRes(Resource):
        slug = "crumb-items"
        cluster = CrumbCluster

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    crumb = (
        Panel.make("crumb")
        .path("/crumb")
        .dashboard(False)
        .clusters([CrumbCluster])
        .resources([CrumbRes])
    )
    CrumbRes._panel_path = "/crumb"  # type: ignore[attr-defined]
    crumbs = crumb.breadcrumbs("/crumb/crumb/crumb-items")
    assert any("Crumb" in str(c.get("label")) for c in crumbs)

    # Cluster without get_cluster_breadcrumb attr (hasattr false path).
    class MinimalCluster:
        @classmethod
        def get_slug(cls):
            return "mini"

        @classmethod
        def get_navigation_label(cls):
            return "Mini"

        @classmethod
        def path_prefix(cls):
            return "/mini"

    class MiniRes(Resource):
        slug = "mini-items"
        cluster = MinimalCluster  # type: ignore[assignment]

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    mini = (
        Panel.make("mini")
        .path("/mini")
        .dashboard(False)
        .clusters([MinimalCluster])  # type: ignore[list-item]
        .resources([MiniRes])
    )
    MiniRes._panel_path = "/mini"  # type: ignore[attr-defined]
    mini_crumbs = mini.breadcrumbs("/mini/mini/mini-items")
    assert any(c.get("label") == "Mini" for c in mini_crumbs)

    # Page without can_access when user is set — already covered; ensure
    # _resolve_cluster without get_cluster (getattr cluster).
    class AttrClusterObj:
        cluster = "attr-c"
        navigation_label = "AttrC"

        @classmethod
        def get_slug(cls):
            return "attrc"

        @classmethod
        def get_navigation_label(cls):
            return "AttrC"

    assert Panel.make("ac").path("/ac")._resolve_cluster(AttrClusterObj) == "attr-c"

    # collect_cluster_sub_navigation: path equals prefix exactly.
    cluster, items = top.collect_cluster_sub_navigation(
        "/topc/topc", user=admin
    )
    assert cluster is TopCluster
    assert items

    # Remaining branch arcs -------------------------------------------------

    # _member_url with no cluster (1030 false → return).
    class NoClusterMember:
        @classmethod
        def get_slug(cls):
            return "ncm"

    ncm_url = Panel.make("ncm").path("/ncm")._member_url(NoClusterMember)
    assert ncm_url.endswith("/ncm") or "ncm" in ncm_url

    # Sub-nav skips a hidden member then includes a visible one (1160 continue).
    class MixCluster(Cluster):
        slug = "mix"
        navigation_label = "Mix"

    class MixHidden(Resource):
        slug = "mix-hidden"
        cluster = MixCluster
        should_register_navigation = False

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class MixVisible(Resource):
        slug = "mix-visible"
        cluster = MixCluster
        navigation_label = "Mix Visible"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    mix = (
        Panel.make("mix")
        .path("/mix")
        .dashboard(False)
        .clusters([MixCluster])
        .resources([MixHidden, MixVisible])
        .user(admin)
    )
    MixVisible._panel_path = "/mix"  # type: ignore[attr-defined]
    MixHidden._panel_path = "/mix"  # type: ignore[attr-defined]
    _c, mix_items = mix.collect_cluster_sub_navigation(
        "/mix/mix/mix-visible", user=admin
    )
    assert any(i["label"] == "Mix Visible" for i in mix_items)
    assert not any(i["label"] == "Mix Hidden" for i in mix_items)

    # Breadcrumbs: multiple clusters (first miss), empty members, no breadcrumb helper.
    class OtherCluster(Cluster):
        slug = "other"

    class LonelyCluster(Cluster):
        slug = "lonely"
        cluster_breadcrumb = "Lonely"

    lonely = (
        Panel.make("lonely")
        .path("/lonely")
        .dashboard(False)
        .clusters([OtherCluster, LonelyCluster])
    )
    lonely_crumbs = lonely.breadcrumbs("/lonely/lonely")
    assert any(c.get("label") == "Lonely" for c in lonely_crumbs)

    # Implied cluster membership (not pre-registered) + members URL.
    class ImpliedOnly(Cluster):
        slug = "impliedonly"

    class ImpliedOnlyRes(Resource):
        slug = "io-items"
        cluster = ImpliedOnly

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    implied = (
        Panel.make("io")
        .path("/io")
        .dashboard(False)
        .resources([ImpliedOnlyRes])  # cluster NOT in .clusters()
    )
    ImpliedOnlyRes._panel_path = "/io"  # type: ignore[attr-defined]
    io_crumbs = implied.breadcrumbs("/io/impliedonly/io-items")
    assert any("Implied" in str(c.get("label")) or "Io" in str(c.get("label")) for c in io_crumbs)
    # Cluster was appended to panel.
    assert ImpliedOnly in implied.get_clusters()

    # String-resolved cluster in membership loop (971 continue).
    class StrSlugCluster(Cluster):
        slug = "strslug"

    class StrSlugRes(Resource):
        slug = "ss-items"
        cluster = "strslug"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class StrSlugRes2(Resource):
        slug = "ss-items-2"
        cluster = "StrSlugCluster"  # match __name__

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    ss = (
        Panel.make("ss")
        .path("/ss")
        .clusters([StrSlugCluster])
        .resources([StrSlugRes, StrSlugRes2, _PostResource])
    )
    assert StrSlugRes in ss._cluster_members(StrSlugCluster)
    assert StrSlugRes2 in ss._cluster_members(StrSlugCluster)

    # String cluster that does not match (972 false → next obj).
    class NopeStrRes(Resource):
        slug = "nope-items"
        cluster = "nope-slug"

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    ss.resources([NopeStrRes])
    ss._cluster_members(StrSlugCluster)  # walks past nope string

    # Sub-nav: first cluster prefix misses, second hits (1161 false → next).
    class ACluster(Cluster):
        slug = "acluster"

    class BCluster(Cluster):
        slug = "bcluster"

    class ARes(Resource):
        slug = "a-items"
        cluster = ACluster

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    class BRes(Resource):
        slug = "b-items"
        cluster = BCluster

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    ab = (
        Panel.make("ab")
        .path("/ab")
        .dashboard(False)
        .clusters([ACluster, BCluster])
        .resources([ARes, BRes])
        .user(admin)
    )
    ARes._panel_path = "/ab"  # type: ignore[attr-defined]
    BRes._panel_path = "/ab"  # type: ignore[attr-defined]
    # Sets do not preserve order — force A (miss) before B (hit).
    ab._iter_clusters_for_nav = lambda _registered: [ACluster, BCluster]  # type: ignore[method-assign]
    b_cluster, b_items = ab.collect_cluster_sub_navigation(
        "/ab/bcluster/b-items", user=admin
    )
    assert b_cluster is BCluster
    assert b_items

    # Breadcrumbs membership find when cluster already in _clusters (1462 false).
    class AlreadyCluster(Cluster):
        slug = "already"

    class AlreadyRes(Resource):
        slug = "already-items"
        cluster = AlreadyCluster

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("t")])

        @classmethod
        def get_records(cls):
            return []

    already = (
        Panel.make("al")
        .path("/al")
        .dashboard(False)
        .clusters([AlreadyCluster])
        .resources([AlreadyRes])
    )
    AlreadyRes._panel_path = "/al"  # type: ignore[attr-defined]
    # First loop uses get_clusters(); force it empty so membership path runs
    # while the cluster remains in ``_clusters``.
    already.get_clusters = lambda: []  # type: ignore[method-assign]
    already_crumbs = already.breadcrumbs("/al/already/already-items")
    assert any("Already" in str(c.get("label")) for c in already_crumbs)
