---
title: Wizards
description: Guide users through sequential schema steps with back / continue navigation and optional skip.
---

## Introduction

`Wizard` guides users through sequential steps with back / continue navigation and an optional skip control. Each step is a labeled schema chunk — ideal for onboarding or multi-page creates without changing routes.

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

## Skippable and start step

```python title="app/orbit/schemas/wizard_options.py"
Wizard.make("onboard")
    .steps(...)
    .skippable()       # show a Skip control in the footer
    .start_step(1)     # zero-based initial step
```

![Wizard (light)](/examples/light/schemas/wizard.png)
![Wizard (dark)](/examples/dark/schemas/wizard.png)

The footer always includes **Back** and **Continue**; Alpine keeps `step` in sync with the nav strip.

## API reference

| Method | Role |
|--------|------|
| `.steps` | One or more step defs |
| `.skippable` | Show Skip in the footer |
| `.start_step` | Zero-based initial step |
| `.schema` | Extra children outside step defs (rare) |

For non-linear panels, prefer [Tabs](/schemas/tabs/).
