"""Server render for a CalendarJS schedule mounted by Alpine."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any, Self

_DAY = re.compile(r"\d{4}-\d{2}-\d{2}")
_TIME = re.compile(r"\d{2}:\d{2}")
_HEX = re.compile(r"#[0-9A-Fa-f]{6}")
_VIEWS = {"day", "week", "weekdays"}
_APPROVED = "#efaf5d"
_MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def schedule_event(row: dict[str, Any]) -> dict[str, Any] | None:
    """One CalendarJS event, or nothing when the date or title is missing."""
    title = str(row.get("title") or "").strip()
    day = str(row.get("date") or "")[:10]
    start = str(row.get("start") or "")
    start = start[:5]
    if not title or _DAY.fullmatch(day) is None or _TIME.fullmatch(start) is None:
        return None
    event: dict[str, Any] = {
        "guid": str(row.get("guid") or f"{day}-{start}-{title}")[:80],
        "title": title,
        "date": day,
        "start": start,
        "color": _color(row.get("color")),
        "readonly": bool(row.get("readonly", True)),
    }
    end = str(row.get("end") or "")[:5]
    if _TIME.fullmatch(end):
        event["end"] = end
    for key in ("description", "location", "type", "url"):
        text = str(row.get(key) or "").strip()
        if text:
            event[key] = text
    return event


def _color(value: Any) -> str:
    text = str(value or "")
    if _HEX.fullmatch(text):
        return text
    return _APPROVED


class CalendarView:
    """A day or week board. Apps pass events; CalendarJS draws them."""

    def __init__(self, name: str) -> None:
        self._name = name or "schedule"
        self._date = ""
        self._view = "week"
        self._events: list[dict[str, Any]] = []
        self._readonly = True
        self._navigate = ""
        self._range: list[str] | None = None

    @classmethod
    def make(cls, name: str) -> CalendarView:
        return cls(name)

    def date(self, value: str) -> Self:
        self._date = str(value or "")
        return self

    def view(self, value: str) -> Self:
        self._view = str(value or "")
        return self

    def events(self, rows: list[dict[str, Any]]) -> Self:
        self._events = [event for row in rows if (event := schedule_event(row)) is not None]
        return self

    def readonly(self, enabled: bool = True) -> Self:
        self._readonly = enabled
        return self

    def navigate(self, template: str) -> Self:
        """URL with ``{month}`` and ``{date}``. Leaving ``range`` fetches it, without reloading the page."""
        self._navigate = template
        return self

    def range(self, start: str, end: str) -> Self:
        self._range = [str(start), str(end)]
        return self

    def render(self) -> str:
        view = self._view if self._view in _VIEWS else "week"
        day = self._date if _DAY.fullmatch(self._date) else datetime.now(UTC).date().isoformat()
        payload = {
            "name": self._name,
            "date": day,
            "view": view,
            "readonly": self._readonly,
            "navigate": self._navigate,
            "range": self._range,
            "events": self._events,
        }
        raw = json.dumps(payload).replace("<", "\\u003c")
        month_label = f"{_MONTHS[int(day[5:7]) - 1]} {day[:4]}"
        buttons = []
        for name, label in (("day", "Day"), ("week", "Week"), ("weekdays", "Weekdays")):
            active = " is-active" if name == view else ""
            buttons.append(
                f'<button type="button" class="or-schedule-view{active}" data-view="{name}">{label}</button>'
            )
        toolbar = (
            '<div class="or-schedule-toolbar" role="toolbar" aria-label="Schedule views">'
            '<button type="button" data-shift="-1">Previous</button>'
            f"{''.join(buttons)}"
            '<button type="button" data-shift="1">Next</button>'
            "</div>"
        )
        return (
            f'<div class="or-schedule" x-data="orbitSchedule" data-orbit-schedule="{self._name}">'
            '<div class="or-schedule-card">'
            '<div class="or-schedule-layout">'
            '<aside class="or-schedule-picker" aria-label="Choose a date">'
            f'<p class="or-schedule-month">{month_label}</p>'
            '<div class="or-schedule-picker-board"></div>'
            "</aside>"
            '<div class="or-schedule-main">'
            f"{toolbar}"
            '<div class="or-schedule-board"></div>'
            "</div>"
            "</div>"
            "</div>"
            f'<script type="application/json" class="or-schedule-data">{raw}</script>'
            "</div>"
        )
