---
title: Split
description: Split places schema columns side by side above a breakpoint — notes beside uploads, preview beside editor.
---

## Introduction

Split places schema columns side by side above a breakpoint — notes beside uploads, preview beside editor.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic split

Notes and attachment columns.

```python
Split.make()
    .from_breakpoint('md')
    .schema([Textarea.make('notes'), FileUpload.make('attachment')])
```

![Orbit Basic split (light)](/examples/light/schemas/split/basic.png)

![Orbit Basic split (dark)](/examples/dark/schemas/split/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
