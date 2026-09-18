---
title: Layouts
description: Structure schemas with Grid, Flex, Group, Split, Fieldset, and related layout components.
---

## Introduction

Layout components from `almasix.orbit.schemas` nest inside any schema — forms, infolists, and custom pages. Prefer `Section` for titled panels, `Tabs` / `Wizard` for progressive disclosure, and `Grid` / `Flex` / `Group` / `Split` for alignment without extra chrome.

![Orbit grid + flex (light)](/examples/light/schemas/grid-flex.png)

![Orbit grid + flex (dark)](/examples/dark/schemas/grid-flex.png)

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

## Component map

| Component | Role |
|-----------|------|
| [`Grid`](/schemas/grid/) | Responsive columns, dense/gap |
| [`Flex`](/schemas/flex/) | Flex row with breakpoint stacking |
| [`Group`](/schemas/group/) | Fuse children (optional columns) |
| [`Split`](/schemas/split/) | Side-by-side panes that stack |
| [`Section`](/schemas/sections/) | Heading, icon, compact/aside, collapsible |
| [`Fieldset`](/schemas/fieldset/) | Native fieldset + legend |
| [`Tabs`](/schemas/tabs/) | Icons, badges, persist |
| [`Wizard`](/schemas/wizards/) | Nav, continue/back, skip |

## More layout shots

![Orbit group + split (light)](/examples/light/schemas/group-split.png)

![Orbit group + split (dark)](/examples/dark/schemas/group-split.png)

![Orbit fieldset (light)](/examples/light/schemas/fieldset.png)

![Orbit fieldset (dark)](/examples/dark/schemas/fieldset.png)
