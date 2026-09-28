"""Load CalendarJS and the Alpine host when a panel boots."""

from __future__ import annotations

from pathlib import Path

from almasix.orbit.panels.hooks import Plugin

_ASSETS = Path(__file__).resolve().parent / "assets"
_CALENDAR_JS = "https://cdn.jsdelivr.net/npm/@calendarjs/ce@1.1.0/dist/index.min.js"
_CALENDAR_CSS = "https://cdn.jsdelivr.net/npm/@calendarjs/ce@1.1.0/dist/style.min.css"
_LEMONADE = "https://cdn.jsdelivr.net/npm/lemonadejs@5.3.6/dist/lemonade.min.js"


def _asset(name: str) -> str:
    return (_ASSETS / name).read_text(encoding="utf-8")


class CalendarPlugin(Plugin):
    """Styles and scripts for ``CalendarView``. Register with ``panel.plugin``."""

    def __init__(self) -> None:
        super().__init__("orbit-calendar")

    def boot(self, panel: object) -> None:
        render_hook = getattr(panel, "render_hook", None)
        if not callable(render_hook):
            return
        css = _asset("orbit-calendar.css").replace("</style>", "<\\/style>")
        script = _asset("orbit-calendar.js").replace("</script>", "<\\/script>")
        render_hook(
            "panels::styles.after",
            lambda **_ctx: (
                f'  <link rel="stylesheet" href="{_CALENDAR_CSS}" />\n'
                f"  <style>{css}</style>\n"
            ),
        )
        render_hook(
            "panels::scripts.after",
            lambda **_ctx: (
                f'  <script src="{_LEMONADE}"></script>\n'
                f'  <script src="{_CALENDAR_JS}"></script>\n'
                f"  <script>{script}</script>\n"
            ),
        )
