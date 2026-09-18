"""Scaffold wiring: provider listed in config + orbit:panel stubs hooked up."""

from __future__ import annotations

from pathlib import Path

from almasix.framework.application import Application
from almasix.orbit.panels.commands import (
    MakeOrbitPanelCommand,
    OrbitInstallCommand,
    _ensure_provider_in_app_config,
    _wire_panel_stub_into_provider,
)


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


def test_orbit_install_registers_provider_in_app_config(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    cmd = OrbitInstallCommand(app)
    cmd._options = {"path": "admin", "panel": "admin", "force": True}
    assert cmd.handle() == 0
    text = (tmp_path / "config" / "app.py").read_text(encoding="utf-8")
    assert "app.providers.orbit_panel_provider.OrbitPanelProvider" in text
    assert (tmp_path / "app" / "providers" / "orbit_panel_provider.py").is_file()


def test_orbit_panel_wires_stub_into_provider(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    # Pretend install already wrote the default provider (inline register).
    (tmp_path / "app" / "providers" / "orbit_panel_provider.py").write_text(
        '''"""Register the default Orbit panel."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.providers import ServiceProvider


class OrbitPanelProvider(ServiceProvider):
    def boot(self) -> None:
        panel = (
            Panel.make("admin")
            .path("admin")
            .brand_name("Orbit")
            .navigation_layout("apps")
            .login()
        )
        self.app.make(PanelRegistry).register(panel)
''',
        encoding="utf-8",
    )

    cmd = MakeOrbitPanelCommand(app)
    cmd._arguments = {"name": "app"}
    cmd._options = {"path": "app", "force": True}
    assert cmd.handle() == 0

    stub = (tmp_path / "app" / "orbit" / "app_panel.py").read_text(encoding="utf-8")
    assert "def register_app_panel" in stub
    provider = (tmp_path / "app" / "providers" / "orbit_panel_provider.py").read_text(
        encoding="utf-8"
    )
    assert "from app.orbit.app_panel import register_app_panel" in provider
    assert "register_app_panel(registry)" in provider
    cfg = (tmp_path / "config" / "app.py").read_text(encoding="utf-8")
    assert "OrbitPanelProvider" in cfg


def test_ensure_provider_idempotent(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    first = _ensure_provider_in_app_config(app)
    second = _ensure_provider_in_app_config(app)
    assert "registered" in first
    assert "already listed" in second


def test_wire_creates_provider_when_missing(tmp_path: Path) -> None:
    app = _app_tree(tmp_path)
    (tmp_path / "app" / "orbit").mkdir(parents=True)
    (tmp_path / "app" / "orbit" / "ops_panel.py").write_text(
        "def register_ops_panel(registry):\n    return None\n",
        encoding="utf-8",
    )
    msg = _wire_panel_stub_into_provider(app, "ops")
    assert "wrote" in msg
    text = (tmp_path / "app" / "providers" / "orbit_panel_provider.py").read_text(
        encoding="utf-8"
    )
    assert "register_ops_panel(registry)" in text
