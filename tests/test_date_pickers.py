"""Coverage for Flowbite date/time picker fields and temporal validation."""

from __future__ import annotations

from datetime import date, datetime

from almasix.orbit.forms import (
    DatePicker,
    DateTimePicker,
    Form,
    MonthPicker,
    TimePicker,
    WeekPicker,
    YearPicker,
)
from almasix.orbit.forms.form import _parse_temporal, _resolve_temporal_bound


def test_flowbite_date_picker_host_attrs() -> None:
    html = (
        DatePicker.make("d")
        .min_date("2020-01-01")
        .max_date("2030-12-31")
        .label("Joined")
        .render("2024-06-01")
    )
    assert "or-datepicker" in html
    assert 'data-mode="date"' in html
    assert "orbitDatePicker" in html
    assert 'type="hidden"' in html
    assert 'value="2024-06-01"' in html
    # Static aria-label — must not be an Alpine expression binding.
    assert 'aria-label="Joined"' in html
    assert ":aria-label=" not in html


def test_datetime_aria_label_not_alpine_expression() -> None:
    html = DateTimePicker.make("reviewed_at").label("Reviewed at").render()
    assert 'aria-label="Reviewed at"' in html
    assert 'aria-label="reviewed_at time"' in html
    assert ":aria-label=" not in html


def test_datetime_time_apis_and_native() -> None:
    dt = (
        DateTimePicker.make("at")
        .seconds()
        .hours12()
        .minute_step(10)
        .render("2024-01-01T09:00:00")
    )
    assert 'data-mode="datetime"' in dt
    assert 'data-seconds="true"' in dt
    assert 'data-time-format="12"' in dt
    assert 'data-minute-step="10"' in dt
    assert "or-timepicker" in dt

    assert 'data-time-format="24"' in DateTimePicker.make("at2").hours24().render()
    assert 'data-seconds="false"' in DateTimePicker.make("at3").seconds(False).render()
    assert DateTimePicker.make("at4").time_format("bogus")._time_format is None
    assert DateTimePicker.make("at5").minute_step("nope")._minute_step == 5

    native = TimePicker.make("t").native(True).seconds().render("09:00:00")
    assert 'type="time"' in native
    assert 'step="1"' in native or "step=" in native

    # Time-only Flowbite host has no calendar block.
    time_host = TimePicker.make("t2").hours12().render("09:30")
    assert 'data-mode="time"' in time_host
    assert "or-datepicker__host" not in time_host
    assert "or-timepicker" in time_host

    native_bounds = (
        DatePicker.make("d2")
        .native(True)
        .min_date("2020-01-01")
        .max_date("2030-12-31")
        .display_format("Y-m-d")
        .render("2024-06-01")
    )
    assert 'max="2030-12-31"' in native_bounds
    assert 'data-display-format="Y-m-d"' in native_bounds

    # Seconds without `_step` still emits step="1" on native time inputs.
    step_fallback = TimePicker.make("t3").native(True)
    step_fallback._seconds = True
    step_fallback._step = None
    assert 'step="1"' in step_fallback.render("09:00:00")


def test_week_month_year_modes() -> None:
    assert 'data-mode="week"' in WeekPicker.make("w").render("2024-01-01")
    assert 'data-mode="month"' in MonthPicker.make("m").render("2024-01-01")
    assert 'data-mode="year"' in YearPicker.make("y").render("2024")
    assert 'type="week"' in WeekPicker.make("w").native(True).render()
    assert 'type="month"' in MonthPicker.make("m").native(True).render()
    assert 'type="number"' in YearPicker.make("y").native(True).render("2024")


def test_after_or_equal_and_time_ordering() -> None:
    form = Form.make("f").schema(
        [
            DatePicker.make("starts").rules("date", "after_or_equal:2020-01-01"),
            DatePicker.make("ends").rules(
                "date", "before_or_equal:2030-12-31", "date_equals:2025-06-15"
            ),
            DatePicker.make("cap").rules("date", "before_or_equal:2030-12-31"),
            TimePicker.make("opens").rules("after:08:00", "before:18:00"),
            DateTimePicker.make("when").rules("after:2024-01-01T08:00"),
            YearPicker.make("yr").rules("after_or_equal:2020", "before:2030"),
            DatePicker.make("rel").rules("after:starts"),
        ]
    )
    assert form.validate({"starts": "2019-12-31"}) != {}
    assert form.validate({"starts": "2020-01-01"}) == {}
    assert form.validate({"ends": "2025-06-15"}) == {}
    assert form.validate({"ends": "2025-06-16"}) != {}
    assert form.validate({"cap": "2031-01-01"}) != {}
    assert form.validate({"opens": "07:30"}) != {}
    assert form.validate({"opens": "09:00"}) == {}
    assert form.validate({"when": "2024-01-01T07:00"}) != {}
    assert form.validate({"when": "2024-01-01T09:00"}) == {}
    assert form.validate({"yr": "2019"}) != {}
    assert form.validate({"yr": "2024"}) == {}
    assert form.validate({"starts": "2024-01-01", "rel": "2023-12-31"}) != {}
    assert form.validate({"starts": "2024-01-01", "rel": "2024-06-01"}) == {}


def test_temporal_parse_helpers() -> None:
    assert _resolve_temporal_bound("", {}) is None
    assert _resolve_temporal_bound("nope", {"nope": "still-nope"}) is None
    # Literal-shaped key that fails to parse, then falls back to state.
    assert _resolve_temporal_bound("25:00", {"25:00": "10:00"}) == datetime(
        1970, 1, 1, 10, 0
    )
    assert _parse_temporal("25:00") is None
    assert _parse_temporal("2024") == datetime(2024, 1, 1)
    assert _parse_temporal(date(2024, 6, 1)) == datetime(2024, 6, 1)
    assert _parse_temporal(datetime(2024, 6, 1, 12, 0)) == datetime(2024, 6, 1, 12, 0)
