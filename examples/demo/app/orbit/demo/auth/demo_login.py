"""Demo login — credentials prefilled for public visitors.

Lives outside ``pages/`` so ``discover_panel_dirs()`` does not register it as a
sidebar page (that produced a spurious “Menu” → ``/login`` root).
"""

from __future__ import annotations

from typing import Any

from almasix.orbit.panels.auth import Login
from almasix.orbit.support.html import e

DEMO_EMAIL = "demo@orbit.test"
DEMO_PASSWORD = "secret"


class DemoLogin(Login):
    """Sign-in page with Orbit Records demo credentials already filled in."""

    should_register_navigation = False

    @classmethod
    def render(cls, **ctx: Any) -> str:
        data = ctx.get("data")
        if not isinstance(data, dict):
            data = {}
        # Prefill only empty fields so a failed attempt keeps what the user typed.
        merged = {
            "email": str(data.get("email") or DEMO_EMAIL),
            "password": str(data.get("password") or DEMO_PASSWORD),
            "remember": bool(data.get("remember")),
        }
        html = super().render(**{**ctx, "data": merged})
        hint = (
            f'<p class="or-login-subtitle or-muted" style="margin-top:-0.5rem;">'
            f"Demo account prefilled: <code>{e(DEMO_EMAIL)}</code> / "
            f"<code>{e(DEMO_PASSWORD)}</code></p>"
        )
        # Insert the hint after the default subtitle block.
        marker = "</header>"
        if marker in html and "Demo account prefilled" not in html:
            html = html.replace(marker, f"{marker}{hint}", 1)
        return html
