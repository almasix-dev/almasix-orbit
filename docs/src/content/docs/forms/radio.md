---
title: Radio
description: Radio presents mutually exclusive options with optional per-option descriptions and multi-column layouts.
---

## Introduction

Radio presents mutually exclusive options with optional per-option descriptions and multi-column layouts. State is a single selected key.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic radio

Plan or tier selection.

```python
Radio.make('plan')
    .label('Plan')
    .options({'starter': 'Starter', 'pro': 'Pro'})
```

![Orbit Basic radio (light)](/examples/light/forms/radio/basic.png)

![Orbit Basic radio (dark)](/examples/dark/forms/radio/basic.png)

## With descriptions

Helper copy under each option label.

```python
Radio.make('plan')
    .label('Plan')
    .options({...})
    .descriptions({'starter': 'For side projects'})
```

![Orbit With descriptions (light)](/examples/light/forms/radio/with-descriptions.png)

![Orbit With descriptions (dark)](/examples/dark/forms/radio/with-descriptions.png)

## Multi-column

Grid layout for dense option sets.

```python
Radio.make('plan')
    .label('Plan')
    .options({...})
    .options_columns(2)
```

![Orbit Multi-column (light)](/examples/light/forms/radio/columns.png)

![Orbit Multi-column (dark)](/examples/dark/forms/radio/columns.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
