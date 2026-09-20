---
title: Color entry
description: ColorEntry shows a swatch plus the color value, optionally copyable to the clipboard.
---

## Introduction

`ColorEntry` renders a small swatch (`or-color-swatch`) beside the hex / CSS color string so brand accents and theme tokens are obvious at a glance on the view page. Empty state uses `.placeholder(...)` instead of inventing `#000000` for display when a placeholder is set.

Pair with `.copyable()` when operators need to grab the hex. Label chrome follows the stacked default from the [overview](/infolists/overview/).

## Basic color entry

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import ColorEntry

ColorEntry.make("accent").label("Accent")
```

![Orbit Color entry basic (light)](/examples/light/infolists/color-entry/basic.png)

![Orbit Color entry basic (dark)](/examples/dark/infolists/color-entry/basic.png)

## Copyable

`.copyable()` wraps the swatch + value so users can copy the hex. Pair with `.copy_message(...)` for toast-style feedback attributes.

```python title="app/orbit/resources/post_resource.py"
ColorEntry.make("accent").label("Accent").copyable().copy_message("Hex copied")
```

![Orbit Color entry copyable (light)](/examples/light/infolists/color-entry/copyable.png)

![Orbit Color entry copyable (dark)](/examples/dark/infolists/color-entry/copyable.png)

## Placeholder

`.placeholder(...)` is the empty-state copy when the record has no color. Orbit does not invent `#000000` for display in that case.

```python title="app/orbit/resources/post_resource.py"
ColorEntry.make("accent").label("Accent").placeholder("No accent set")
```

![Orbit Color entry placeholder (light)](/examples/light/infolists/color-entry/placeholder.png)

![Orbit Color entry placeholder (dark)](/examples/dark/infolists/color-entry/placeholder.png)

## API cheat sheet

| Method | Notes |
|--------|-------|
| `.copyable` / `.copy_message` / `.copy_message_duration` | Clipboard |
| `.placeholder` | Empty-state text |
| Shared chrome | Label, helper, hint, tooltip — see [overview](/infolists/overview/) |
