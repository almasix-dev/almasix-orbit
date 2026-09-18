"""Regression tests for Panel Configuration (Filament 5 parity surface)."""

from __future__ import annotations

from typing import Any

from almasix.orbit.panels.hooks import (
    PANEL_HOOKS,
    Plugin,
    clear_render_hooks,
    register_render_hook,
)
from almasix.orbit.panels.panel import Panel, PanelRegistry


class _ProbePlugin(Plugin):
    def __init__(self) -> None:
        super().__init__("probe")
        self.registered = False
        self.booted = False

    def register(self, panel: Any) -> None:
        self.registered = True
        panel.brand_name("Probed")

    def boot(self, panel: Any) -> None:
        self.booted = True


def test_panel_configuration_identity_and_chrome() -> None:
    clear_render_hooks()
    panel = (
        Panel.make("admin")
        .default()
        .path("")
        .domain("admin.example.com")
        .home_url("/welcome")
        .favicon("images/favicon.svg")
        .brand_name("Acme")
        .brand_logo("/logo.svg")
        .brand_logo_height("2.5rem")
        .font("Inter")
        .primary("#111111")
        .colors(danger="#ff0000")
        .content_max_width("7xl")
        .simple_page_max_content_width("sm")
        .dark_mode()
        .theme_switcher(False)
        .default_theme_mode("dark")
        .breadcrumbs_enabled(False)
        .auth_middleware(["auth"], replace=True)
        .middleware(["web"], replace=True)
    )
    assert panel.get_path() == "/"
    assert panel.is_default() is True
    assert panel.get_domain() == "admin.example.com"
    assert panel.get_home_url() == "/welcome"
    assert panel.get_favicon_url() is not None
    assert panel.get_auth_middleware() == ["auth"]
    assert panel.get_simple_page_max_content_width() == "sm"

    brand = panel._brand_html()
    assert 'href="/welcome"' in brand

    shell = panel.render_shell("<p>Hi</p>", user=None)
    assert 'rel="icon"' in shell
    assert "--or-brand-logo-height: 2.5rem" in shell
    assert "or-theme-toggle" not in shell
    assert "fallback='dark'" in shell
    assert 'data-orbit-panel="admin"' in shell
    assert panel._render_breadcrumbs("/posts") == ""

    bare = panel.render_shell("<p>Login</p>", bare=True)
    assert "--or-content-max:" in bare
    # simple page width token ``sm`` → 24rem
    assert "24rem" in bare

    d = panel.to_dict()
    assert d["default"] is True
    assert d["domain"] == "admin.example.com"
    assert d["theme_switcher"] is False
    assert d["default_theme_mode"] == "dark"
    assert d["breadcrumbs"] is False


def test_panel_default_theme_mode_invalid_falls_back() -> None:
    panel = Panel.make("x").default_theme_mode("nope")  # type: ignore[arg-type]
    assert panel._default_theme_mode == "system"


def test_panel_plugins_boot_using_and_render_hook() -> None:
    clear_render_hooks()
    probe = _ProbePlugin()
    seen: list[str] = []

    panel = (
        Panel.make("plug")
        .plugins([probe])
        .plugin(lambda p: seen.append(p.id))
        .boot_using(lambda p: seen.append(f"boot:{p.id}"))
        .render_hook("panels::head.end", lambda **_c: "<!--hooked-->")
    )
    panel.run_plugins()
    assert probe.registered and probe.booted
    assert panel._brand == "Probed"
    assert seen == ["plug", "boot:plug"]
    html = panel.render_shell("<p>x</p>")
    assert "<!--hooked-->" in html
    assert "panels::head.end" in PANEL_HOOKS


def test_panel_registry_default() -> None:
    registry = PanelRegistry()
    a = Panel.make("a").path("a")
    b = Panel.make("b").path("b").default()
    registry.register(a)
    registry.register(b)
    assert registry.get_default() is b
    assert registry.default("a") is a
    assert registry.get_default() is a
    assert registry.default("missing") is None


