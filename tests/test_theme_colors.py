"""Tests for panel theme color resolution and shell injection."""

from __future__ import annotations

import re
from pathlib import Path

from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.theme_colors import (
    DEFAULT_PRIMARY,
    resolve_panel_color_vars,
)
from almasix.orbit.support.colors import Color, Colors


def test_resolve_panel_color_vars_defaults() -> None:
    vars_ = resolve_panel_color_vars({})
    assert vars_ == {"--or-primary": DEFAULT_PRIMARY}
    assert DEFAULT_PRIMARY == Colors.MAP[Color.PRIMARY]


def test_resolve_panel_color_vars_semantic_and_extra() -> None:
    vars_ = resolve_panel_color_vars(
        {"primary": "#2563eb", "danger": "#dc2626", "unknown": "#000"}
    )
    assert vars_["--or-primary"] == "#2563eb"
    assert vars_["--or-danger"] == "#dc2626"
    assert "--or-unknown" not in vars_


def test_panel_brand_name_font_size_injects_css_var() -> None:
    panel = Panel.make("admin").brand_name_font_size("1.25rem")
    html = panel.render_shell("<div class='or-page'>x</div>")
    assert "--or-brand-name-size: 1.25rem" in html
    assert panel.to_dict()["brand_name_font_size"] == "1.25rem"


def test_panel_primary_injects_css_var() -> None:
    panel = Panel.make("admin").primary("#2563eb")
    html = panel.render_shell("<div class='or-page'>x</div>")
    assert "--or-primary: #2563eb" in html
    assert panel.to_dict()["colors"]["primary"] == "#2563eb"


def test_panel_primary_accepts_semantic_token() -> None:
    panel = Panel.make("admin").primary("info")
    html = panel.render_shell("<div class='or-page'>x</div>")
    assert f"--or-primary: {Colors.MAP[Color.INFO]}" in html


def test_panel_colors_injects_danger() -> None:
    panel = Panel.make("admin").colors(danger="#dc2626")
    html = panel.render_shell("<div class='or-page'>x</div>")
    assert f"--or-primary: {DEFAULT_PRIMARY}" in html
    assert "--or-danger: #dc2626" in html


def test_css_derives_primary_soft_deep() -> None:
    css = Path("packages/panels/src/almasix/orbit/resources/css/orbit.css").read_text(
        encoding="utf-8"
    )
    assert "--or-primary-soft: color-mix(in srgb, var(--or-primary)" in css
    assert "--or-primary-deep: color-mix(in srgb, var(--or-primary)" in css


def test_css_native_controls_use_primary_accent() -> None:
    css = Path("packages/panels/src/almasix/orbit/resources/css/orbit.css").read_text(
        encoding="utf-8"
    )
    for selector in (".or-checkbox", ".or-toggle", ".or-radio", ".or-row-check"):
        assert selector in css
    # Accent block for form/table native controls
    assert re.search(
        r"\.or-checkbox,\s*\n\s*\.or-toggle,\s*\n\s*\.or-radio\s*\{[^}]*accent-color:\s*var\(--or-primary\)",
        css,
    )
    assert ".or-badge.or-color-primary" in css
    assert "background: color-mix(in srgb, var(--or-primary)" in css
