---
title: Wizard
description: Wizard guides users through sequential steps with back/next navigation and optional skip.
---

## Introduction

`Wizard` is a schema layout that shows one labeled step at a time. Each step is a chunk of fields (or nested layouts). Alpine keeps the current step in `x-data`; Back / Continue (and optional Skip) move between them without a route change.

Reach for it on onboarding, multi-page creates, and any form that is too long for a single scroll.

## Basic wizard

Steps as dicts (`label` + `schema`) or as `(label, components)` tuples.

```python title="app/orbit/resources/user_resource.py"
from almasix.orbit.forms import TextInput, Textarea
from almasix.orbit.schemas import Wizard

Wizard.make("onboard")
    .steps(
        {"label": "Account", "schema": [TextInput.make("email").email().required()]},
        {"label": "Profile", "schema": [TextInput.make("name").required()]},
    )
    .start_step(0)
```

![Orbit Basic wizard (light)](/examples/light/schemas/wizard/basic.png)

![Orbit Basic wizard (dark)](/examples/dark/schemas/wizard/basic.png)

`.start_step(index)` picks which pane is visible on first paint (clamped to the last step).

## Step descriptions

Dict steps may include `description`. It renders under the step title inside the pane.

```python title="app/orbit/resources/user_resource.py"
Wizard.make("onboard").steps(
    {
        "label": "Account",
        "description": "We will send a confirmation to this address.",
        "schema": [TextInput.make("email").email().required()],
    },
    {
        "label": "Profile",
        "description": "Shown on your public author page.",
        "schema": [TextInput.make("name").required(), Textarea.make("bio")],
    },
)
```

![Orbit Wizard with descriptions (light)](/examples/light/schemas/wizard/descriptions.png)

![Orbit Wizard with descriptions (dark)](/examples/dark/schemas/wizard/descriptions.png)

## Skippable steps

`.skippable()` adds a Skip link that advances to the next step without validating the current pane. Validation still runs when the wrapping form submits.

```python title="app/orbit/resources/user_resource.py"
Wizard.make("onboard")
    .skippable()
    .steps(
        {"label": "Account", "schema": [TextInput.make("email").required()]},
        {"label": "Optional bio", "schema": [Textarea.make("bio")]},
    )
```

![Orbit Skippable wizard (light)](/examples/light/schemas/wizard/skippable.png)

![Orbit Skippable wizard (dark)](/examples/dark/schemas/wizard/skippable.png)

The nav buttons on the left jump to any step (`@click="step = n"`). Continue is disabled on the last step; Back is disabled on the first.

## API cheat sheet

| Method | Role |
|--------|------|
| `.steps(...)` | Dicts (`label` / `id`, `schema` / `components`, optional `description`) or `(label, components)` tuples |
| `.start_step(index)` | Zero-based first pane |
| `.skippable()` | Show Skip in the footer |

All fields across every step are still children of the parent [form](/components/form/) — dehydrate and validate the whole schema on submit.

Closures on `.visible()` hide a wizard (or nested fields) entirely — see [Form closures](/forms/closures/).
