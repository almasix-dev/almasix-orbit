"""Schedule view for Orbit panels, ready to live in its own package."""

from almasix.orbit.calendar.plugin import CalendarPlugin
from almasix.orbit.calendar.view import CalendarView, schedule_event

__all__ = ["CalendarPlugin", "CalendarView", "schedule_event"]
