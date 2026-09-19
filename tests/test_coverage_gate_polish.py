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
