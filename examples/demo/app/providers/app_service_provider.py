"""Host application provider."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from almasix.providers import ServiceProvider


def _copy_vendor(dest_css: Path, dest_js: Path) -> None:
    """Copy Orbit CSS/JS from the installed ``almasix-orbit`` wheel."""
    root = resources.files("almasix.orbit")
    css = root.joinpath("resources/css/orbit.css")
    js = root.joinpath("resources/js/orbit.js")
    if css.is_file():
        dest_css.write_bytes(css.read_bytes())
    if js.is_file():
        dest_js.write_bytes(js.read_bytes())


class AppServiceProvider(ServiceProvider):
    def boot(self) -> None:
        dest_css = Path(self.app.path("public", "vendor", "orbit", "orbit.css"))
        dest_js = Path(self.app.path("public", "vendor", "orbit", "orbit.js"))
        dest_css.parent.mkdir(parents=True, exist_ok=True)
        try:
            _copy_vendor(dest_css, dest_js)
        except Exception:
            pass
