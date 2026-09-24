"""Host routes — Orbit mounts at ``/``; extras live under ``/__orbit-demo/``."""

from __future__ import annotations

import hmac

from almasix.config import env
from almasix.console import Smith
from almasix.http import json
from almasix.routing import Route


def _bearer_token(request: object | None) -> str:
    if request is None:
        return ""
    headers = getattr(request, "headers", None)
    if headers is None:
        return ""
    getter = getattr(headers, "get", None)
    if not callable(getter):
        return ""
    header = str(getter("Authorization") or getter("authorization") or "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return ""


async def reset_catalog(request: object | None = None) -> object:
    """Soft-reset catalog + notifications (preserves users / sessions).

    Authenticate with header ``Authorization: Bearer <DEMO_RESET_TOKEN>``.
    """
    expected = str(env("DEMO_RESET_TOKEN", "") or "")
    if not expected:
        return json(
            {"ok": False, "error": "DEMO_RESET_TOKEN not configured"},
            status=503,
        )

    provided = _bearer_token(request)
    if not provided or not hmac.compare_digest(provided, expected):
        return json({"ok": False, "error": "unauthorized"}, status=401)

    code = Smith.call("demo:reset")
    if code not in (0, None):
        return json(
            {"ok": False, "error": "demo:reset failed", "code": code},
            status=500,
        )
    return json({"ok": True, "message": "catalog reset"})


async def reset_status(_request: object | None = None) -> object:
    configured = bool(str(env("DEMO_RESET_TOKEN", "") or ""))
    return json({"ok": True, "reset_token_configured": configured})


with Route.group(prefix="/__orbit-demo"):
    Route.post("/reset", reset_catalog)
    Route.get("/reset-status", reset_status)
