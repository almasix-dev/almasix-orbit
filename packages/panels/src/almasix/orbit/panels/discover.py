"""Filesystem discovery helpers for panel resources/pages/widgets."""

from __future__ import annotations

import importlib
import pkgutil
import re
import warnings
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

    v0.3 colocated convention (preferred)::

        app/orbit/admin/panel.py → ``register_admin_panel``
        app/orbit/app/panel.py   → ``register_app_panel``

    Legacy (deprecated)::

        app/orbit/admin_panel.py → ``register_admin_panel``

    Skips the reserved ``shared`` package. Returns panels from registrars
    (may include ``None``).
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
    seen_ids: set[str] = set()

    for modinfo in pkgutil.iter_modules(paths, prefix):
        name = modinfo.name.rsplit(".", 1)[-1]
        if name.startswith("_") or name in {"shared", "fields"}:
            continue

        # v0.3: app.orbit.<id> package with nested panel.py
        if modinfo.ispkg and not name.endswith("_panel"):
            panel_mod_name = f"{modinfo.name}.panel"
            try:
                module = importlib.import_module(panel_mod_name)
            except ImportError:
                continue
            panel_id = name
            if panel_id in seen_ids:
                continue
            panel = _call_panel_registrar(module, panel_id, registry)
            if panel is not None or callable(getattr(module, f"register_{panel_id}_panel", None)):
                seen_ids.add(panel_id)
                _wire_default_discovery(panel, package=package, panel_id=panel_id)
                registered.append(panel)
            continue

        # Legacy: app.orbit.<id>_panel module
        if not name.endswith("_panel"):
            continue
        panel_id = name[: -len("_panel")]
        warnings.warn(
            f"Legacy panel module {modinfo.name!r} is deprecated; "
            f"move to {package}.{panel_id}.panel "
            f"(app/orbit/{panel_id}/panel.py). Will be removed in Orbit 0.4.",
            DeprecationWarning,
            stacklevel=2,
        )
        try:
            module = importlib.import_module(modinfo.name)
        except Exception:
            continue
        if panel_id in seen_ids:
            continue
        panel = _call_panel_registrar(module, panel_id, registry)
        if panel is not None or callable(getattr(module, f"register_{panel_id}_panel", None)):
            seen_ids.add(panel_id)
            registered.append(panel)

    return registered
