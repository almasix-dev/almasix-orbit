---
title: Builder
description: Builder extends Repeater with typed blocks — each block has its own schema and picker button.
---

## Introduction

Builder extends Repeater with typed blocks — each block has its own schema and picker button. Use for page builders, email sections, or CMS layouts.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic builder

![Orbit Basic builder (light)](/examples/light/forms/builder/basic.png)

![Orbit Basic builder (dark)](/examples/dark/forms/builder/basic.png)

Hero and text blocks with picker.

```python
Builder.make('content').label('Page blocks').blocks([Block.make('hero').label('Hero').schema([TextInput.make('heading')])])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
