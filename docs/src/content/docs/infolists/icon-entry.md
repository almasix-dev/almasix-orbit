---
title: Icon entry
description: IconEntry renders a Heroicon from state, or boolean true/false icons with Filament-parity colors and sizes.
---

## Introduction

`IconEntry` is icon-forward: the value itself is treated as an icon name, or you pass `.icon(...)` / `.boolean()` for check / x display. Shared [Entry chrome](/infolists/overview/) (label, helper, placeholder, tooltip) still applies.

## Basic icon entry

State is a Heroicon name string.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import IconEntry

IconEntry.make("icon").label("Icon").color("primary").size("lg")
```

![Orbit Icon entry basic (light)](/examples/light/infolists/icon-entry/basic.png)

![Orbit Icon entry basic (dark)](/examples/dark/infolists/icon-entry/basic.png)

## Boolean icons

`.boolean()` maps truthy → `.true_icon()` (default `heroicon-o-check`) and falsy → `.false_icon()` (default `heroicon-o-x-mark`). Colors default to `success` / `danger`; override with `.true_color()` / `.false_color()`, or a shared `.color(...)`.

```python title="app/orbit/resources/post_resource.py"
IconEntry.make("active").label("Active").boolean()

IconEntry.make("featured")
    .label("Featured")
    .boolean()
    .false_color("gray")
    .false_icon("heroicon-o-minus")
```

![Orbit Icon entry boolean (light)](/examples/light/infolists/icon-entry/boolean.png)

![Orbit Icon entry boolean (dark)](/examples/dark/infolists/icon-entry/boolean.png)

## Colors and sizes

`.color(...)` tints the icon. `.size("sm" | "md" | "lg" | …)` maps to `or-icon-size-*`.

```python title="app/orbit/resources/post_resource.py"
IconEntry.make("icon").label("Launch").color("warning").size("md")
```

![Orbit Icon entry colors (light)](/examples/light/infolists/icon-entry/colors.png)

![Orbit Icon entry colors (dark)](/examples/dark/infolists/icon-entry/colors.png)

## API cheat sheet

| Method | Notes |
|--------|-------|
| `.boolean` | True / false icon mode |
| `.true_icon` / `.false_icon` | Override boolean glyphs |
| `.true_color` / `.false_color` | Per-state colors |
| `.color` | Shared icon color |
| `.size` | Icon size utility |
| `.icon` | Explicit icon when state is not a name |
| `.placeholder` | Empty-state text (non-boolean) |
