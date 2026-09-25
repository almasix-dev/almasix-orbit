---
title: Week picker
description: WeekPicker selects a full ISO week (Mon–Sun) and stores the Monday as YYYY-MM-DD.
---

## Introduction

`WeekPicker` opens a Flowbite calendar with ISO week numbers. Clicking any day highlights the **entire Mon–Sun week** in the panel primary color. The input displays the week number and date range (for example `Week 12 · Mar 16 – Mar 22`); the dehydrated value is the **Monday** of that week (`YYYY-MM-DD`).

Use `.native(True)` for `<input type="week">` when you prefer the browser control.

```python title="app/orbit/resources/example_resource.py"
WeekPicker.make('sprint')
    .label('Sprint week')
    .min_date('2026-01-01')
```

![Orbit Week picker (light)](/examples/light/forms/week-picker/basic.png)

![Orbit Week picker (dark)](/examples/dark/forms/week-picker/basic.png)
