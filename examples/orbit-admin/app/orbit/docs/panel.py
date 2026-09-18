"""Orbit panel: docs (minimal multi-panel guest shell)."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry


def register_docs_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("docs")
        .path("docs")
        .brand_name("Orbit Docs")
        .font("Outfit")
        .primary("#3b82f6")
        .login(False)
        .dashboard(False)
        .dark_mode()
        .theme_switcher(False)
        .default_theme_mode("light")
        .breadcrumbs_enabled(False)
        .discover_panel_dirs()
    )
    registry.register(panel)
    return panel
