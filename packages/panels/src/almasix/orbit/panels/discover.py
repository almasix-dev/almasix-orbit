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
    if not hasattr(package, "__path__"):  # pragma: no cover - namespace packages only
        return _classes_from_module(package, base_class, seen)
    prefix = package.__name__ + "."
    for mod in pkgutil.walk_packages(package.__path__, prefix):
        try:
            module = importlib.import_module(mod.name)
        except Exception:  # pragma: no cover - broken modules skipped
            continue
        out.extend(_classes_from_module(module, base_class, seen))
    return out


def _load_module_file(path: Path, base_class: type[Any], seen: set[type[Any]]) -> list[type[Any]]:
    import importlib.util

    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:  # pragma: no cover - invalid paths
        return []
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:  # pragma: no cover - broken module body
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
        if value in seen:  # pragma: no cover - duplicate class across modules
            continue
        seen.add(value)
        out.append(value)
    return out
