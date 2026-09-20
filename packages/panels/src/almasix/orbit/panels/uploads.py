"""Panel upload endpoint — validates against the field, then stores the file.

The browser never dictates where a file lands: the endpoint looks the
``FileUpload`` field up on the resource's own form and uses *its* disk, directory,
size limits, and accepted types.
"""

from __future__ import annotations

from typing import Any

from almasix.orbit.forms.uploads import (
    UploadRejected,
    UploadRules,
    delete_upload,
    store_upload,
)
from almasix.orbit.forms.walk import iter_fields


def find_upload_field(panel: Any, resource_slug: str, field_name: str) -> Any | None:
    """Locate the ``FileUpload`` field named ``field_name`` on a panel resource."""
    if not field_name:
        return None
    for resource in panel.get_resources():
        if resource_slug and str(resource.get_slug()) != str(resource_slug):
            continue
        try:
            form = resource.get_form()
        except Exception:
            continue
        for field in iter_fields(form.get_components()):
            if field.__class__.__name__ != "FileUpload":
                continue
            if (field.get_state_path() or field.get_name()) == field_name:
                return field
    return None


def upload_rules_for(panel: Any, resource_slug: str, field_name: str) -> UploadRules | None:
    field = find_upload_field(panel, resource_slug, field_name)
    if field is None:
        return None
    return field.get_upload_rules()


async def handle_upload(
    panel: Any,
    *,
    resource: str,
    field: str,
    filename: str,
    data: bytes,
) -> dict[str, Any]:
    """Store one uploaded file; returns a JSON-ready payload."""
    rules = upload_rules_for(panel, resource, field)
    if rules is None:
        return {"ok": False, "error": f"Unknown upload field '{field}'."}
    if not data:
        return {"ok": False, "error": "No file was uploaded."}
    try:
        stored = await store_upload(data, filename, rules)
    except UploadRejected as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "file": stored.to_dict()}


async def handle_upload_delete(
    panel: Any,
    *,
    resource: str,
    field: str,
    path: str,
) -> dict[str, Any]:
    """Remove a previously stored file."""
    rules = upload_rules_for(panel, resource, field)
    if rules is None:
        return {"ok": False, "error": f"Unknown upload field '{field}'."}
    if not path:
        return {"ok": False, "error": "No file path given."}
    await delete_upload(path, rules)
    return {"ok": True, "path": path}


def panel_upload_url(panel: Any) -> str:
    """URL of this panel's upload endpoint."""
    return _upload_url(str(panel.get_path()))


def resource_upload_url(resource: Any) -> str:
    """Upload endpoint for the panel a resource is mounted on."""
    return _upload_url(str(getattr(resource, "_panel_path", "") or ""))


def _upload_url(panel_path: str) -> str:
    prefix = panel_path.rstrip("/")
    return f"{prefix}/orbit-upload" if prefix and prefix != "/" else "/orbit-upload"
