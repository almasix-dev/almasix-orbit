"""Scaffold: colocated panels under app/orbit/{id}/; provider only discovers them."""

from __future__ import annotations

import sys
from pathlib import Path

from almasix.framework.application import Application
from almasix.orbit.panels.commands import (
    MakeOrbitPageCommand,
    MakeOrbitPanelCommand,
    MakeOrbitResourceCommand,
    MakeOrbitWidgetCommand,
    OrbitInstallCommand,
    _ensure_provider_in_app_config,
    _ensure_thin_provider,
)
from almasix.orbit.panels.discover import register_app_orbit_panels
from almasix.orbit.panels.panel import Panel, PanelRegistry


def _app_tree(tmp_path: Path) -> Application:
    (tmp_path / "app" / "providers").mkdir(parents=True)
    (tmp_path / "config").mkdir()
    (tmp_path / "public").mkdir()
    (tmp_path / "config" / "app.py").write_text(
        '''"""Application configuration."""

config = {
    "providers": [
        "app.providers.app_service_provider.AppServiceProvider",
    ],
}
''',
        encoding="utf-8",
    )
    return Application(tmp_path)


def test_orbit_install_writes_colocated_panel_and_thin_provider(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    cmd = OrbitInstallCommand(app)
    cmd._options = {"path": "admin", "panel": "admin", "force": True}
    assert cmd.handle() == 0

    stub = tmp_path / "app" / "orbit" / "admin" / "panel.py"
    assert stub.is_file()
    text = stub.read_text(encoding="utf-8")
    assert "def register_admin_panel" in text
    assert "discover_panel_dirs" in text
    assert (tmp_path / "app" / "orbit" / "admin" / "resources" / "__init__.py").is_file()
    assert (tmp_path / "app" / "orbit" / "admin" / "pages" / "__init__.py").is_file()
    assert (tmp_path / "app" / "orbit" / "admin" / "widgets" / "__init__.py").is_file()
    assert (tmp_path / "app" / "orbit" / "admin" / "themes" / "__init__.py").is_file()

    provider = (tmp_path / "app" / "providers" / "orbit_panel_provider.py").read_text(
        encoding="utf-8"
    )
    assert "register_app_orbit_panels" in provider
    assert "Panel.make" not in provider

    cfg = (tmp_path / "config" / "app.py").read_text(encoding="utf-8")
    assert "OrbitPanelProvider" in cfg


def test_orbit_panel_adds_colocated_package(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    install = OrbitInstallCommand(app)
    install._options = {"path": "admin", "panel": "admin", "force": True}
    assert install.handle() == 0

    cmd = MakeOrbitPanelCommand(app)
    cmd._arguments = {"name": "shop"}
    cmd._options = {"path": "shop", "force": True}
    assert cmd.handle() == 0

    assert (tmp_path / "app" / "orbit" / "shop" / "panel.py").is_file()
    provider = (tmp_path / "app" / "providers" / "orbit_panel_provider.py").read_text(
        encoding="utf-8"
    )
    assert "register_app_orbit_panels" in provider


def test_make_orbit_resource_respects_panel(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    install = OrbitInstallCommand(app)
    install._options = {"path": "admin", "panel": "admin", "force": True}
    assert install.handle() == 0

    cmd = MakeOrbitResourceCommand(app)
    cmd._arguments = {"name": "Post"}
    cmd._options = {"panel": "admin", "force": True}
    assert cmd.handle() == 0
    assert (tmp_path / "app" / "orbit" / "admin" / "resources" / "post_resource.py").is_file()


def test_make_orbit_page_and_widget(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    install = OrbitInstallCommand(app)
    install._options = {"path": "admin", "panel": "admin", "force": True}
    assert install.handle() == 0

    page = MakeOrbitPageCommand(app)
    page._arguments = {"name": "Settings"}
    page._options = {"panel": "admin", "force": True}
    assert page.handle() == 0
    assert (tmp_path / "app" / "orbit" / "admin" / "pages" / "settings_page.py").is_file()

    widget = MakeOrbitWidgetCommand(app)
    widget._arguments = {"name": "StatsOverview"}
    widget._options = {"panel": "admin", "force": True}
    assert widget.handle() == 0
    assert (
        tmp_path / "app" / "orbit" / "admin" / "widgets" / "stats_overview_widget.py"
    ).is_file()


def test_register_app_orbit_panels_discovers_colocated(tmp_path: Path, monkeypatch) -> None:
    app = _app_tree(tmp_path)
    install = OrbitInstallCommand(app)
    install._options = {"path": "admin", "panel": "admin", "force": True}
    assert install.handle() == 0
    cmd = MakeOrbitPanelCommand(app)
    cmd._arguments = {"name": "shop"}
    cmd._options = {"path": "shop", "force": True}
    assert cmd.handle() == 0

    monkeypatch.chdir(tmp_path)
    sys.path.insert(0, str(tmp_path))
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]
    try:
        registry = PanelRegistry()
        panels = register_app_orbit_panels(registry)
        assert registry.get("admin") is not None
        assert registry.get("shop") is not None
        assert len(panels) == 2
        admin = registry.get("admin")
        assert "app.orbit.admin.resources" in admin._discover_resources_in
    finally:
        sys.path.remove(str(tmp_path))
        for key in list(sys.modules):
            if key == "app" or key.startswith("app."):
                del sys.modules[key]


def test_legacy_panel_module_still_works_with_warning(tmp_path: Path, monkeypatch) -> None:
    import pytest

    app = _app_tree(tmp_path)
    _ensure_thin_provider(app, force=True)
    orbit = tmp_path / "app" / "orbit"
    orbit.mkdir(parents=True)
    (orbit / "__init__.py").write_text('"""orbit."""\n', encoding="utf-8")
    (orbit / "admin_panel.py").write_text(
        '''from almasix.orbit import Panel, PanelRegistry

def register_admin_panel(registry: PanelRegistry) -> Panel:
    panel = Panel.make("admin").path("admin")
    registry.register(panel)
    return panel
''',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    sys.path.insert(0, str(tmp_path))
    # Drop cached app.orbit* from earlier tmp_path tests.
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]
    try:
        registry = PanelRegistry()
        with pytest.warns(DeprecationWarning, match="Legacy panel module"):
            register_app_orbit_panels(registry)
        assert registry.get("admin") is not None
    finally:
        sys.path.remove(str(tmp_path))
        for key in list(sys.modules):
            if key == "app" or key.startswith("app."):
                del sys.modules[key]


def test_discover_panel_dirs_and_fqcn_dedupe() -> None:
    panel = Panel.make("admin").discover_panel_dirs()
    assert panel._discover_resources_in == ["app.orbit.admin.resources"]
    assert panel._discover_pages_in == ["app.orbit.admin.pages"]
    assert panel._discover_widgets_in == ["app.orbit.admin.widgets"]


def test_ensure_provider_idempotent(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    first = _ensure_provider_in_app_config(app)
    second = _ensure_provider_in_app_config(app)
    assert "registered" in first
    assert "already listed" in second


def test_ensure_thin_provider_upgrades_legacy(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    provider = tmp_path / "app" / "providers" / "orbit_panel_provider.py"
    provider.write_text(
        '''from almasix.orbit import Panel, PanelRegistry
from almasix.providers import ServiceProvider

class OrbitPanelProvider(ServiceProvider):
    def boot(self) -> None:
        self.app.make(PanelRegistry).register(Panel.make("admin").path("admin"))
''',
        encoding="utf-8",
    )
    msg = _ensure_thin_provider(app, force=False)
    assert "upgraded" in msg
    assert "register_app_orbit_panels" in provider.read_text(encoding="utf-8")
