---
title: Time picker
description: TimePicker is a native time input for reminders, slots, and office hours.
---

## Introduction

TimePicker is a native time input for reminders, slots, and office hours. Min/max attributes bound acceptable times.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic time picker

![Orbit Basic time picker (light)](/examples/light/forms/time-picker/basic.png)

![Orbit Basic time picker (dark)](/examples/dark/forms/time-picker/basic.png)

HH:MM time selection.

```python
TimePicker.make('remind_at')
    .label('Remind at')
```

## Time window

![Orbit Time window (light)](/examples/light/forms/time-picker/min-max.png)

![Orbit Time window (dark)](/examples/dark/forms/time-picker/min-max.png)

Business-hours style constraints.

```python
TimePicker.make('slot')
    .label('Time slot')
    .min_date('08:00')
    .max_date('18:00')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
