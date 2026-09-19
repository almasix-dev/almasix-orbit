---
title: Date time picker
description: DateTimePicker combines calendar date and time in one native datetime-local control with Orbit field chrome.
---

## Introduction

`DateTimePicker` subclasses `DatePicker` and sets `type="datetime-local"`. Orbit wraps the native browser control with the same label, hint, helper, prefix/suffix, and validation surface as other fields. Values dehydrate as strings the browser emits (typically `YYYY-MM-DDTHH:MM`). Use min/max for scheduling windows, `display_format` for client hint metadata, and shared Field helpers for required/disabled/live behavior.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic date time

Start with a labeled datetime field for publish times, appointment slots, or audit stamps. Without min/max the browser allows any valid local datetime. Pair with `.required()` when the schedule must be set before save.

```python title="app/orbit/resources/example_resource.py"
DateTimePicker.make('published_at')
    .label('Published at')
    .helper_text('Local time for the panel timezone.')
```

![Orbit Basic date time (light)](/examples/light/forms/date-time-picker/basic.png)

![Orbit Basic date time (dark)](/examples/dark/forms/date-time-picker/basic.png)

## Bounded range

`.min_date()` and `.max_date()` emit HTML `min` / `max` attributes on the input. Pass ISO-like strings the browser accepts for `datetime-local` (for example `2026-01-01T00:00`). Bounds are enforced by the browser UI; add `.after()` / `.before()` validation rules when you also need server-side checks against other fields.

```python title="app/orbit/resources/example_resource.py"
DateTimePicker.make('scheduled_at')
    .label('Scheduled at')
    .min_date('2026-01-01T00:00')
    .max_date('2026-12-31T23:59')
```

![Orbit Bounded range (light)](/examples/light/forms/date-time-picker/min-max.png)

![Orbit Bounded range (dark)](/examples/dark/forms/date-time-picker/min-max.png)

## Display format hint

`.display_format()` stores a Filament-style format string on `data-display-format`. Orbit does not reformat the stored value on the server — the attribute is a hint for client scripts or future non-native chrome. Keep dehydrating the native `datetime-local` string unless you transform it in `.dehydrate_state_using()`.

```python title="app/orbit/resources/example_resource.py"
DateTimePicker.make('starts_at')
    .label('Starts at')
    .display_format('Y-m-d H:i')
```

![Orbit Display format hint (light)](/examples/light/forms/date-time-picker/display-format.png)

![Orbit Display format hint (dark)](/examples/dark/forms/date-time-picker/display-format.png)

## Non-native flag

`.native(False)` adds `data-native="false"` while still rendering a `datetime-local` input today. Use it when your panel assets will swap in a custom picker. Until that host integration lands, behavior matches the native control.

```python title="app/orbit/resources/example_resource.py"
DateTimePicker.make('ends_at')
    .label('Ends at')
    .native(False)
```

![Orbit Non-native flag (light)](/examples/light/forms/date-time-picker/non-native.png)

![Orbit Non-native flag (dark)](/examples/dark/forms/date-time-picker/non-native.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
