"""Packaging guards — Orbit must not clobber the Almasix framework namespace."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"


def test_orbit_packages_do_not_ship_almasix_root_init() -> None:
    """Orbit wheels used to ship ``almasix/__init__.py`` (namespace stub).

    Pip installs that file over the framework's ``almasix/__init__.py``, which
    drops ``__version__`` and breaks Smith commands (``version``, ``list``,
    introspection). See GitHub issue #24.
    """
    offenders = sorted(PACKAGES.glob("*/src/almasix/__init__.py"))
    assert offenders == [], (
        "Do not ship packages/*/src/almasix/__init__.py — it overwrites the "
        f"framework namespace init. Found: {offenders}"
    )


def test_orbit_subpackages_still_present() -> None:
    assert (PACKAGES / "panels" / "src" / "almasix" / "orbit" / "__init__.py").is_file()
    assert (PACKAGES / "support" / "src" / "almasix" / "orbit" / "__init__.py").is_file()
