"""Host application provider."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from almasix.orbit.forms import FilesystemUploadStorage, set_upload_storage
from almasix.providers import ServiceProvider


def _copy_vendor(dest_dir: Path) -> None:
    """Copy Orbit CSS/JS (+ FilePond / Flowbite datepicker) from the installed wheel."""
    root = resources.files("almasix.orbit")
    mapping = (
        ("resources/css/orbit.css", "orbit.css"),
        ("resources/js/orbit.js", "orbit.js"),
        ("resources/js/orbit-datepicker.js", "orbit-datepicker.js"),
        ("resources/vendor/filepond.bundle.min.js", "filepond.bundle.min.js"),
        ("resources/vendor/filepond.bundle.min.css", "filepond.bundle.min.css"),
        ("resources/vendor/flowbite-datepicker.min.js", "flowbite-datepicker.min.js"),
        ("resources/vendor/flowbite-datepicker.min.css", "flowbite-datepicker.min.css"),
    )
    for rel, name in mapping:
        src = root.joinpath(rel)
        if src.is_file():
            (dest_dir / name).write_bytes(src.read_bytes())


def _register_catalog_notification_observers() -> None:
    from app.models.album import Album
    from app.models.artist import Artist
    from app.models.track import Track
    from app.orbit.demo.catalog_notifications import CatalogNotificationObserver

    observer = CatalogNotificationObserver()
    Artist.observe(observer)
    Album.observe(observer)
    Track.observe(observer)


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
        public_root = storage_root / "public"
        public_root.mkdir(parents=True, exist_ok=True)
        link = Path(self.app.path("public", "storage"))
        if not link.exists():
            try:
                link.symlink_to(public_root, target_is_directory=True)
            except OSError:
                pass
        set_upload_storage(FilesystemUploadStorage(base_url="/storage"))

        try:
            _register_catalog_notification_observers()
        except Exception:
            pass
