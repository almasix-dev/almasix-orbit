"""Scaffold a third-party Orbit plugin package and marketplace YAML."""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import almasix.orbit.__main__ as orbit_main  # noqa: F401 — coverage for python -m entry
from almasix.orbit.panels.commands import ORBIT_COMMANDS, MakeOrbitPluginCommand
from almasix.orbit.panels.plugin_scaffold import (
    PluginScaffoldError,
    kebab,
    main,
    parse_plugin_spec,
    resolve_root,
    run_new,
    studly,
    write_scaffold,
)


def test_kebab_and_studly() -> None:
    assert kebab("AuditLog") == "audit-log"
    assert kebab("acme_orbit_kit") == "acme-orbit-kit"
    assert studly("audit-log") == "AuditLog"


def test_parse_class_name_from_feature() -> None:
    spec = parse_plugin_spec("AuditLog", vendor="acme", author="jane")
    assert spec.package == "acme-orbit-audit-log"
    assert spec.slug == "acme-audit-log"
    assert spec.module == "acme_orbit_audit_log"
    assert spec.class_name == "AuditLogPlugin"
    assert spec.plugin_id == "acme-audit-log"
    assert spec.author == "jane"
    assert spec.category == "developer-tool"
    assert spec.orbit_line == "0.4"


def test_parse_distribution_name() -> None:
    spec = parse_plugin_spec("acme-orbit-branding")
    assert spec.package == "acme-orbit-branding"
    assert spec.slug == "acme-branding"
    assert spec.vendor == "acme"
    assert spec.class_name == "BrandingPlugin"


def test_parse_package_override_and_paid() -> None:
    spec = parse_plugin_spec(
        "kit",
        vendor="zen",
        package="zen-orbit-kit",
        category="theme",
        paid=True,
    )
    assert spec.package == "zen-orbit-kit"
    assert spec.slug == "zen-kit"
    assert spec.paid is True
    assert spec.category == "theme"


def test_parse_rejects_empty_and_reserved() -> None:
    try:
        parse_plugin_spec("")
        raise AssertionError("expected empty name to fail")
    except PluginScaffoldError as exc:
        assert "required" in str(exc)
    try:
        parse_plugin_spec("almasix-orbit-branding")
        raise AssertionError("expected reserved prefix to fail")
    except PluginScaffoldError as exc:
        assert "reserved" in str(exc)
    try:
        parse_plugin_spec("kit", vendor="almasix")
        raise AssertionError("expected almasix vendor to fail")
    except PluginScaffoldError as exc:
        assert "almasix" in str(exc)
    try:
        parse_plugin_spec("using", package="using")
        raise AssertionError("expected reserved slug to fail")
    except PluginScaffoldError as exc:
        assert "reserved" in str(exc)
    try:
        parse_plugin_spec("kit", package="almasix-orbit-kit")
        raise AssertionError("expected reserved package to fail")
    except PluginScaffoldError as exc:
        assert "almasix-orbit" in str(exc)
    try:
        parse_plugin_spec("kit", category="not-a-category")
        raise AssertionError("expected unknown category to fail")
    except PluginScaffoldError as exc:
        assert "unknown category" in str(exc)
    try:
        parse_plugin_spec("9bad")
        raise AssertionError("expected invalid slug to fail")
    except PluginScaffoldError as exc:
        assert "kebab-case" in str(exc)


def test_resolve_root_uses_package_dir_or_explicit_name(tmp_path: Path) -> None:
    spec = parse_plugin_spec("AuditLog", vendor="acme")
    nested = resolve_root(tmp_path, spec, listing_only=False)
    assert nested == tmp_path / spec.package
    listed = resolve_root(tmp_path, spec, listing_only=True)
    assert listed == tmp_path.resolve()
    named = tmp_path / spec.package
    named.mkdir()
    assert resolve_root(named, spec, listing_only=False) == named.resolve()
    slug_dir = tmp_path / spec.slug
    slug_dir.mkdir()
    assert resolve_root(slug_dir, spec, listing_only=False) == slug_dir.resolve()


def test_write_scaffold_package_and_listing(tmp_path: Path) -> None:
    spec = parse_plugin_spec("AuditLog", vendor="acme", author="jane")
    written = write_scaffold(spec, path=tmp_path)
    root = tmp_path / spec.package
    paths = {path.relative_to(root).as_posix() for path in written}
    assert "pyproject.toml" in paths
    assert f"src/{spec.module}/plugin.py" in paths
    assert f"marketplace/{spec.slug}.yaml" in paths
    assert f"marketplace/{spec.author}.yaml" in paths
    plugin_src = (root / "src" / spec.module / "plugin.py").read_text(encoding="utf-8")
    assert spec.class_name in plugin_src
    yaml = (root / "marketplace" / f"{spec.slug}.yaml").read_text(encoding="utf-8")
    assert "price: free" in yaml
    assert "status: draft" in yaml

    sys.path.insert(0, str(root / "src"))
    try:
        mod = __import__(spec.module)
        plugin = mod.AuditLogPlugin()
        from almasix.orbit import Panel

        panel = Panel.make("admin").path("admin")
        plugin.register(panel)
        plugin.boot(panel)
        assert plugin.get_id() == spec.plugin_id
    finally:
        sys.path.pop(0)
        sys.modules.pop(spec.module, None)
        sys.modules.pop(f"{spec.module}.plugin", None)


