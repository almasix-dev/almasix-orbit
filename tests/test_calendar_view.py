"""CalendarJS schedule widget and the panel plugin that loads it."""

from __future__ import annotations

from almasix.orbit.calendar import CalendarPlugin, CalendarView
from almasix.orbit.panels.hooks import clear_render_hooks, render_hook
from almasix.orbit.panels.panel import Panel


def test_a_schedule_renders_events_and_the_plugin_loads_calendarjs() -> None:
    clear_render_hooks()
    html = (
        CalendarView.make("leave")
        .date("2026-03-16")
        .view("month")
        .readonly(False)
        .navigate("/leave-calendar?month={month}")
        .range("2026-03-01", "2026-03-31")
        .events(
            [
                {"title": "", "date": "2026-03-16", "start": "08:00"},
                {"title": "Skip", "date": "nope", "start": "08:00"},
                {"title": "Skip", "date": "2026-03-16", "start": "8"},
                {
                    "guid": "evt-1",
                    "title": "Ada <b>",
                    "date": "2026-03-16",
                    "start": "08:00",
                    "end": "17:00",
                    "color": "red",
                    "readonly": False,
                    "description": "Approved",
                },
                {"title": "No end", "date": "2026-03-17", "start": "09:00", "color": "#46341c"},
            ]
        )
        .render()
    )
    assert 'data-orbit-schedule="leave"' in html
    assert "or-schedule-card" in html
    assert "or-schedule-picker" in html
    assert "March 2026" in html
    assert 'data-view="day"' in html
    assert 'data-view="weekdays"' in html
    assert "orbitSchedule" in html
    assert 'data-view="week" class="or-schedule-view is-active"' in html or "is-active" in html
    assert "evt-1" in html
    assert "\\u003cb" in html
    assert "#efaf5d" in html
    assert "#46341c" in html
    assert '"readonly": false' in html
    assert '"view": "week"' in html
    assert "2026-03-01" in html
    assert '"navigate": "/leave-calendar?month={month}"' in html

    bare = CalendarView.make("").date("bad").readonly().render()
    assert 'data-orbit-schedule="schedule"' in bare
    assert '"navigate": ""' in bare
    assert '"range": null' in bare
    assert '"view": "week"' in bare

    CalendarPlugin().boot(object())
    panel = Panel.make("demo")
    CalendarPlugin().boot(panel)
    styles = render_hook("panels::styles.after", scope="demo")
    scripts = render_hook("panels::scripts.after", scope="demo")
    assert "@calendarjs/ce@1.1.0/dist/style.min.css" in styles
    assert ".or-schedule-board" in styles
    assert "lemonadejs@5.3.6" in scripts
    assert "@calendarjs/ce@1.1.0/dist/index.min.js" in scripts
    assert "orbitSchedule" in scripts
    assert "window.fetch" in scripts
    assert '["00:00", "08:00"]' in scripts
    assert '["17:00", "24:00"]' in scripts
    assert "window.location" not in scripts
    assert scripts.count("</script>") == 3
    clear_render_hooks()
