---
title: Schemas overview
description: Nest Orbit UI with Schema, layouts, callouts, empty states, and primes — the fabric under forms and pages.
---

## Introduction

Schemas are the nesting fabric under forms (and anything else that wants a component tree). A `Schema` holds state, dehydrates fields, and renders children. Layouts (`Grid`, `Flex`, `Group`, `Split`, `Section`, `Tabs`, `Wizard`, `Fieldset`) organize fields; primes (`Text`, `Icon`, `Image`, `UnorderedList`) and callouts add non-field chrome.

```python
from almasix.orbit.schemas import (
    Schema, Section, Flex, Callout,
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

![Orbit schema section (light)](/examples/light/schemas/section/basic.png)

![Orbit schema section (dark)](/examples/dark/schemas/section/basic.png)

## Layout gallery

| Layout | Preview |
|--------|---------|
| [Section](/schemas/sections/) | Collapsible panels with headings |
| [Tabs](/schemas/tabs/) | Icon + badge aware tab strips |
| [Wizard](/schemas/wizards/) | Multi-step nav with continue/back |
| [Grid](/schemas/grid/) / [Flex](/schemas/flex/) | Responsive columns |
| [Group](/schemas/group/) / [Split](/schemas/split/) | Fuse or side-by-side panes |
| [Fieldset](/schemas/fieldset/) | Native legend grouping |
| [Callout](/schemas/callouts/) | Status banners |
| [Empty state](/schemas/empty-states/) | Zero-data placeholders |
| [Primes](/schemas/primes/) | Text, icon, image, lists |

## Schema basics

| Method | Role |
|--------|------|
| `.components([...])` / `.schema([...])` | Child tree |
| `.columns(n)` | Hint for grid-ish rendering |
| `.state({…})` / `.fill({…})` | Hydrate |
| `.get_state()` / `.dehydrate()` | Read back |
| `.render(state)` | HTML |
