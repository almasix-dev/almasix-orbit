---
title: Builder
description: Builder extends Repeater with typed blocks — each block has its own schema and picker button.
---

## Introduction

Builder extends Repeater with typed blocks — each block has its own schema and picker button. Use for page builders, email sections, or CMS layouts.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic builder

Hero and text blocks with picker.

```python
Builder.make('content')
    .label('Page blocks')
    .blocks([Block.make('hero').label('Hero').schema([TextInput.make('heading')])])
```

![Orbit Basic builder (light)](/examples/light/forms/builder/basic.png)

![Orbit Basic builder (dark)](/examples/dark/forms/builder/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
