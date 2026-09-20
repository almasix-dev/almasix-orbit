"""Upload storage contract behind ``FileUpload``.

A panel posts the selected file to its upload endpoint; that endpoint validates it
against the field's own configuration and hands it to an :class:`UploadStorage`.
Swap the storage to send files anywhere — the default writes through Almasix's
filesystem disks, and an in-memory implementation keeps tests and demos honest.
"""

from __future__ import annotations

import posixpath
import re
import uuid
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any, Protocol, runtime_checkable


class UploadRejected(Exception):
    """Raised when a file fails the field's own upload rules."""


@dataclass
class StoredUpload:
    """One file that made it into storage."""

    path: str
    name: str
    size: int = 0
    mime: str = ""
    url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "name": self.name,
            "size": self.size,
            "mime": self.mime,
            "url": self.url or self.path,
        }


@dataclass
class UploadRules:
    """Server-side constraints read off the ``FileUpload`` field."""

    disk: str | None = None
    directory: str | None = None
    visibility: str | None = None
    preserve_filenames: bool = False
    max_size: int | None = None
    min_size: int | None = None
    accepted_types: list[str] = dataclass_field(default_factory=list)


@runtime_checkable
class UploadStorage(Protocol):
    """Where accepted files end up."""

    async def store(self, data: bytes, filename: str, rules: UploadRules) -> StoredUpload: ...

    async def delete(self, path: str, rules: UploadRules) -> bool: ...


class MemoryUploadStorage:
    """Keeps files in a dict — the default until an app configures a disk."""

    def __init__(self, base_url: str = "/storage") -> None:
        self.base_url = base_url.rstrip("/")
        self.files: dict[str, bytes] = {}

    async def store(self, data: bytes, filename: str, rules: UploadRules) -> StoredUpload:
        path = build_upload_path(filename, rules)
        self.files[path] = data
        return StoredUpload(
            path=path,
            name=filename,
            size=len(data),
            mime=guess_mime(filename),
            url=f"{self.base_url}/{path}",
        )

    async def delete(self, path: str, rules: UploadRules) -> bool:
        return self.files.pop(path, None) is not None


class FilesystemUploadStorage:
    """Writes through ``almasix.filesystem`` disks."""

    def __init__(self, base_url: str = "/storage") -> None:
        self.base_url = base_url.rstrip("/")

    async def store(self, data: bytes, filename: str, rules: UploadRules) -> StoredUpload:
        from almasix.filesystem import Storage

        path = build_upload_path(filename, rules)
        disk = Storage.disk(rules.disk)
        await _maybe_await(disk.put(path, data, visibility=rules.visibility))
        return StoredUpload(
            path=path,
            name=filename,
            size=len(data),
            mime=guess_mime(filename),
            url=_disk_url(disk, path, self.base_url),
        )

    async def delete(self, path: str, rules: UploadRules) -> bool:
        from almasix.filesystem import Storage

        disk = Storage.disk(rules.disk)
        await _maybe_await(disk.delete(path))
        return True


_storage: UploadStorage = MemoryUploadStorage()


def set_upload_storage(storage: UploadStorage) -> None:
    """Register the storage used by every panel upload endpoint."""
    global _storage
    _storage = storage


def get_upload_storage() -> UploadStorage:
    return _storage


async def store_upload(data: bytes, filename: str, rules: UploadRules) -> StoredUpload:
    """Validate ``data`` against ``rules``, then hand it to the registered storage."""
    validate_upload(data, filename, rules)
    return await _storage.store(data, sanitize_filename(filename), rules)


async def delete_upload(path: str, rules: UploadRules) -> bool:
    return await _storage.delete(path, rules)


def validate_upload(data: bytes, filename: str, rules: UploadRules) -> None:
    """Raise :class:`UploadRejected` when a file breaks the field's rules."""
    size_kb = len(data) / 1024
    if rules.max_size is not None and size_kb > rules.max_size:
        raise UploadRejected(f"{filename} is larger than {rules.max_size} KB.")
    if rules.min_size is not None and size_kb < rules.min_size:
        raise UploadRejected(f"{filename} is smaller than {rules.min_size} KB.")
    if rules.accepted_types and not matches_accepted_types(filename, rules.accepted_types):
        allowed = ", ".join(rules.accepted_types)
        raise UploadRejected(f"{filename} is not one of the accepted types ({allowed}).")


def matches_accepted_types(filename: str, accepted: list[str]) -> bool:
    """Match a filename against ``accept``-style entries (``image/*``, ``.pdf``)."""
    mime = guess_mime(filename)
    lowered = filename.lower()
    for entry in accepted:
        rule = str(entry).strip().lower()
        if not rule:
            continue
        if rule.startswith("."):
            if lowered.endswith(rule):
                return True
        elif rule.endswith("/*"):
            if mime.startswith(rule[:-1]):
                return True
        elif rule == mime:
            return True
    return False


def build_upload_path(filename: str, rules: UploadRules) -> str:
    """Directory + (optionally randomised) filename."""
    safe = sanitize_filename(filename)
    if not rules.preserve_filenames:
        suffix = posixpath.splitext(safe)[1]
        safe = f"{uuid.uuid4().hex}{suffix}"
    directory = (rules.directory or "").strip("/")
    return f"{directory}/{safe}" if directory else safe


def sanitize_filename(filename: str) -> str:
    """Strip directories and anything that is not filename-safe."""
    base = str(filename or "file").replace("\\", "/").rsplit("/", 1)[-1]
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-.")
    return cleaned or "file"


_MIME_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "svg": "image/svg+xml",
    "pdf": "application/pdf",
    "csv": "text/csv",
    "txt": "text/plain",
    "zip": "application/zip",
    "mp4": "video/mp4",
}


def guess_mime(filename: str) -> str:
    suffix = posixpath.splitext(str(filename or "").lower())[1].lstrip(".")
    return _MIME_TYPES.get(suffix, "application/octet-stream")


def is_image(path: str) -> bool:
    return guess_mime(path).startswith("image/")


def _disk_url(disk: Any, path: str, base_url: str) -> str:
    url_fn = getattr(disk, "url", None)
    if callable(url_fn):
        try:
            return str(url_fn(path))
        except Exception:
            pass
    return f"{base_url}/{path}"


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value
