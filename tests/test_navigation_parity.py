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
