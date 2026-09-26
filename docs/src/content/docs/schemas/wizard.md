---
title: Wizard
description: Wizard guides users through sequential steps with a progress stepper, linear or free navigation, and optional vertical layout.
---

## Introduction

`Wizard` is a schema layout that shows one labeled step at a time. Each step is a chunk of fields (or nested layouts). Alpine (`orbitWizard`) keeps the current step; Back / Continue (and optional Skip) move between them without a route change.

The stepper chrome is intentionally distinct from [tabs](/schemas/tabs/) — numbered progress indicators, connectors, and completed-step checks — so users read it as a multi-step flow.

Reach for it on onboarding, multi-page creates, and any form that is too long for a single scroll.

## Basic wizard

Prefer a `WizardStep` for each pane. The step owns its label, description, icons, and schema:

```python title="app/orbit/resources/user_resource.py"
from almasix.orbit.forms import TextInput
from almasix.orbit.schemas import Wizard, WizardStep

Wizard.make("onboard").steps(
    WizardStep.make("account")
        .label("Account")
        .description("We will send a confirmation to this address.")
        .icon("heroicon-o-envelope")
        .schema([TextInput.make("email").email().required()]),
    WizardStep.make("profile")
        .label("Profile")
        .completed_icon("heroicon-o-check")
        .schema([TextInput.make("name").required()]),
)
```

`.description(...)` is the sentence under the step title. `.icon(...)` replaces the step number in the stepper. `.completed_icon(...)` replaces the check mark after the step has been passed. `.extra_attributes({...})` adds classes and data attributes on the step button.

Dicts (`label` + `schema`) and `(label, components)` tuples still work when a step needs no extra chrome. Wizards are **linear by default**: Continue validates the current pane (HTML5 constraints) before unlocking the next step, and nav buttons for future steps stay locked until reached.

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

## Linear vs non-linear

| Mode | Behavior |
|------|----------|
| `.linear()` (default) | Continue runs constraint validation on the current step; nav cannot jump ahead of `maxReached` |
| `.non_linear()` | Users may click any step in the stepper; Continue still advances without locking |

```python title="app/orbit/resources/user_resource.py"
Wizard.make("survey").non_linear().steps(
    {"label": "Basics", "schema": [TextInput.make("name")]},
    {"label": "Details", "schema": [Textarea.make("notes")]},
)
```

Server-side form validation still runs for the whole schema on submit either way.

## Vertical stepper

`.vertical()` places the step list beside the body (side rail) instead of above it — useful on wide create pages.

```python title="app/orbit/resources/user_resource.py"
Wizard.make("onboard").vertical().steps(
    {"label": "Account", "schema": [TextInput.make("email").required()]},
    {"label": "Profile", "schema": [TextInput.make("name").required()]},
)
```

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

## API cheat sheet

| Method | Role |
|--------|------|
| `.steps(...)` | `WizardStep` components, dicts, or `(label, components)` tuples |
| `WizardStep.description` | Sentence under the step title |
| `WizardStep.icon` | Icon in place of the step number |
| `WizardStep.completed_icon` | Icon in place of the check mark once the step is passed |
| `.start_step(index)` | Zero-based first pane |
| `.linear()` / `.non_linear()` | Lock ahead steps vs free nav jump |
| `.vertical()` | Side-rail stepper instead of top row |
| `.skippable()` | Show Skip in the footer |

All fields across every step are still children of the parent [form](/components/form/) — dehydrate and validate the whole schema on submit.

Closures on `.visible()` hide a wizard (or nested fields) entirely — see [Form closures](/forms/closures/).
