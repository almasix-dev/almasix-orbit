---
title: Time picker
description: TimePicker is a native time input sharing DatePicker min/max and display-format helpers.
---

## Introduction

`TimePicker` subclasses `DatePicker` with `type="time"`. Use it for opening hours, shift starts, and time-only preferences. Min/max accept time strings such as `09:00` / `17:30`.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic time picker

Renders a browser time control. Dehydrated values follow the browser’s time string (often `HH:MM`).

```python title="app/orbit/resources/example_resource.py"
TimePicker.make('opens_at')
    .label('Opens at')
```

![Orbit Basic time picker (light)](/examples/light/forms/time-picker/basic.png)

![Orbit Basic time picker (dark)](/examples/dark/forms/time-picker/basic.png)

## Bounded range

Constrain selectable times with `.min_date()` / `.max_date()` (same helpers as DatePicker — they emit `min`/`max` regardless of date vs time).

```python title="app/orbit/resources/example_resource.py"
TimePicker.make('closes_at')
    .label('Closes at')
    .min_date('09:00')
    .max_date('17:00')
```

![Orbit Bounded range (light)](/examples/light/forms/time-picker/min-max.png)

![Orbit Bounded range (dark)](/examples/dark/forms/time-picker/min-max.png)

## Display format hint

`.display_format()` stores a client hint on `data-display-format` without server-side reformatting.

```python title="app/orbit/resources/example_resource.py"
TimePicker.make('reminder_at')
    .label('Reminder')
    .display_format('H:i')
```

![Orbit Display format hint (light)](/examples/light/forms/time-picker/display-format.png)

![Orbit Display format hint (dark)](/examples/dark/forms/time-picker/display-format.png)

## Step and input mode

Inherited Field helpers `.step()` and `.input_mode()` emit attributes on the control when you need minute granularity or a numeric keypad. Pair with `.required()` for mandatory windows.

```python title="app/orbit/resources/example_resource.py"
TimePicker.make('break_at')
    .label('Break')
    .step(300)
    .required()
```

![Orbit Step and input mode (light)](/examples/light/forms/time-picker/step.png)

![Orbit Step and input mode (dark)](/examples/dark/forms/time-picker/step.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
