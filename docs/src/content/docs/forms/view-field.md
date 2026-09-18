---
title: View field
description: ViewField displays read-only HTML or computed content inside a form — summaries, previews, or audit snippets without dehydrating user input.
---

## Introduction

ViewField displays read-only HTML or computed content inside a form — summaries, previews, or audit snippets without dehydrating user input.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic view field

![Orbit Basic view field (light)](/examples/light/forms/view-field/basic.png)

![Orbit Basic view field (dark)](/examples/dark/forms/view-field/basic.png)

Static HTML summary block.

```python
ViewField.make('summary').label('Summary').content('<p>Published on <strong>18 Sep 2026</strong>.</p>')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
