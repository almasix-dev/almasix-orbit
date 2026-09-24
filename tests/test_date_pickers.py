"""Coverage for Flowbite date/time picker fields and temporal validation."""

from __future__ import annotations

from almasix.orbit.forms import (
    DatePicker,
    DateTimePicker,
    Form,
    MonthPicker,
    TimePicker,
    WeekPicker,
    YearPicker,
)


def test_flowbite_date_picker_host_attrs() -> None:
    html = (
        DatePicker.make("d")
        .min_date("2020-01-01")
        .max_date("2030-12-31")
        .render("2024-06-01")
    )
    assert "or-datepicker" in html
    assert 'data-mode="date"' in html
    assert "orbitDatePicker" in html
    assert 'type="hidden"' in html
    assert 'value="2024-06-01"' in html


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

    native = TimePicker.make("t").native(True).seconds().render("09:00:00")
    assert 'type="time"' in native
    assert 'step="1"' in native or "step=" in native


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
            DatePicker.make("ends").rules("date", "before_or_equal:2030-12-31", "date_equals:2025-06-15"),
            TimePicker.make("opens").rules("after:08:00", "before:18:00"),
            DateTimePicker.make("when").rules("after:2024-01-01T08:00"),
        ]
    )
    assert form.validate({"starts": "2019-12-31"}) != {}
    assert form.validate({"starts": "2020-01-01"}) == {}
    assert form.validate({"ends": "2025-06-15"}) == {}
    assert form.validate({"ends": "2025-06-16"}) != {}
    assert form.validate({"opens": "07:30"}) != {}
    assert form.validate({"opens": "09:00"}) == {}
    assert form.validate({"when": "2024-01-01T07:00"}) != {}
    assert form.validate({"when": "2024-01-01T09:00"}) == {}
