"""Host application provider."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from almasix.orbit.forms import FilesystemUploadStorage, set_upload_storage
from almasix.providers import ServiceProvider


def _copy_vendor(dest_dir: Path) -> None:
    """Copy Orbit CSS/JS (+ FilePond) from the installed ``almasix-orbit`` wheel."""
    root = resources.files("almasix.orbit")
    mapping = (
        ("resources/css/orbit.css", "orbit.css"),
        ("resources/js/orbit.js", "orbit.js"),
        ("resources/vendor/filepond.bundle.min.js", "filepond.bundle.min.js"),
        ("resources/vendor/filepond.bundle.min.css", "filepond.bundle.min.css"),
    )
    for rel, name in mapping:
        src = root.joinpath(rel)
        if src.is_file():
            (dest_dir / name).write_bytes(src.read_bytes())


class AppServiceProvider(ServiceProvider):
    def boot(self) -> None:
        dest_dir = Path(self.app.path("public", "vendor", "orbit"))
        dest_dir.mkdir(parents=True, exist_ok=True)
        try:
            _copy_vendor(dest_dir)
        except Exception:
            pass

        storage_root = Path(self.app.path("storage", "app"))
        storage_root.mkdir(parents=True, exist_ok=True)
        set_upload_storage(FilesystemUploadStorage(base_url="/storage"))
