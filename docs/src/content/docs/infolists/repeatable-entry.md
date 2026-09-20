---
title: Repeatable entry
description: RepeatableEntry nests an entry schema over each item in a list — with optional columns and contained chrome.
---

## Introduction

`RepeatableEntry` is the read-only cousin of a form repeater: each list item renders a nested entry schema. Reach for it on view pages when a record owns related rows — line items, modules, addresses — and you want the same typed entries (badges, icons, text) inside each card instead of a flat comma-joined string.

Nested entries keep the stacked label-above-value default unless you opt into `.inline_label()`. Empty lists render an “No items” empty state so the chrome still explains what would appear.

## Basic repeatable entry

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import RepeatableEntry, TextEntry

RepeatableEntry.make("items")
    .label("Modules")
    .schema([
        TextEntry.make("name").label("Name"),
        TextEntry.make("status").label("Status").badge().color("info"),
    ])
```

![Orbit Repeatable entry basic (light)](/examples/light/infolists/repeatable-entry/basic.png)

![Orbit Repeatable entry basic (dark)](/examples/dark/infolists/repeatable-entry/basic.png)

## Columns and contained layout

`.columns(2)` lays items out in a grid. `.contained(False)` drops the bordered card chrome (`or-repeatable-bare`). Empty lists render an “No items” empty state.

```python title="app/orbit/resources/post_resource.py"
RepeatableEntry.make("items")
    .label("Modules")
    .columns(2)
    .contained(False)
    .schema([
        TextEntry.make("name").label("Name"),
        TextEntry.make("status").label("Status").badge(),
    ])
```

![Orbit Repeatable entry columns (light)](/examples/light/infolists/repeatable-entry/columns.png)

![Orbit Repeatable entry columns (dark)](/examples/dark/infolists/repeatable-entry/columns.png)

## API cheat sheet

| Method | Notes |
|--------|-------|
| `.schema` | Nested entry components per item |
| `.columns` | Multi-column item grid |
| `.contained` | Toggle bordered container (default `True`) |
| Shared chrome | Label, helper, hint — see [overview](/infolists/overview/) |
