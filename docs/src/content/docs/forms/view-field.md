---
title: View field
description: ViewField displays read-only HTML or computed content inside a form — summaries, previews, or audit snippets without dehydrating user input.
---

## Introduction

ViewField displays read-only HTML or computed content inside a form — summaries, previews, or audit snippets without dehydrating user input.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic view field

Static HTML summary block.

```python
ViewField.make('summary')
    .label('Summary')
    .content('<p>Published on <strong>18 Sep 2026</strong>.</p>')
```

![Orbit Basic view field (light)](/examples/light/forms/view-field/basic.png)

![Orbit Basic view field (dark)](/examples/dark/forms/view-field/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
