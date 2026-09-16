"""Orbit service provider."""

from __future__ import annotations

from pathlib import Path

from almasix.providers import ServiceProvider

_HERE = Path(__file__).resolve().parent


class OrbitServiceProvider(ServiceProvider):
    """Registers Orbit assets, panel discovery, and smith commands."""

    def register(self) -> None:
        from almasix.orbit.panels.panel import PanelRegistry

        if not self.app.config.has("orbit"):
            self.app.config.set(
                "orbit",
                {
                    "path": "/orbit",
                    "font": "Outfit",
                    "brand": "Orbit",
                },
            )
        if not self.app.container.bound(PanelRegistry):
            self.app.container.instance(PanelRegistry, PanelRegistry())

    def boot(self) -> None:
        self.publishes(
            {
                _HERE
                / "resources"
                / "css"
                / "orbit.css": self.app.path("public", "vendor", "orbit", "orbit.css")
            },
            "orbit-assets",
        )
        self.publishes(
            {
                _HERE
                / "resources"
                / "js"
                / "orbit.js": self.app.path("public", "vendor", "orbit", "orbit.js")
            },
            "orbit-assets",
        )
        try:
            from almasix.orbit.panels.commands import MakeOrbitResourceCommand

            self.commands([MakeOrbitResourceCommand])
        except Exception:  # pragma: no cover
            pass
        self._register_directives()

    def _register_directives(self) -> None:
        try:
            from almasix.prism.engine import Engine

            if not self.app.container.bound(Engine):
                return
            engine = self.app.make(Engine)
        except Exception:  # pragma: no cover
            return

        def styles_directive(_expr: str) -> str:
            return "__w(context.get('__orbit_styles', lambda: '')())"

        def scripts_directive(_expr: str) -> str:
            return "__w(context.get('__orbit_scripts', lambda: '')())"

        engine.directive("orbitStyles", styles_directive)
        engine.directive("orbitScripts", scripts_directive)
