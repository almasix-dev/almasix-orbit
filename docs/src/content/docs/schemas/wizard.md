---
title: Wizard
description: Wizard guides users through sequential steps with back/next navigation and optional skip.
---

## Introduction

Wizard guides users through sequential steps with back/next navigation and optional skip. Each step is a labeled schema chunk — ideal for onboarding or multi-page creates without route changes.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic wizard

![Orbit Basic wizard (light)](/examples/light/schemas/wizard/basic.png)

![Orbit Basic wizard (dark)](/examples/dark/schemas/wizard/basic.png)

Account then profile steps.

```python
Wizard.make('onboard')
    .steps({'label': 'Account', 'schema': [...]}, {'label': 'Profile', 'schema': [...]})
    .start_step(0)
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
