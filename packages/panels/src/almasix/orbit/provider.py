"""Orbit service provider."""

from __future__ import annotations

from pathlib import Path

from almasix.providers import ServiceProvider

_HERE = Path(__file__).resolve().parent


class OrbitServiceProvider(ServiceProvider):
    """Registers Orbit assets, panel discovery, smith commands, and route mounts."""

    def register(self) -> None:
        from almasix.orbit.panels.panel import PanelRegistry

        if not self.app.config.has("orbit"):
            self.app.config.set(
                "orbit",
                {
                    "path": "/admin",
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
                / "orbit.js": self.app.path("public", "vendor", "orbit", "orbit.js"),
                _HERE
                / "resources"
                / "js"
                / "orbit-datepicker.js": self.app.path(
                    "public", "vendor", "orbit", "orbit-datepicker.js"
                ),
            },
            "orbit-assets",
        )
        self.publishes(
            {
                _HERE
                / "resources"
                / "vendor"
                / "chart.umd.min.js": self.app.path(
                    "public", "vendor", "orbit", "chart.umd.min.js"
                ),
                _HERE
                / "resources"
                / "vendor"
                / "apexcharts.min.js": self.app.path(
                    "public", "vendor", "orbit", "apexcharts.min.js"
                ),
                _HERE
                / "resources"
                / "vendor"
                / "filepond.bundle.min.js": self.app.path(
                    "public", "vendor", "orbit", "filepond.bundle.min.js"
                ),
                _HERE
                / "resources"
                / "vendor"
                / "filepond.bundle.min.css": self.app.path(
                    "public", "vendor", "orbit", "filepond.bundle.min.css"
                ),
                _HERE
                / "resources"
                / "vendor"
                / "cropper.min.js": self.app.path(
                    "public", "vendor", "orbit", "cropper.min.js"
                ),
                _HERE
                / "resources"
                / "vendor"
                / "cropper.min.css": self.app.path(
                    "public", "vendor", "orbit", "cropper.min.css"
                ),
                _HERE
                / "resources"
                / "vendor"
                / "flowbite-datepicker.min.js": self.app.path(
                    "public", "vendor", "orbit", "flowbite-datepicker.min.js"
                ),
                _HERE
                / "resources"
                / "vendor"
                / "flowbite-datepicker.min.css": self.app.path(
                    "public", "vendor", "orbit", "flowbite-datepicker.min.css"
                ),
            },
            "orbit-assets",
        )
        try:
            from almasix.orbit.panels.commands import ORBIT_COMMANDS

            self.commands(ORBIT_COMMANDS)
        except Exception:  # pragma: no cover
            pass
        self._register_directives()
        self._mount_assets()
        self._mount_panels()

    def _mount_assets(self) -> None:
        try:
            from almasix.orbit.panels.routing import mount_orbit_assets
            from almasix.routing import get_router

            mount_orbit_assets(get_router())
        except Exception:  # pragma: no cover
            pass

    def _mount_panels(self) -> None:
        try:
            from almasix.orbit.panels.routing import mount_registered_panels

            mount_registered_panels(self.app)
        except Exception:  # pragma: no cover
            pass

    def _register_directives(self) -> None:
        try:
            from almasix.prism.engine import Engine

            if not self.app.container.bound(Engine):
                return
            engine = self.app.make(Engine)
            if engine is None:
                return
        except Exception:  # pragma: no cover
            return

        def styles_directive(_expr: str) -> str:
            return "__w(context.get('__orbit_styles', lambda: '')())"

        def scripts_directive(_expr: str) -> str:
            return "__w(context.get('__orbit_scripts', lambda: '')())"

        try:
            engine.directive("orbitStyles", styles_directive)
            engine.directive("orbitScripts", scripts_directive)
        except Exception:  # pragma: no cover
            return
