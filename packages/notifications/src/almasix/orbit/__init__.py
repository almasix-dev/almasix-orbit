"""Orbit namespace (split across packages via pkgutil.extend_path).

Thin inits re-export the panels public API when installed so language servers
that resolve *this* file (instead of panels') still autocomplete ``Panel.*``.
"""

from __future__ import annotations

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

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
except ImportError:  # panels package not installed alongside this contrib
    pass
