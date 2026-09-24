---
title: Time picker
description: TimePicker uses Orbit’s time stepper by default (or a native time input) and stores HH:mm or HH:mm:ss.
---

## Introduction

`TimePicker` stores a time-of-day as `HH:mm` (or `HH:mm:ss` with `.seconds()`). The default UI is Orbit’s stepper popover with optional 12-hour display. Call `.native(True)` for `<input type="time">`.

## Basic time picker

```python title="app/orbit/resources/example_resource.py"
TimePicker.make('remind_at')
    .label('Remind at')
```

![Orbit Basic time picker (light)](/examples/light/forms/time-picker/basic.png)

![Orbit Basic time picker (dark)](/examples/dark/forms/time-picker/basic.png)

## Twelve-hour display and minute step

```python title="app/orbit/resources/example_resource.py"
TimePicker.make('opens_at')
    .label('Opens at')
    .hours12()
    .minute_step(15)
```

![Orbit Twelve-hour display (light)](/examples/light/forms/time-picker/hours12.png)

![Orbit Twelve-hour display (dark)](/examples/dark/forms/time-picker/hours12.png)

## Seconds

```python title="app/orbit/resources/example_resource.py"
TimePicker.make('exact')
    .label('Exact time')
    .seconds()
```

![Orbit Seconds (light)](/examples/light/forms/time-picker/seconds.png)

![Orbit Seconds (dark)](/examples/dark/forms/time-picker/seconds.png)

## Native browser input

```python title="app/orbit/resources/example_resource.py"
TimePicker.make('slot')
    .label('Time slot')
    .native(True)
    .min_date('08:00')
    .max_date('18:00')
```

![Orbit Native time (light)](/examples/light/forms/time-picker/native.png)

![Orbit Native time (dark)](/examples/dark/forms/time-picker/native.png)
