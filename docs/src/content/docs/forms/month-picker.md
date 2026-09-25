---
title: Month picker
description: MonthPicker selects a calendar month and stores the first day as YYYY-MM-DD.
---

## Introduction

`MonthPicker` uses Flowbite’s month view. The stored value is the first day of the month (`YYYY-MM-DD`). Call `.native(True)` for `<input type="month">`.

```python title="app/orbit/resources/example_resource.py"
MonthPicker.make('billing_month')
    .label('Billing month')
```

![Orbit Month picker (light)](/examples/light/forms/month-picker/basic.png)

![Orbit Month picker (dark)](/examples/dark/forms/month-picker/basic.png)
