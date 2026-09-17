"""Host routes — Orbit mounts under /admin via OrbitServiceProvider."""

from __future__ import annotations

from typing import Any

from almasix.http import html
from almasix.routing import Route


async def home() -> Any:
    return html(
        "<!DOCTYPE html><html><body style='font-family:Outfit,sans-serif;padding:2rem'>"
        "<h1>Orbit Admin demo</h1>"
        "<p>Host route at <code>/</code> is untouched. "
        "<a href='/admin'>Open admin panel →</a></p>"
        "</body></html>"
    )


Route.get("/", home)
