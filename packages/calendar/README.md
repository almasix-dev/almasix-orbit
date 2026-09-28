# Orbit calendar

A panel plugin and a `CalendarView` widget. The widget renders a day, week, or weekday schedule by wrapping [CalendarJS](https://calendarjs.com/) (`@calendarjs/ce`) in an Alpine component.

Register it on a panel:

```python
from almasix.orbit.calendar import CalendarPlugin, CalendarView

panel.plugin(CalendarPlugin())
```

```python
CalendarView.make("leave").date("2026-03-16").view("week").readonly().events([
    {
        "guid": "leave-1",
        "title": "Ada Lovelace · Annual",
        "date": "2026-03-16",
        "start": "08:00",
        "end": "17:00",
        "color": "#efaf5d",
        "description": "Approved · Full day",
    }
]).render()
```

`CalendarPlugin` adds the CalendarJS stylesheet and script, plus the Alpine host `orbitSchedule`. The page does not load those assets by itself.

This package is self-contained under `almasix.orbit.calendar`. It can move to its own repository without changes to the other Orbit packages: publish the folder, depend on `almasix-orbit-panels`, and keep the `panel.plugin(CalendarPlugin())` call in each app.
