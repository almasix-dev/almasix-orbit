"""Filesystem discovery helpers for panel resources/pages/widgets."""

from __future__ import annotations

import importlib
import pkgutil
import re
from pathlib import Path
from types import ModuleType
from typing import Any


def discover_classes(
    *paths: str,
    base_class: type[Any],
) -> list[type[Any]]:
    """Import modules under ``paths`` and return subclasses of ``base_class``."""
    found: list[type[Any]] = []
    seen: set[type[Any]] = set()
    for path in paths:
        found.extend(_discover_in_path(path, base_class, seen))
    return found


def class_key(cls: type[Any]) -> str:
    """Stable identity for discovery dedupe (module + qualname)."""
    return f"{cls.__module__}.{cls.__qualname__}"


def load_theme_css(*packages: str) -> list[tuple[str, str]]:
    """Load ``*.css`` files from theme packages.

    Returns ``(source_id, css_text)`` pairs. ``source_id`` is
    ``{package}:{relative/path.css}`` for stable ``data-orbit-theme`` attrs.
    Missing packages are skipped (empty list contribution).
    """
    out: list[tuple[str, str]] = []
    for package in packages:
        pkg = str(package).strip()
        if not pkg:
            continue
        try:
            mod = importlib.import_module(pkg)
        except ImportError:
            continue
        paths = getattr(mod, "__path__", None)
        if not paths:
            continue
        for root in paths:
            root_p = Path(root)
            if not root_p.is_dir():
                continue
            for css in sorted(root_p.rglob("*.css")):
                if css.name.startswith("_"):
                    continue
                try:
                    text = css.read_text(encoding="utf-8")
                except OSError:
                    continue
                rel = css.relative_to(root_p).as_posix()
                out.append((f"{pkg}:{rel}", text))
    return out


def _discover_in_path(path: str, base_class: type[Any], seen: set[type[Any]]) -> list[type[Any]]:
    out: list[type[Any]] = []
    root = Path(path)
    if not root.exists():
        # Treat as dotted package name
        try:
            package = importlib.import_module(path)
        except ImportError:
            return out
        return _discover_in_package(package, base_class, seen)

    if root.is_file() and root.suffix == ".py":
        return _load_module_file(root, base_class, seen)

    for py in root.rglob("*.py"):
        if py.name.startswith("_"):
            continue
        out.extend(_load_module_file(py, base_class, seen))
    return out


def _discover_in_package(
    package: ModuleType, base_class: type[Any], seen: set[type[Any]]
) -> list[type[Any]]:
    out: list[type[Any]] = []
    if not hasattr(package, "__path__"):
        return _classes_from_module(package, base_class, seen)
    prefix = package.__name__ + "."
    for mod in pkgutil.walk_packages(package.__path__, prefix):
        try:
            module = importlib.import_module(mod.name)
        except Exception:
            continue
        out.extend(_classes_from_module(module, base_class, seen))
    return out


def _load_module_file(path: Path, base_class: type[Any], seen: set[type[Any]]) -> list[type[Any]]:
    import importlib.util

    # Prefer a stable dotted name from the path when under a known package root.
    mod_name = path.stem
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        return []
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        return []
    return _classes_from_module(module, base_class, seen)


def _classes_from_module(
    module: ModuleType, base_class: type[Any], seen: set[type[Any]]
) -> list[type[Any]]:
    out: list[type[Any]] = []
    for value in vars(module).values():
        if not isinstance(value, type):
            continue
        if value is base_class or not issubclass(value, base_class):
            continue
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _call_panel_registrar(module: ModuleType, panel_id: str, registry: Any) -> Any:
    fn_name = f"register_{panel_id}_panel"
    fn = getattr(module, fn_name, None)
    if not callable(fn):
        for attr, value in vars(module).items():
            if re.fullmatch(r"register_\w+_panel", attr) and callable(value):
                fn = value
                break
    if not callable(fn):
        return None
    return fn(registry)


def _wire_default_discovery(panel: Any, *, package: str, panel_id: str) -> None:
    """If the panel has no discover paths yet, point at colocated dirs."""
    if panel is None:
        return
    has_paths = bool(
        getattr(panel, "_discover_resources_in", None)
        or getattr(panel, "_discover_pages_in", None)
        or getattr(panel, "_discover_widgets_in", None)
    )
    if has_paths:
        return
    wire = getattr(panel, "discover_panel_dirs", None)
    if callable(wire):
        wire(f"{package}.{panel_id}")


def register_app_orbit_panels(
    registry: Any,
    *,
    package: str = "app.orbit",
) -> list[Any]:
    """Import panel modules under ``package`` and call each ``register_*_panel``.

    Colocated convention (v0.3+)::

        app/orbit/admin/panel.py → ``register_admin_panel``
        app/orbit/app/panel.py   → ``register_app_panel``

    Flat ``app/orbit/{id}_panel.py`` modules are ignored (removed in 0.4).
    Skips reserved packages (``shared``, ``fields``, ``plugins``) that are not
    panels. Plugins are never auto-discovered — register with ``Panel.plugin``.
    Returns panels from registrars (may include ``None``).
    """
    registered: list[Any] = []
    try:
        package_mod = importlib.import_module(package)
    except ImportError:
        return registered

    paths = getattr(package_mod, "__path__", None)
    if not paths:
        return registered

    prefix = package_mod.__name__ + "."
    _reserved = frozenset({"shared", "fields", "plugins"})

    for modinfo in pkgutil.iter_modules(paths, prefix):
        name = modinfo.name.rsplit(".", 1)[-1]
        if name.startswith("_") or name in _reserved:
            continue
        if not modinfo.ispkg:
            continue
        panel_mod_name = f"{modinfo.name}.panel"
        try:
            module = importlib.import_module(panel_mod_name)
        except ImportError:
            continue
        panel_id = name
        panel = _call_panel_registrar(module, panel_id, registry)
        if panel is not None or callable(getattr(module, f"register_{panel_id}_panel", None)):
            _wire_default_discovery(panel, package=package, panel_id=panel_id)
            registered.append(panel)

    return registered