def test_panel_theme_switcher_requires_dark_mode() -> None:
    panel = Panel.make("t").dark_mode(False).theme_switcher()
    html = panel.render_shell("<p>x</p>")
    assert "or-theme-toggle" not in html
    assert "orbit-theme" not in html


def test_register_render_hook_export() -> None:
    clear_render_hooks()
    register_render_hook("panels::body.start", lambda **_c: "START", scopes=["z"])
    html = Panel.make("z").render_shell("c")
    assert "START" in html


def test_mount_panel_applies_domain_and_auth_middleware() -> None:
    from almasix.orbit.panels.routing import mount_panel
    from almasix.routing import Router

    router = Router()
    panel = (
        Panel.make("dom")
        .path("dom")
        .domain("admin.test")
        .middleware(["web"], replace=True)
        .auth_middleware(["auth"])
        .login(False)
        .dashboard(False)
    )
    mount_panel(router, panel)
    home = next(r for r in router.routes if getattr(r, "route_name", None) == "orbit.dom.home")
    assert getattr(home, "domain_pattern", None) == "admin.test"
    mw = list(getattr(home, "middleware_names", []) or [])
    assert "web" in mw and "auth" in mw


def test_panel_configuration_edge_cases() -> None:
    clear_render_hooks()
    panel = (
        Panel.make("edge")
        .path("/")
        .domain(None)
        .home_url(None)
        .favicon(None)
        .auth_middleware(["a"])
        .auth_middleware(["a", "b"])  # append + dedupe
        .sidebar_navigation()
        .widgets([])
    )
    assert panel.get_path() == "/"
    assert panel.get_domain() is None
    assert panel.get_home_url() == "/"
    assert panel.get_favicon_url() is None
    assert panel.get_auth_middleware() == ["a", "b"]
    assert panel.get_widgets() == []
    html = panel.render_shell("<p>x</p>")
    assert "or-app-sidebar" in html

    # Plugin objects without register/boot still run callbacks.
    class _Bare:
        def get_id(self) -> str:
            return "bare"

    bare = _Bare()
    flags: list[str] = []
    Panel.make("p2").plugin(bare).plugin(lambda _p: flags.append("cb")).run_plugins()
    assert flags == ["cb"]

    empty = PanelRegistry()
    assert empty.get_default() is None
    only = Panel.make("only")
    empty.register(only)
    assert empty.get_default() is only
    # Second non-default panel must not steal the default slot.
    second = Panel.make("second")
    empty.register(second)
    assert empty.get_default() is only


def test_panel_theme_package_and_stylesheet(tmp_path, monkeypatch) -> None:
    from almasix.orbit.panels import discover as discover_mod

    themes = tmp_path / "themes_pkg"
    themes.mkdir()
    (themes / "__init__.py").write_text("", encoding="utf-8")
    (themes / "brand.css").write_text(":root { --or-primary: #112233; }\n", encoding="utf-8")
    (themes / "_skip.css").write_text("/* ignored */\n", encoding="utf-8")

    import sys
    import types

    pkg = types.ModuleType("orbit_test_themes")
    pkg.__path__ = [str(themes)]  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "orbit_test_themes", pkg)

    panel = (
        Panel.make("themed")
        .theme_package("orbit_test_themes")
        .theme_stylesheet("/vendor/custom.css")
        .theme_package("missing.package.ignored")
    )
    html = panel.render_shell("<p>x</p>")
    assert 'data-orbit-theme="orbit_test_themes:brand.css"' in html
    assert "--or-primary: #112233" in html
    assert "_skip.css" not in html
    assert 'href="/vendor/custom.css"' in html

    # Helper returns empty for missing packages
    assert discover_mod.load_theme_css("does.not.exist") == []


def test_discover_panel_dirs_wires_theme_package() -> None:
    panel = Panel.make("admin").discover_panel_dirs()
    assert "app.orbit.admin.resources" in panel._discover_resources_in
    assert "app.orbit.admin.themes" in panel._theme_packages
