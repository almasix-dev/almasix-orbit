---
title: Date picker
description: DatePicker uses a Flowbite calendar by default, with min/max bounds and an optional native browser input.
---

## Introduction

`DatePicker` stores a calendar day as `YYYY-MM-DD`. By default Orbit mounts a **Flowbite** calendar (Alpine `orbitDatePicker`) that matches the panel theme. Call `.native(True)` when you want the browser’s `<input type="date">` instead.

Prefer it for birthdays, start dates, and deadlines where time-of-day does not matter. Closely related fields: [Date-time](/forms/date-time-picker/), [Time](/forms/time-picker/), [Week](/forms/week-picker/), [Month](/forms/month-picker/), and [Year](/forms/year-picker/).

## Basic date picker

A labeled date field dehydrates as `YYYY-MM-DD`. The visible control is a text input that opens the calendar on focus.

```python title="app/orbit/resources/example_resource.py"
DatePicker.make('starts_on')
    .label('Starts on')
    .helper_text('Inclusive start date.')
```

![Orbit Basic date picker (light)](/examples/light/forms/date-picker/basic.png)

![Orbit Basic date picker (dark)](/examples/dark/forms/date-picker/basic.png)

## Bounded range

`.min_date()` / `.max_date()` constrain the calendar (`2020-01-01` style). Combine with `.after('starts_on')` on a sibling end-date field for cross-field ordering.

```python title="app/orbit/resources/example_resource.py"
DatePicker.make('ends_on')
    .label('Ends on')
    .min_date('2020-01-01')
    .max_date('2030-12-31')
```

![Orbit Bounded range (light)](/examples/light/forms/date-picker/min-max.png)

![Orbit Bounded range (dark)](/examples/dark/forms/date-picker/min-max.png)

## Native browser input

`.native(True)` swaps the Flowbite host for a plain `<input type="date">`. Use this when you need the OS control or are embedding Orbit in a constrained host.

```python title="app/orbit/resources/example_resource.py"
DatePicker.make('anniversary')
    .label('Anniversary')
    .native(True)
```

![Orbit Native date input (light)](/examples/light/forms/date-picker/native.png)

![Orbit Native date input (dark)](/examples/dark/forms/date-picker/native.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
