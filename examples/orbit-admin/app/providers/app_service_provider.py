"""Host application provider."""

from __future__ import annotations

from pathlib import Path

from almasix.orbit.forms import FilesystemUploadStorage, set_upload_storage
from almasix.providers import ServiceProvider

_REPO = Path(__file__).resolve().parents[4]
_RES = _REPO / "packages" / "panels" / "src" / "almasix" / "orbit" / "resources"
_ASSETS = (
    (_RES / "css" / "orbit.css", "orbit.css"),
    (_RES / "js" / "orbit.js", "orbit.js"),
    (_RES / "js" / "orbit-datepicker.js", "orbit-datepicker.js"),
    (_RES / "vendor" / "flowbite-datepicker.min.js", "flowbite-datepicker.min.js"),
    (_RES / "vendor" / "flowbite-datepicker.min.css", "flowbite-datepicker.min.css"),
    (_RES / "vendor" / "filepond.bundle.min.js", "filepond.bundle.min.js"),
    (_RES / "vendor" / "filepond.bundle.min.css", "filepond.bundle.min.css"),
)


class AppServiceProvider(ServiceProvider):
    def boot(self) -> None:
        # Ensure vendor assets exist for local demo without vendor:publish.
        dest_dir = Path(self.app.path("public", "vendor", "orbit"))
        dest_dir.mkdir(parents=True, exist_ok=True)
        for src, name in _ASSETS:
            if src.is_file():
                (dest_dir / name).write_bytes(src.read_bytes())

        storage_root = Path(self.app.path("storage", "app"))
        storage_root.mkdir(parents=True, exist_ok=True)
        public_root = storage_root / "public"
        public_root.mkdir(parents=True, exist_ok=True)
        link = Path(self.app.path("public", "storage"))
        if not link.exists():
            try:
                link.symlink_to(public_root.resolve(), target_is_directory=True)
            except OSError:
                pass
        # Persist uploads on disk so avatar previews survive save/re-edit.
        set_upload_storage(FilesystemUploadStorage(base_url="/storage"))
