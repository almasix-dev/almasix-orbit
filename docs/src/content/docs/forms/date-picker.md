---
title: Date picker
description: DatePicker is a native date input with min/max bounds, display-format hints, and shared Field validation.
---

## Introduction

`DatePicker` sets `type="date"` and shares min/max, display format, and native flags with `DateTimePicker` / `TimePicker`. Prefer it for birthdays, start dates, and calendar-day deadlines where time-of-day is irrelevant.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic date picker

A labeled date field dehydrates as `YYYY-MM-DD`. Add `.placeholder()` sparingly — many browsers ignore placeholders on date inputs.

```python title="app/orbit/resources/example_resource.py"
DatePicker.make('starts_on')
    .label('Starts on')
    .helper_text('Inclusive start date.')
```

![Orbit Basic date picker (light)](/examples/light/forms/date-picker/basic.png)

![Orbit Basic date picker (dark)](/examples/dark/forms/date-picker/basic.png)

## Bounded range

`.min_date()` / `.max_date()` map to HTML `min` / `max`. Use calendar dates (`2020-01-01`). Combine with `.after('starts_on')` on a sibling end-date field for cross-field ordering.

```python title="app/orbit/resources/example_resource.py"
DatePicker.make('ends_on')
    .label('Ends on')
    .min_date('2020-01-01')
    .max_date('2030-12-31')
```

![Orbit Bounded range (light)](/examples/light/forms/date-picker/min-max.png)

![Orbit Bounded range (dark)](/examples/dark/forms/date-picker/min-max.png)

## Display format hint

`.display_format()` sets `data-display-format` for client presentation hints without changing the stored ISO date string.

```python title="app/orbit/resources/example_resource.py"
DatePicker.make('due_on')
    .label('Due on')
    .display_format('d/m/Y')
```

![Orbit Display format hint (light)](/examples/light/forms/date-picker/display-format.png)

![Orbit Display format hint (dark)](/examples/dark/forms/date-picker/display-format.png)

## Non-native flag

`.native(False)` marks the control for custom picker assets while still rendering `<input type="date">` in the forms package today.

```python title="app/orbit/resources/example_resource.py"
DatePicker.make('anniversary')
    .label('Anniversary')
    .native(False)
```

![Orbit Non-native flag (light)](/examples/light/forms/date-picker/non-native.png)

![Orbit Non-native flag (dark)](/examples/dark/forms/date-picker/non-native.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
