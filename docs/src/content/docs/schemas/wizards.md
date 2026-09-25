---
title: Wizards
description: Guide users through sequential schema steps with a progress stepper, linear or free navigation, and optional vertical layout.
---

## Introduction

`Wizard` guides users through sequential steps with a progress stepper (not tabs), Back / Continue, and an optional Skip control. Each step is a labeled schema chunk — ideal for onboarding or multi-page creates without changing routes.

See [Wizard](/schemas/wizard/) for the full API (linear / non-linear, vertical stepper, descriptions).

```python title="app/orbit/schemas/wizard_basic.py"
from almasix.orbit.schemas import Wizard
from almasix.orbit.forms import TextInput, Textarea

Wizard.make("onboard")
    .steps(
        {"label": "Account", "schema": [TextInput.make("email")]},
        {
            "label": "Profile",
            "description": "Tell us a little about yourself.",
            "schema": [Textarea.make("bio")],
        },
    )
    .start_step(0)
```

![Basic wizard (light)](/examples/light/schemas/wizard/basic.png)
![Basic wizard (dark)](/examples/dark/schemas/wizard/basic.png)

## Defining steps

`.steps(...)` accepts dicts or `(label, components)` tuples. Dict keys: `label` (or `id`), `schema` / `components`, optional `description`.

```python title="app/orbit/schemas/wizard_steps.py"
Wizard.make("onboard").steps(
    ("Account", [TextInput.make("email")]),
    ("Profile", [TextInput.make("display_name")]),
)
```

## Options

```python title="app/orbit/schemas/wizard_options.py"
Wizard.make("onboard")
    .steps(...)
    .linear()          # default — validate before Continue; lock ahead nav
    .non_linear()      # free jump to any step
    .vertical()        # side-rail stepper
    .skippable()       # Skip in the footer
    .start_step(1)     # zero-based initial step
```

![Wizard (light)](/examples/light/schemas/wizard.png)
![Wizard (dark)](/examples/dark/schemas/wizard.png)

The footer always includes **Back** and **Continue**; Alpine `orbitWizard` keeps `step` / `maxReached` in sync with the stepper.

## API reference

| Method | Role |
|--------|------|
| `.steps` | One or more step defs |
| `.linear` / `.non_linear` | Lock ahead steps vs free nav |
| `.vertical` | Side-rail stepper |
| `.skippable` | Show Skip in the footer |
| `.start_step` | Zero-based initial step |
| `.schema` | Extra children outside step defs (rare) |

Prefer [Tabs](/schemas/tabs/) when panes are peers, not a sequenced flow.
