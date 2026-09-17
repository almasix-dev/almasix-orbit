"""Default panel Dashboard page."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit.panels.page import Page
from almasix.orbit.support.html import e


class Dashboard(Page):
    """Default first page for a panel (home route ``/``)."""

    title = "Dashboard"
    slug = "dashboard"
    navigation_icon: ClassVar[str] = "heroicon-o-home"
    navigation_label: ClassVar[str | None] = "Dashboard"
    # Own sidebar root (apps layout) — not the ungrouped "Menu" bucket.
    navigation_group: ClassVar[str | None] = "Dashboard"
    navigation_sort: ClassVar[int] = -100

    @classmethod
    def render(cls, **ctx: Any) -> str:
        widgets = ctx.get("widgets") or []
        body = ""
        if widgets:
            cards = "".join(
                f'<div class="or-widget">{w}</div>' if isinstance(w, str) else ""
                for w in widgets
            )
            body = f'<div class="or-dashboard-widgets">{cards}</div>'
        else:
            brand = e(str(ctx.get("brand") or "Orbit"))
            body = (
                f'<p class="or-muted">Welcome to {brand}. '
                f"Register resources or customize this dashboard.</p>"
            )
        return (
            f'<div class="or-page or-page-dashboard">'
            f'<h1 class="or-page-title">{e(cls.get_title())}</h1>'
            f"{body}"
            f"</div>"
        )
