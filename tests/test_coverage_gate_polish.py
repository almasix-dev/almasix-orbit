"""Push remaining coverage gaps toward 100% (gate 99.5%)."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
from almasix.orbit import Panel, PanelRegistry, Resource
from almasix.orbit.panels.commands import _pluralize_label
from almasix.orbit.panels.conduit.hosts import CreateRecordHost, EditRecordHost
from almasix.orbit.panels.discover import (
    _call_panel_registrar,
    _classes_from_module,
    _discover_in_path,
    _wire_default_discovery,
    load_theme_css,
    register_app_orbit_panels,
)
from almasix.orbit.panels.navigation import build_menu_layout
from almasix.orbit.panels.resource_generator import load_columns


def test_load_theme_css_non_directory_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    file_path = tmp_path / "not_a_dir"
    file_path.write_text("x", encoding="utf-8")
    pkg = types.ModuleType("orbit_theme_file_path")
    pkg.__path__ = [str(file_path)]  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "orbit_theme_file_path", pkg)
    assert load_theme_css("orbit_theme_file_path") == []


def test_register_duplicate_and_legacy_import_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "app" / "orbit"
    root.mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")

    admin = root / "admin"
    admin.mkdir()
    (admin / "__init__.py").write_text("", encoding="utf-8")
    (admin / "panel.py").write_text(
        '''from almasix.orbit import Panel, PanelRegistry

def register_admin_panel(registry: PanelRegistry) -> Panel:
    panel = Panel.make("admin").path("admin")
    registry.register(panel)
    return panel
''',
        encoding="utf-8",
    )
    # Legacy twin for same id — should be skipped via seen_ids after colocated
    (root / "admin_panel.py").write_text(
        '''from almasix.orbit import Panel, PanelRegistry

def register_admin_panel(registry: PanelRegistry) -> Panel:
    panel = Panel.make("admin").path("admin2")
    registry.register(panel)
    return panel
''',
        encoding="utf-8",
    )
    # Broken legacy module
    (root / "broken_panel.py").write_text("raise RuntimeError('boom')\n", encoding="utf-8")
    # Non-panel module name that isn't a package
    (root / "notes.py").write_text("x = 1\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    sys.path.insert(0, str(tmp_path))
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]
    try:
        with pytest.warns(DeprecationWarning):
            panels = register_app_orbit_panels(PanelRegistry())
        ids = [p.id for p in panels if p is not None]
        assert ids.count("admin") == 1
    finally:
        sys.path.remove(str(tmp_path))
        for key in list(sys.modules):
            if key == "app" or key.startswith("app."):
                del sys.modules[key]


def test_pluralize_mixed_case_trailing_upper() -> None:
    assert _pluralize_label("itemQ") == "itemQS"

    assert _pluralize_label("") == ""
    assert _pluralize_label("   ") == ""
    assert _pluralize_label("box") == "boxes"
    assert _pluralize_label("Box") == "Boxes"
    assert _pluralize_label("buzz") == "buzzes"
    assert _pluralize_label("church") == "churches"
    assert _pluralize_label("dish") == "dishes"
    assert _pluralize_label("city") == "cities"
    assert _pluralize_label("CITY") == "CITIES"
    assert _pluralize_label("day") == "days"
    assert _pluralize_label("POST") == "POSTS"
    assert _pluralize_label("ID") == "IDS"
    assert _pluralize_label("Post") == "Posts"
    assert _pluralize_label("A") == "AS"


def test_load_columns_non_callable_class_casts(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeModel:
        connection = None
        class_casts = {"active": "bool"}  # attribute, not callable

        @classmethod
        def get_table(cls) -> str:
            return "things"

    async def fake_columns(table: str, connection: str | None = None) -> list[dict[str, object]]:
        return [{"name": "active", "type": "BOOLEAN", "nullable": True}]

    monkeypatch.setattr("almasix.orm.schema.Schema.columns", fake_columns)
    cols, err = load_columns(FakeModel)  # type: ignore[arg-type]
    assert err is None
    assert cols[0].cast is None


def test_load_theme_css_edge_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert load_theme_css("") == []
    assert load_theme_css("   ") == []
    assert load_theme_css("does.not.exist.theme") == []

    pkg = types.ModuleType("orbit_theme_cov")
    pkg.__path__ = [str(tmp_path)]  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "orbit_theme_cov", pkg)

    bare = types.ModuleType("orbit_theme_bare")
    monkeypatch.setitem(sys.modules, "orbit_theme_bare", bare)
    assert load_theme_css("orbit_theme_bare") == []

    (tmp_path / "_skip.css").write_text("a{}", encoding="utf-8")
    (tmp_path / "ok.css").write_text(".x{}", encoding="utf-8")
    bad = tmp_path / "bad.css"
    bad.write_text("y{}", encoding="utf-8")

    original = Path.read_text

    def selective(self: Path, encoding: str | None = "utf-8", errors: str = "strict") -> str:
        if self.name == "bad.css":
            raise OSError("denied")
        return original(self, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", selective)
    loaded = load_theme_css("orbit_theme_cov")
    assert any(src.endswith("ok.css") for src, _ in loaded)
    assert not any("bad.css" in src for src, _ in loaded)
    assert not any("_skip" in src for src, _ in loaded)


def test_discover_in_path_and_classes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = _discover_in_path(str(tmp_path / "nope"), Resource, set())
    assert missing == []

    monkeypatch.setitem(sys.modules, "cov_pkg_missing", None)  # type: ignore[dict-item]
    assert _discover_in_path("cov_pkg_missing_zzz", Resource, set()) == []

    mod = types.ModuleType("cov_single")
    class Demo(Resource):
        pass

    mod.Demo = Demo  # type: ignore[attr-defined]
    seen: set[type] = set()
    found = _classes_from_module(mod, Resource, seen)
    assert Demo in found
    assert _classes_from_module(mod, Resource, seen) == []  # dedupe


def test_call_panel_registrar_and_wire(tmp_path: Path) -> None:
    mod = types.ModuleType("cov_panel")

    def register_ops_panel(registry: object) -> Panel:
        return Panel.make("ops").path("ops")

    mod.register_ops_panel = register_ops_panel  # type: ignore[attr-defined]
    panel = _call_panel_registrar(mod, "ops", PanelRegistry())
    assert panel is not None and panel.id == "ops"

    alt = types.ModuleType("cov_panel_alt")

    def register_shop_panel(registry: object) -> Panel:
        return Panel.make("shop")

    alt.register_shop_panel = register_shop_panel  # type: ignore[attr-defined]
    assert _call_panel_registrar(alt, "missing", PanelRegistry()) is not None

    empty = types.ModuleType("cov_panel_empty")
    assert _call_panel_registrar(empty, "x", PanelRegistry()) is None

    _wire_default_discovery(None, package="app.orbit", panel_id="admin")
    already = Panel.make("admin").discover_resources("app.models")
    _wire_default_discovery(already, package="app.orbit", panel_id="admin")
    assert already._discover_resources_in == ["app.models"]

    bare = Panel.make("admin")
    _wire_default_discovery(bare, package="app.orbit", panel_id="admin")
    assert "app.orbit.admin.resources" in bare._discover_resources_in


def test_register_app_orbit_panels_import_edges(monkeypatch: pytest.MonkeyPatch) -> None:
    assert register_app_orbit_panels(PanelRegistry(), package="definitely.missing.pkg") == []

    bare = types.ModuleType("orbit_bare_pkg")
    monkeypatch.setitem(sys.modules, "orbit_bare_pkg", bare)
    assert register_app_orbit_panels(PanelRegistry(), package="orbit_bare_pkg") == []


def test_register_skips_pkg_without_panel_module(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "app" / "orbit"
    root.mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    ghost = root / "ghost"
    ghost.mkdir()
    (ghost / "__init__.py").write_text("", encoding="utf-8")
    # no panel.py

    monkeypatch.chdir(tmp_path)
    sys.path.insert(0, str(tmp_path))
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]
    try:
        panels = register_app_orbit_panels(PanelRegistry())
        assert panels == [] or all(p is None or p.id != "ghost" for p in panels)
    finally:
        sys.path.remove(str(tmp_path))


def test_navigation_sub_category_alias_normalized() -> None:
    ctx = build_menu_layout(
        [
            {
                "label": "Posts",
                "url": "/posts",
                "group": "Content",
                "sub_category": "Writing",
                "sort": 1,
            }
        ],
        active_path="/posts",
        layout="sidebar_topbar",
    )
    assert any(i.get("subgroup") == "Writing" for i in ctx.flat_items)
    assert any(s.label == "Writing" for s in ctx.menu_secondary)


def test_search_select_options_and_model_fallback() -> None:
    class Host(CreateRecordHost):
        panel_id = "admin"

        def get_resource(self) -> type:
            class Broken(Resource):
                @classmethod
                def get_model(cls) -> type:
                    raise RuntimeError("no model")

                model = None

                @classmethod
                def get_form(cls) -> object:
                    from almasix.orbit.forms import Form

                    return Form.make("f")

            return Broken

        def dispatch(self, *args: object, **kwargs: object) -> None:
            return None

    host = Host()
    host.searchSelectOptions("author", "ada")
    assert host.select_search["author"] == "ada"

    html = host.render()
    assert isinstance(html, str)


def test_select_option_label_branch_edges() -> None:
    from almasix.orbit.forms import Select

    # Existing relationship with search_columns + custom title — skip overwrite branches
    sel = (
        Select.make("a")
        .relationship("artist", "name", search_columns=["name"])
        .option_label("{name} - {country}")
    )
    rel = sel.get_relationship()
    assert rel is not None
    assert rel["search_columns"] == ["name"]
    assert rel["title_attribute"] == "name"
    assert rel["option_label"] == "{name} - {country}"

    # get_option_label on existing relationship
    sel.get_option_label_from_record_using(lambda r: "lab")
    assert callable(sel.get_relationship()["get_option_label"])

    # owner model: resource without get_model, and get_model failing without model attr
    class OnlyModel:
        model = object

    class RaisingNoModel:
        @classmethod
        def get_model(cls) -> type:
            raise RuntimeError("x")

    assert Select.make("x")._owner_model(resource=OnlyModel) is object
    assert Select.make("x")._owner_model(resource=RaisingNoModel) is None
    assert Select.make("x").resolve_relationship_options() == {}


def test_select_render_rel_search_columns_without_name() -> None:
    from almasix.orbit.forms import Select

    sel = Select.make("x")
    sel._relationship = {
        "name": None,
        "title_attribute": "id",
        "model": None,
        "option_label": None,
        "search_columns": ["name"],
        "preload": True,
        "modify_query": None,
        "get_option_label": None,
    }
    html = sel.searchable().render(None)
    assert "data-search-columns" in html
    assert "data-preload" in html


def test_edit_record_model_fallback() -> None:
    class Host(EditRecordHost):
        panel_id = "admin"
        record_id = "1"
        data = {"title": "x"}

        def get_resource(self) -> type:
            class Broken(Resource):
                @classmethod
                def get_model(cls) -> type:
                    raise RuntimeError("no model")

                model = None

                @classmethod
                def get_form(cls) -> object:
                    from almasix.orbit.forms import Form

                    return Form.make("f")

            return Broken

        def get_record(self) -> dict[str, object]:
            return {"id": "1", "title": "x"}

    host = Host()
    html = host.render()
    assert isinstance(html, str)


def test_option_label_sets_title_from_placeholders() -> None:
    from almasix.orbit.forms import Select

    sel = Select.make("a").relationship("artist", "id").option_label("{name} ({country})")
    rel = sel.get_relationship()
    assert rel is not None
    assert rel["title_attribute"] == "name"
    assert rel["search_columns"] == ["name", "country"]
    assert rel["option_label"] == "{name} ({country})"


def test_create_edit_record_page_model_exception_without_ctx() -> None:
    from almasix.orbit.forms import Form
    from almasix.orbit.panels.pages.resource_pages import CreateRecord, EditRecord

    class Broken(Resource):
        records_mutable = True

        @classmethod
        def get_model(cls) -> type:
            raise RuntimeError("no model")

        model = None

        @classmethod
        def get_form(cls) -> object:
            return Form.make("f")

        @classmethod
        def get_slug(cls) -> str:
            return "broken"

        @classmethod
        def get_navigation_label(cls) -> str:
            return "Broken"

    class BoundCreate(CreateRecord):
        resource = Broken

    class BoundEdit(EditRecord):
        resource = Broken

    assert "Create" in BoundCreate.render(state={})
    assert "or-page-edit" in BoundEdit.render(record={"id": "1"}, state={"title": "t"})


def test_prompt_name_and_list_panel_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from almasix.framework.application import Application
    from almasix.orbit.panels.commands import (
        MakeOrbitPageCommand,
        MakeOrbitWidgetCommand,
        _ensure_provider_in_app_config,
        _list_panel_ids,
        _panel_id_option,
        _prompt_name,
    )

    class FakeCmd:
        INVALID = 2
        FAILURE = 1
        SUCCESS = 0
        app = None

        def ask(self, *_a: object, **_k: object) -> str:
            return "  Settings  "

        def error(self, *_a: object, **_k: object) -> None:
            return None

        def option(self, name: str) -> object:
            return None

    monkeypatch.setattr("almasix.console.prompts.types.is_interactive", lambda: True)
    assert _prompt_name(FakeCmd(), label="Page name") == "Settings"  # type: ignore[arg-type]

    class EmptyAsk(FakeCmd):
        def ask(self, *_a: object, **_k: object) -> str:
            return "   "

    assert _prompt_name(EmptyAsk(), label="Page name") is None  # type: ignore[arg-type]

    monkeypatch.setattr("almasix.console.prompts.types.is_interactive", lambda: False)
    assert _prompt_name(FakeCmd(), label="Page name") is None  # type: ignore[arg-type]

    empty = Application(tmp_path / "no_orbit")
    assert _list_panel_ids(empty) == []

    orbit = tmp_path / "app" / "orbit"
    orbit.mkdir(parents=True)
    (orbit / "shared").mkdir()
    (orbit / "_skip").mkdir()
    (orbit / "notes.txt").write_text("x", encoding="utf-8")
    (orbit / "ops").mkdir()
    (orbit / "ops" / "panel.py").write_text("x=1\n", encoding="utf-8")
    (orbit / "ghost").mkdir()  # dir without panel.py
    app = Application(tmp_path)
    assert _list_panel_ids(app) == ["ops"]

    cmd = MakeOrbitPageCommand(app)
    assert _panel_id_option(cmd, panel="shop") == "shop"

    # provider config edges
    bare = Application(tmp_path / "bare")
    assert "not found" in _ensure_provider_in_app_config(bare)

    cfg_dir = tmp_path / "cfg"
    (cfg_dir / "config").mkdir(parents=True)
    (cfg_dir / "config" / "app.py").write_text("config = {}\n", encoding="utf-8")
    assert "could not patch" in _ensure_provider_in_app_config(Application(cfg_dir))

    sq = tmp_path / "sq"
    (sq / "config").mkdir(parents=True)
    (sq / "config" / "app.py").write_text("config = {'providers': []}\n", encoding="utf-8")
    assert "registered" in _ensure_provider_in_app_config(Application(sq))
    assert "OrbitPanelProvider" in (sq / "config" / "app.py").read_text(encoding="utf-8")

    # page/widget: missing name, Page/Widget suffix, app None, exists without force
    page = MakeOrbitPageCommand()
    page._arguments = {}
    page._options = {}
    monkeypatch.setattr("almasix.console.prompts.types.is_interactive", lambda: False)
    assert page.handle() == page.INVALID

    page2 = MakeOrbitPageCommand()
    page2._arguments = {"name": "SettingsPage"}
    page2._options = {"panel": "admin"}
    assert page2.handle() == page2.SUCCESS

    widget = MakeOrbitWidgetCommand()
    widget._arguments = {}
    widget._options = {}
    assert widget.handle() == widget.INVALID

    widget2 = MakeOrbitWidgetCommand()
    widget2._arguments = {"name": "StatsWidget"}
    widget2._options = {"panel": "admin"}
    assert widget2.handle() == widget2.SUCCESS

    pages_dir = orbit / "ops" / "pages"
    pages_dir.mkdir(parents=True)
    (pages_dir / "__init__.py").write_text("", encoding="utf-8")
    existing = pages_dir / "settings_page.py"
    existing.write_text("x=1\n", encoding="utf-8")
    page3 = MakeOrbitPageCommand(app)
    page3._arguments = {"name": "Settings"}
    page3._options = {"panel": "ops", "force": False}
    assert page3.handle() == page3.FAILURE

    widgets_dir = orbit / "ops" / "widgets"
    widgets_dir.mkdir(parents=True)
    (widgets_dir / "__init__.py").write_text("", encoding="utf-8")
    (widgets_dir / "stats_widget.py").write_text("x=1\n", encoding="utf-8")
    widget3 = MakeOrbitWidgetCommand(app)
    widget3._arguments = {"name": "Stats"}
    widget3._options = {"panel": "ops", "force": False}
    assert widget3.handle() == widget3.FAILURE


def test_resource_model_without_generate_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from almasix.orbit.panels.commands import MakeOrbitResourceCommand

    app_root = tmp_path
    (app_root / "app" / "orbit" / "admin").mkdir(parents=True)
    (app_root / "app" / "orbit" / "admin" / "panel.py").write_text("x=1\n", encoding="utf-8")

    class FakeApp:
        def path(self, *parts: str) -> str:
            return str(app_root.joinpath(*parts))

    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.resolve_model",
        lambda name: type(
            "Post",
            (),
            {
                "__module__": "app.models.post",
                "__name__": "Post",
                "get_table": classmethod(lambda cls: "posts"),
            },
        ),
    )
    cmd = MakeOrbitResourceCommand(FakeApp())
    monkeypatch.setattr(cmd, "_should_prompt_generate", lambda: False)
    cmd._arguments = {"name": "Post"}
    cmd._options = {"panel": "admin", "force": True}
    assert cmd.handle() == 0


def test_wire_discovery_non_callable_and_empty_registrar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from almasix.orbit.panels.discover import _wire_default_discovery

    class NoWire:
        _discover_resources_in: list[str] = []
        _discover_pages_in: list[str] = []
        _discover_widgets_in: list[str] = []
        discover_panel_dirs = "not-callable"

    _wire_default_discovery(NoWire(), package="app.orbit", panel_id="x")  # type: ignore[arg-type]

    root = tmp_path / "app" / "orbit"
    root.mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    empty = root / "empty"
    empty.mkdir()
    (empty / "__init__.py").write_text("", encoding="utf-8")
    (empty / "panel.py").write_text("x = 1\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    sys.path.insert(0, str(tmp_path))
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]
    try:
        panels = register_app_orbit_panels(PanelRegistry())
        assert all(p is None or getattr(p, "id", None) != "empty" for p in panels)
    finally:
        sys.path.remove(str(tmp_path))


def test_legacy_registrar_none_without_callable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "app" / "orbit"
    root.mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    (root / "ghost_panel.py").write_text("x = 1\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    sys.path.insert(0, str(tmp_path))
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]
    try:
        with pytest.warns(DeprecationWarning):
            panels = register_app_orbit_panels(PanelRegistry())
        assert panels == [] or all(
            p is None or getattr(p, "id", None) != "ghost" for p in panels
        )
    finally:
        sys.path.remove(str(tmp_path))


def test_navigation_subgroup_empty_name_skipped() -> None:
    from almasix.orbit.panels.navigation import NavigationSubgroup

    panel = Panel.make("admin").navigation_subgroup(NavigationSubgroup.make())
    assert panel._nav_subgroups == {}


def test_mount_panel_dedupes_overlapping_auth_middleware() -> None:
    from almasix.orbit.panels.routing import mount_panel

    class Router:
        def __init__(self) -> None:
            self.routes: list[object] = []

        def add(self, *args: object, **kwargs: object) -> None:
            self.routes.append((args, kwargs))

    panel = (
        Panel.make("admin")
        .path("admin")
        .middleware(["web"])
        .auth_middleware(["web"])
        .login()
    )
    mount_panel(Router(), panel)
    assert panel.get_auth_middleware() == ["web"]
