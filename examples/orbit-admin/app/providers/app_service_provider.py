"""Host application provider."""

from __future__ import annotations

from pathlib import Path

from almasix.providers import ServiceProvider

_REPO = Path(__file__).resolve().parents[4]
_CSS = _REPO / "packages" / "panels" / "src" / "almasix" / "orbit" / "resources" / "css" / "orbit.css"
_JS = _REPO / "packages" / "panels" / "src" / "almasix" / "orbit" / "resources" / "js" / "orbit.js"


class AppServiceProvider(ServiceProvider):
    def boot(self) -> None:
        # Ensure vendor assets exist for local demo without vendor:publish.
        dest_css = Path(self.app.path("public", "vendor", "orbit", "orbit.css"))
        dest_js = Path(self.app.path("public", "vendor", "orbit", "orbit.js"))
        dest_css.parent.mkdir(parents=True, exist_ok=True)
        if _CSS.is_file():
            dest_css.write_bytes(_CSS.read_bytes())
        if _JS.is_file():
            dest_js.write_bytes(_JS.read_bytes())
