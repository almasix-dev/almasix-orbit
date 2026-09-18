---
title: Split
description: Split places schema columns side by side above a breakpoint — notes beside uploads, preview beside editor.
---

## Introduction

Split places schema columns side by side above a breakpoint — notes beside uploads, preview beside editor.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic split

![Orbit Basic split (light)](/examples/light/schemas/split/basic.png)

![Orbit Basic split (dark)](/examples/dark/schemas/split/basic.png)

Notes and attachment columns.

```python
Split.make()
    .from_breakpoint('md')
    .schema([Textarea.make('notes'), FileUpload.make('attachment')])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
