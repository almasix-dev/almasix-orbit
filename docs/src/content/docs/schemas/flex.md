---
title: Flex
description: Arrange schema children in a responsive flex row that stacks below a breakpoint.
---

## Introduction

`Flex` arranges children in a horizontal flex row. Each child is wrapped in an `or-flex-item`. Use `.from_breakpoint("md")` (or `sm` / `lg` / …) so fields stack on small screens and sit side-by-side from that breakpoint up — the usual pattern for first-name / last-name pairs.

```python title="app/orbit/schemas/flex_basic.py"
from almasix.orbit.schemas import Flex
from almasix.orbit.forms import TextInput

Flex.make()
    .from_breakpoint("md")
    .schema([
        TextInput.make("left"),
        TextInput.make("right"),
    ])
```

![Basic flex (light)](/examples/light/schemas/flex/basic.png)
![Basic flex (dark)](/examples/dark/schemas/flex/basic.png)

## Breakpoints

`.from_breakpoint` emits `or-flex-from-{breakpoint}`. Omit it when the row should stay horizontal at all widths:

```python title="app/orbit/schemas/flex_breakpoints.py"
Flex.make().from_breakpoint("sm").schema([...])
Flex.make().from_breakpoint("lg").schema([...])
Flex.make().schema([...])  # always a row
```

## Grow

Children grow to fill space by default (`or-flex-grow`). Disable with `.grow(False)` when you want intrinsic widths:

```python title="app/orbit/schemas/flex_grow.py"
Flex.make().grow(False).from_breakpoint("lg").schema([...])
```

If a child sets a column span, the item wrapper still receives `or-col-span-N`.

## Dense and gap

```python title="app/orbit/schemas/flex_gap.py"
Flex.make().dense().gap("sm").from_breakpoint("md").schema([...])
Flex.make().gap(False).schema([...])
```

## When to prefer Grid

Reach for [Grid](/schemas/grid/) when you need a fixed track count (three equal columns, wrapped rows). Prefer Flex when the children should share one responsive row that stacks cleanly on mobile.

![Grid + flex gallery (light)](/examples/light/schemas/grid-flex.png)
![Grid + flex gallery (dark)](/examples/dark/schemas/grid-flex.png)

## API reference

| Method | Role |
|--------|------|
| `.from_breakpoint` | Stack below this breakpoint; row from it upward |
| `.grow` | Whether flex items grow (default `True`) |
| `.schema` | Child components |
| `.dense` / `.gap` / `.defer_loading` | Shared layout helpers |

See [Layouts](/schemas/layouts/) for composition patterns with Section, Group, and Split.
