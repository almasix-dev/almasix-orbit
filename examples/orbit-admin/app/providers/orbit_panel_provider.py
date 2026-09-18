"""Register every panel defined under ``app/orbit/*/panel.py``."""

from __future__ import annotations

from almasix.orbit import PanelRegistry
from almasix.orbit.panels.discover import register_app_orbit_panels
from almasix.providers import ServiceProvider


class OrbitPanelProvider(ServiceProvider):
    def boot(self) -> None:
        register_app_orbit_panels(self.app.make(PanelRegistry))