def test_write_scaffold_listing_only_paid_and_no_listing(tmp_path: Path) -> None:
    spec = parse_plugin_spec("ProKit", vendor="zen", author="zen", paid=True, category="panel-kit")
    listed = write_scaffold(spec, path=tmp_path, listing_only=True)
    assert any(path.name == f"{spec.slug}.yaml" for path in listed)
    assert not (tmp_path / spec.package / "pyproject.toml").exists()
    paid_yaml = next(path for path in listed if path.name == f"{spec.slug}.yaml").read_text(
        encoding="utf-8"
    )
    assert "checkout_url:" in paid_yaml
    assert "amount: 29" in paid_yaml

    spec_free = parse_plugin_spec("Notes", vendor="zen")
    only_pkg = write_scaffold(spec_free, path=tmp_path, no_listing=True)
    pkg_root = tmp_path / spec_free.package
    assert (pkg_root / "pyproject.toml").is_file()
    assert not (pkg_root / "marketplace").exists()
    assert any(path.name == "plugin.py" for path in only_pkg)

    try:
        write_scaffold(spec_free, path=tmp_path, listing_only=True, no_listing=True)
        raise AssertionError("expected combined flags to fail")
    except PluginScaffoldError as exc:
        assert "cannot combine" in str(exc)


def test_write_scaffold_refuses_existing_without_force(tmp_path: Path) -> None:
    spec = parse_plugin_spec("AuditLog", vendor="acme")
    write_scaffold(spec, path=tmp_path)
    try:
        write_scaffold(spec, path=tmp_path)
        raise AssertionError("expected existing files to fail")
    except PluginScaffoldError as exc:
        assert "--force" in str(exc)
    again = write_scaffold(spec, path=tmp_path, force=True)
    assert again


def test_cli_new_and_errors(tmp_path: Path) -> None:
    assert (
        main(
            [
                "plugin",
                "new",
                "AuditLog",
                "--vendor",
                "acme",
                "--author",
                "jane",
                "--path",
                str(tmp_path),
            ]
        )
        == 0
    )
    assert (tmp_path / "acme-orbit-audit-log" / "pyproject.toml").is_file()

    orig = sys.stdout
    missing = io.StringIO()
    sys.stdout = missing
    try:
        assert main(["plugin", "new"]) == 2
    finally:
        sys.stdout = orig
    assert "name is required" in missing.getvalue()

    bad = io.StringIO()
    sys.stdout = bad
    try:
        assert main(["plugin", "new", "AuditLog", "--category", "nope", "--path", str(tmp_path)]) == 1
    finally:
        sys.stdout = orig
    assert "unknown category" in bad.getvalue()

    assert main(["--help"]) == 0
    assert main(["plugin"]) == 2


def test_cli_run_new_missing_name_message() -> None:
    buf = io.StringIO()
    ns = argparse.Namespace(
        name="",
        author="",
        vendor="",
        package="",
        category="developer-tool",
        path=".",
        paid=False,
        listing_only=False,
        no_listing=False,
        force=False,
    )
    assert run_new(ns, stdout=buf) == 2
    assert "name is required" in buf.getvalue()


def test_smith_command_writes_and_validates(tmp_path: Path) -> None:
    names = {cls.name() for cls in ORBIT_COMMANDS}
    assert "make:orbit-plugin" in names
    aliases = {a for cls in ORBIT_COMMANDS for a in cls.aliases}
    assert "orbit:plugin" in aliases

    assert MakeOrbitPluginCommand().handle() == 2

    cmd = MakeOrbitPluginCommand()
    cmd._options = {
        "author": "jane",
        "vendor": "acme",
        "path": str(tmp_path),
        "category": "developer-tool",
        "force": False,
        "paid": False,
        "listing-only": False,
        "no-listing": False,
    }
    assert cmd.handle(name="AuditLog") == 0
    assert (tmp_path / "acme-orbit-audit-log" / "README.md").is_file()

    listed = MakeOrbitPluginCommand()
    listed._options = {
        "author": "jane",
        "vendor": "acme",
        "path": str(tmp_path / "yaml-only"),
        "listing-only": True,
        "force": True,
        "category": "developer-tool",
    }
    assert listed.handle(name="AuditLog") == 0
    assert list((tmp_path / "yaml-only" / "marketplace").glob("*.yaml"))

    boom = MakeOrbitPluginCommand()
    boom._options = {"package": "using", "path": str(tmp_path)}
    assert boom.handle(name="using") == 1
