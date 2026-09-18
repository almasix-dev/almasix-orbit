---
title: Date picker
description: DatePicker wraps a native date input with min/max constraints and optional non-native picker chrome.
---

## Introduction

DatePicker wraps a native date input with min/max constraints and optional non-native picker chrome. Values dehydrate as ISO date strings.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic date picker

Standard date field.

```python
DatePicker.make('starts')
    .label('Starts on')
```

![Orbit Basic date picker (light)](/examples/light/forms/date-picker/basic.png)

![Orbit Basic date picker (dark)](/examples/dark/forms/date-picker/basic.png)

## Min and max dates

Restrict selectable range.

```python
DatePicker.make('window')
    .label('Window')
    .min_date('2026-01-01')
    .max_date('2026-12-31')
```

![Orbit Min and max dates (light)](/examples/light/forms/date-picker/min-max.png)

![Orbit Min and max dates (dark)](/examples/dark/forms/date-picker/min-max.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
