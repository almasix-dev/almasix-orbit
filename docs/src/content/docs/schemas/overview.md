---
title: Overview
description: Compose Orbit UI with Schema, Grid, Flex, Section, Tabs, Callout, EmptyState, and primes.
---

**Schemas** are the nesting fabric under forms (and anything else that wants a component tree). Layouts and primes sit beside fields and render structured HTML.

```python
from almasix.orbit.schemas import (
    Schema, Grid, Flex, Section, Tabs, Fieldset, Wizard,
    Callout, EmptyState, Text, Icon, Image, UnorderedList,
)
from almasix.orbit.forms import TextInput

schema = (
    Schema.make("user")
    .schema([
        Callout.make("tip").info().label("Tip").description("Fill your profile"),
        Section.make("profile").heading("Profile").schema([
            Flex.make("names").from_breakpoint("md").schema([
                TextInput.make("first_name").required(),
                TextInput.make("last_name").required(),
            ]),
        ]),
    ])
)
```

## Schema basics

| Method | Role |
|--------|------|
| `.components([...])` / `.schema([...])` | Child tree |
| `.columns(n)` | Hint for grid-ish rendering |
| `.state({…})` / `.fill({…})` | Hydrate |
| `.get_state()` / `.dehydrate()` | Read back |
| `.render(state)` | HTML |

## Layouts

| Layout | Key API |
|--------|---------|
| `Grid` | `.columns(n)`, `.dense()`, `.gap(False)`, `.grid_container()` |
| `Flex` | `.grow()`, `.from_breakpoint("md")` |
| `Section` | `.heading`, `.description`, `.collapsible`, `.collapsed` |
| `Tabs` | `.tabs(("One", […]), ("Two", […]))` |
| `Fieldset` | `.label(…).schema([...])` |
| `Wizard` | `.steps(("Step 1", […]), …)` |
| `Callout` | `.status` / `.info()` / `.danger()` / `.success()` / `.warning()`, `.description`, `.icon`, `.footer_actions` |
| `EmptyState` | `.heading`, `.description`, `.icon`, `.actions` |

## Primes

| Prime | Key API |
|-------|---------|
| `Text` | `.content()`, `.markdown()`, `.html()`, `.badge()`, `.color()`, `.size()`, `.weight()`, `.tooltip()`, `.icon()` |
| `Icon` | `.icon()`, `.color()`, `.size()`, `.tooltip()` |
| `Image` | `.src()`, `.width()` / `.height()` / `.image_size()`, `.alignment()` |
| `UnorderedList` | `.items([...])`, `.bullet_size()` |

```python
Text.make().content("Published").badge().color("success")
Icon.make().icon("heroicon-o-check").color("success")
Image.make().src("/avatar.png").image_size(40).alignment("center")
UnorderedList.make().items(["Ship", "Iterate", "Document"])
EmptyState.make().heading("No posts yet").description("Create your first post.")
Callout.make().warning().label("Unsaved").description("Leave carefully.")
```

Forms inherit from `Schema`, so a form *is* a schema with validation bolted on. See [Forms](/forms/overview/).


## Preview

![Orbit schemas/section (light)](/examples/light/schemas/section.png)

![Orbit schemas/section (dark)](/examples/dark/schemas/section.png)
