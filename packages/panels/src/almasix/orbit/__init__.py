"""Orbit — Filament-power for Almasix (panels meta package)."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from almasix.orbit.panels.auth import Login, Register
from almasix.orbit.panels.navigation import NavigationGroup, NavigationItem
from almasix.orbit.panels.page import Page
from almasix.orbit.panels.pages.dashboard import Dashboard
from almasix.orbit.panels.panel import Panel, PanelRegistry
from almasix.orbit.panels.relation_manager import RelationManager
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.users import OrbitUser, PanelNotification, UserMenuItem

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "Panel",
    "PanelRegistry",
    "Resource",
    "Page",
    "Dashboard",
    "Login",
    "Register",
    "RelationManager",
    "NavigationItem",
    "NavigationGroup",
    "OrbitUser",
    "UserMenuItem",
    "PanelNotification",
]
