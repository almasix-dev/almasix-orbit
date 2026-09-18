"""Filesystem discovery helpers for panel resources/pages/widgets."""

from __future__ import annotations

import importlib
import pkgutil
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

    spec = importlib.util.spec_from_file_location(path.stem, path)
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


def register_app_orbit_panels(
    registry: Any,
    *,
    package: str = "app.orbit",
) -> list[Any]:
    """Import ``{package}.*_panel`` modules and call each ``register_*_panel``.

    Convention used by ``orbit:install`` / ``orbit:panel`` scaffolding:

    - ``app/orbit/admin_panel.py`` → ``register_admin_panel(registry)``
    - ``app/orbit/app_panel.py`` → ``register_app_panel(registry)``

    Returns the list of panels returned by those registrars (may include ``None``).
    """
    import re

    registered: list[Any] = []
    try:
        package_mod = importlib.import_module(package)
    except ImportError:
        return registered

    paths = getattr(package_mod, "__path__", None)
    if not paths:
        return registered

    prefix = package_mod.__name__ + "."
    for modinfo in pkgutil.iter_modules(paths, prefix):
        name = modinfo.name.rsplit(".", 1)[-1]
        if not name.endswith("_panel") or name.startswith("_"):
            continue
        try:
            module = importlib.import_module(modinfo.name)
        except Exception:
            continue
        panel_id = name[: -len("_panel")]
        fn_name = f"register_{panel_id}_panel"
        fn = getattr(module, fn_name, None)
        if not callable(fn):
            # Fall back: any register_*_panel in the module
            for attr, value in vars(module).items():
                if re.fullmatch(r"register_\w+_panel", attr) and callable(value):
                    fn = value
                    break
        if not callable(fn):
            continue
        registered.append(fn(registry))
    return registered
