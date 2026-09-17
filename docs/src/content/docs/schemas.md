---
title: Schemas & layouts
description: Compose Orbit UI with Schema, Grid, Section, Tabs, Fieldset, and Wizard.
---

**Schemas** are the nesting fabric under forms (and anything else that wants a component tree). Layouts sit beside fields and render structured HTML with Alpine where interaction is needed.

```python
from almasix.orbit.schemas import Schema, Grid, Section, Tabs, Fieldset, Wizard
from almasix.orbit.forms import TextInput

schema = (
    Schema.make("user")
    .columns(1)
    .schema([
        Section.make("profile")
        .heading("Profile")
        .description("Who is this person?")
        .collapsible()
        .schema([
            Grid.make("names").columns(2).schema([
                TextInput.make("first_name").required(),
                TextInput.make("last_name").required(),
            ]),
        ]),
    ])
)

schema.fill({"first_name": "Ada"})
payload = schema.dehydrate()
html = schema.render(schema.get_state())
```

## Schema basics

| Method | Role |
|--------|------|
| `.components([...])` / `.schema([...])` | Child tree |
| `.columns(n)` | Hint for grid-ish rendering |
| `.state({…})` / `.fill({…})` | Hydrate |
| `.get_state()` / `.dehydrate()` | Read back |
| `.get_components()` / `.render(state)` | Inspect / HTML |

`dehydrate()` only includes dehydrated children that have a state path, falling back to defaults when needed.

## Layouts

| Layout | Key API | Markup vibe |
|--------|---------|-------------|
| `Grid` | `.columns(n).schema([...])` | `or-grid-cols-n` |
| `Section` | `.heading`, `.description`, `.collapsible`, `.collapsed` | `<section class="or-section">` |
| `Tabs` | `.tabs(("One", […]), ("Two", […]))` | Alpine `tab` index |
| `Fieldset` | `.label(…).schema([...])` | Native `<fieldset>` |
| `Wizard` | `.steps(("Step 1", […]), …)` | Alpine `step` index |

```python
Tabs.make("account").tabs(
    ("Profile", [TextInput.make("name")]),
    ("Billing", [TextInput.make("vat")]),
)

Wizard.make("onboard").steps(
    ("Details", [TextInput.make("company").required()]),
    ("Plan", [TextInput.make("plan").required()]),
)
```

## Where they show up

- Inside `Form.schema([...])` — the usual place
- Anywhere you want a reusable component tree with state

Forms inherit from `Schema`, so a form *is* a schema with validation bolted on. See [Forms](/forms/).
