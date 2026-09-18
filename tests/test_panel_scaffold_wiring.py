"""Scaffold: panels live in app/orbit; provider only discovers them."""

from __future__ import annotations

import sys
from pathlib import Path

from almasix.framework.application import Application
from almasix.orbit.panels.commands import (
    MakeOrbitPanelCommand,
    OrbitInstallCommand,
    _ensure_provider_in_app_config,
    _ensure_thin_provider,
)
from almasix.orbit.panels.discover import register_app_orbit_panels
from almasix.orbit.panels.panel import PanelRegistry


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


def test_orbit_install_writes_app_orbit_panel_and_thin_provider(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    cmd = OrbitInstallCommand(app)
    cmd._options = {"path": "admin", "panel": "admin", "force": True}
    assert cmd.handle() == 0

    stub = tmp_path / "app" / "orbit" / "admin_panel.py"
    assert stub.is_file()
    assert "def register_admin_panel" in stub.read_text(encoding="utf-8")
    assert (tmp_path / "app" / "orbit" / "__init__.py").is_file()

    provider = (tmp_path / "app" / "providers" / "orbit_panel_provider.py").read_text(
        encoding="utf-8"
    )
    assert "register_app_orbit_panels" in provider
    assert "Panel.make" not in provider

    cfg = (tmp_path / "config" / "app.py").read_text(encoding="utf-8")
    assert "OrbitPanelProvider" in cfg


def test_orbit_panel_adds_stub_without_patching_provider_calls(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    install = OrbitInstallCommand(app)
    install._options = {"path": "admin", "panel": "admin", "force": True}
    assert install.handle() == 0

    cmd = MakeOrbitPanelCommand(app)
    cmd._arguments = {"name": "app"}
    cmd._options = {"path": "app", "force": True}
    assert cmd.handle() == 0

    assert (tmp_path / "app" / "orbit" / "app_panel.py").is_file()
    provider = (tmp_path / "app" / "providers" / "orbit_panel_provider.py").read_text(
        encoding="utf-8"
    )
    assert "register_app_orbit_panels" in provider
    assert "register_app_panel(registry)" not in provider


def test_register_app_orbit_panels_discovers_stubs(tmp_path: Path, monkeypatch) -> None:
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
    try:
        registry = PanelRegistry()
        panels = register_app_orbit_panels(registry)
        assert registry.get("admin") is not None
        assert registry.get("shop") is not None
        assert len(panels) == 2
    finally:
        sys.path.remove(str(tmp_path))


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
