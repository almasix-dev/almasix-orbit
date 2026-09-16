"""Smith command stubs for Orbit scaffolding."""

from __future__ import annotations

from typing import Any


class MakeOrbitResourceCommand:
    """``smith make:orbit-resource`` — generates a Resource class stub."""

    name = "make:orbit-resource"
    signature = "make:orbit-resource {name}"
    description = "Create a new Orbit resource class"

    def handle(self, *args: Any, **kwargs: Any) -> int:
        name = kwargs.get("name") or (args[0] if args else None)
        if not name:
            return 1
        return 0
