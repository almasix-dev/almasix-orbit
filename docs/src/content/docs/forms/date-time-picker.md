---
title: Date time picker
description: DateTimePicker combines calendar date and time in one datetime-local control.
---

## Introduction

DateTimePicker combines calendar date and time in one datetime-local control. Share min/max with DatePicker for scheduling windows.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic date time

Publish or schedule timestamps.

```python
DateTimePicker.make('published_at')
    .label('Published at')
```

![Orbit Basic date time (light)](/examples/light/forms/date-time-picker/basic.png)

![Orbit Basic date time (dark)](/examples/dark/forms/date-time-picker/basic.png)

## Bounded range

Limit selectable datetime window.

```python
DateTimePicker.make('scheduled')
    .label('Scheduled')
    .min_date('2026-01-01')
    .max_date('2026-12-31')
```

![Orbit Bounded range (light)](/examples/light/forms/date-time-picker/min-max.png)

![Orbit Bounded range (dark)](/examples/dark/forms/date-time-picker/min-max.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
