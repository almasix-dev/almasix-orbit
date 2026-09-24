---
title: Year picker
description: YearPicker selects a calendar year and stores a four-digit YYYY string.
---

## Introduction

`YearPicker` uses Flowbite’s year view (`pickLevel` 2). The stored value is a four-digit year (`YYYY`). Call `.native(True)` for a numeric year input.

```python title="app/orbit/resources/example_resource.py"
YearPicker.make('vintage')
    .label('Vintage year')
    .min_date('1990')
    .max_date('2030')
```

![Orbit Year picker (light)](/examples/light/forms/year-picker/basic.png)

![Orbit Year picker (dark)](/examples/dark/forms/year-picker/basic.png)
