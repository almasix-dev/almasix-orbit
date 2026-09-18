---
title: Date picker
description: DatePicker wraps a native date input with min/max constraints and optional non-native picker chrome.
---

## Introduction

DatePicker wraps a native date input with min/max constraints and optional non-native picker chrome. Values dehydrate as ISO date strings.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic date picker

![Orbit Basic date picker (light)](/examples/light/forms/date-picker/basic.png)

![Orbit Basic date picker (dark)](/examples/dark/forms/date-picker/basic.png)

Standard date field.

```python
(
    DatePicker.make('starts')
    .label('Starts on')
)
```

## Min and max dates

![Orbit Min and max dates (light)](/examples/light/forms/date-picker/min-max.png)

![Orbit Min and max dates (dark)](/examples/dark/forms/date-picker/min-max.png)

Restrict selectable range.

```python
(
    DatePicker.make('window')
    .label('Window')
    .min_date('2026-01-01')
    .max_date('2026-12-31')
)
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
