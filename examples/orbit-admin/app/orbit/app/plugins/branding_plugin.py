"""Panel Configuration showcase plugins for orbit-admin."""

from __future__ import annotations

from typing import Any

from almasix.orbit.panels.hooks import Plugin


class BrandingPlugin(Plugin):
    """Demonstrates ``Plugin.register`` / ``boot`` on the admin panel."""

    def __init__(self) -> None:
        super().__init__("orbit-admin-branding")
        self.booted = False

    def register(self, panel: Any) -> None:
        # Keep register lightweight — mutate panel config only if unset.
        if not getattr(panel, "_favicon", None):
            panel.favicon("images/favicon.svg")

    def boot(self, panel: Any) -> None:
        self.booted = True
        panel.render_hook(
            "panels::styles.after",
            lambda **_ctx: "<!-- orbit-admin BrandingPlugin booted -->\n",
        )
