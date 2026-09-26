"""Orbit namespace — support package."""

from __future__ import annotations

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

__version__ = "0.4.4"

try:
    from almasix.orbit.panels.navigation import NavigationGroup as NavigationGroup
    from almasix.orbit.panels.navigation import NavigationItem as NavigationItem
    from almasix.orbit.panels.page import Page as Page
    from almasix.orbit.panels.panel import Panel as Panel
    from almasix.orbit.panels.panel import PanelRegistry as PanelRegistry
    from almasix.orbit.panels.relation_manager import RelationManager as RelationManager
    from almasix.orbit.panels.resource import Resource as Resource
    from almasix.orbit.panels.users import OrbitUser as OrbitUser
    from almasix.orbit.panels.users import PanelNotification as PanelNotification
    from almasix.orbit.panels.users import UserMenuItem as UserMenuItem
except ImportError:  # pragma: no cover - panels package optional for support-only installs
    pass

__all__ = ["__version__"]
