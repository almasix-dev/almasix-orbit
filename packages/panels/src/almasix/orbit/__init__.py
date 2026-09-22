"""Orbit — Filament-power for Almasix (panels meta package)."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from almasix.orbit.panels.auth import Login, MfaChallenge, Register
from almasix.orbit.panels.cluster import Cluster
from almasix.orbit.panels.hooks import PANEL_HOOKS, Plugin, register_render_hook
from almasix.orbit.panels.mfa import AppAuthentication, EmailAuthentication
from almasix.orbit.panels.navigation import (
    NavigationBuilder,
    NavigationGroup,
    NavigationItem,
    NavigationSubgroup,
)
from almasix.orbit.panels.page import Page
from almasix.orbit.panels.pages.dashboard import Dashboard
from almasix.orbit.panels.panel import Panel, PanelRegistry
from almasix.orbit.panels.relation_manager import RelationManager
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.users import OrbitUser, PanelNotification, UserMenuItem

__version__ = "0.4.2"

__all__ = [
    "__version__",
    "Panel",
    "PanelRegistry",
    "Resource",
    "Page",
    "Dashboard",
    "Login",
    "Register",
    "MfaChallenge",
    "AppAuthentication",
    "EmailAuthentication",
    "RelationManager",
    "Cluster",
    "NavigationItem",
    "NavigationGroup",
    "NavigationSubgroup",
    "NavigationBuilder",
    "OrbitUser",
    "UserMenuItem",
    "PanelNotification",
    "Plugin",
    "PANEL_HOOKS",
    "register_render_hook",
]
