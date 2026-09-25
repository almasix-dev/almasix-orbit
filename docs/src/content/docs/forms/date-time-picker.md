---
title: Date-time picker
description: DateTimePicker combines a Flowbite calendar with a time stepper; values store as local datetime-local strings.
---

## Introduction

`DateTimePicker` stores a local date and time as `YYYY-MM-DDTHH:mm` (add seconds with `.seconds()` → `…:ss`). The default UI is a Flowbite calendar plus Orbit’s time stepper (12/24-hour display, minute step, Now/Clear). Call `.native(True)` for `<input type="datetime-local">`.

## Basic date-time

```python title="app/orbit/resources/example_resource.py"
DateTimePicker.make('published_at')
    .label('Published at')
```

![Orbit Basic date time (light)](/examples/light/forms/date-time-picker/basic.png)

![Orbit Basic date time (dark)](/examples/dark/forms/date-time-picker/basic.png)

## Seconds and clock format

`.seconds()` includes seconds in the stored value and stepper. `.hours12()` / `.hours24()` control display only — storage stays 24-hour. `.minute_step(n)` sets the minute nudge interval (default 5, or 1 when seconds are on).

```python title="app/orbit/resources/example_resource.py"
DateTimePicker.make('starts_at')
    .label('Starts at')
    .seconds()
    .hours12()
    .minute_step(5)
```

![Orbit Seconds and clock format (light)](/examples/light/forms/date-time-picker/seconds.png)

![Orbit Seconds and clock format (dark)](/examples/dark/forms/date-time-picker/seconds.png)

## Bounded range

`.min_date()` / `.max_date()` accept date or datetime strings and bind the calendar.

```python title="app/orbit/resources/example_resource.py"
DateTimePicker.make('scheduled')
    .label('Scheduled')
    .min_date('2026-01-01')
    .max_date('2026-12-31T23:59')
```

![Orbit Bounded range (light)](/examples/light/forms/date-time-picker/min-max.png)

![Orbit Bounded range (dark)](/examples/dark/forms/date-time-picker/min-max.png)

## Native browser input

```python title="app/orbit/resources/example_resource.py"
DateTimePicker.make('published_at')
    .label('Published at')
    .native(True)
```

![Orbit Native date-time (light)](/examples/light/forms/date-time-picker/native.png)

![Orbit Native date-time (dark)](/examples/dark/forms/date-time-picker/native.png)
