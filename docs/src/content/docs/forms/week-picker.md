---
title: Week picker
description: WeekPicker selects an ISO week and stores the Monday of that week as YYYY-MM-DD.
---

## Introduction

`WeekPicker` opens a Flowbite calendar with week numbers. The dehydrated value is the **Monday** of the selected week (`YYYY-MM-DD`). Use `.native(True)` for `<input type="week">` when you prefer the browser control.

```python title="app/orbit/resources/example_resource.py"
WeekPicker.make('sprint')
    .label('Sprint week')
    .min_date('2026-01-01')
```

![Orbit Week picker (light)](/examples/light/forms/week-picker/basic.png)

![Orbit Week picker (dark)](/examples/dark/forms/week-picker/basic.png)
