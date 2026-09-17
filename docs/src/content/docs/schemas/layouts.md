---
title: Layouts
description: Structure schemas with Grid, Flex, Group, Split, and Fieldset.
---

Use layout components from `almasix.orbit.schemas` inside any schema (forms, infolists, pages).

| Component | Role |
|-----------|------|
| `Grid` | Responsive columns, dense/gap, optional grid container |
| `Flex` | Flex row with grow + breakpoint stacking |
| `Group` | Fuse children without fieldset chrome (optional columns) |
| `Split` | Side-by-side panes that stack below a breakpoint |
| `Section` | Bordered section with heading, icon, compact/aside, collapsible |
| `Fieldset` | Native fieldset + legend |
| `Tabs` | Tabbed panels with optional icons, badges, persist |
| `Wizard` | Multi-step flow with nav, continue/back, optional skip |

```python
from almasix.orbit.schemas import Grid, Flex, Group, Split, Section, Fieldset
from almasix.orbit.forms import TextInput

layout = Section.make("profile").heading("Profile").collapsible().schema([
    Flex.make().from_breakpoint("md").schema([
        TextInput.make("first_name"),
        TextInput.make("last_name"),
    ]),
    Group.make().columns(2).schema([
        TextInput.make("city"),
        TextInput.make("country"),
    ]),
    Split.make().from_("lg").schema([
        Fieldset.make().label("Contact").schema([TextInput.make("email")]),
        Fieldset.make().label("Notes").schema([TextInput.make("notes")]),
    ]),
])
```

See [Schemas overview](/schemas/overview/) for nesting with forms.

## Preview

![Orbit schemas/grid-flex (light)](/examples/light/schemas/grid-flex.png)

![Orbit schemas/grid-flex (dark)](/examples/dark/schemas/grid-flex.png)
