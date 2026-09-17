---
title: Support toolkit
description: Component base, colors, icons, and HTML helpers shared across Orbit.
---

`almasix-orbit-support` is the quiet foundation — fluent components, brand colors, Heroicons, and tiny HTML helpers.

```python
from almasix.orbit.support import Component, Color, Colors, Heroicon, e, tag, icon
```

## Component

Almost everything fluent in Orbit subclasses `Component`:

```python
Component.make("demo")
    .label("Demo")
    .hidden(False)
    .visible(True)                 # bool or callable
    .disabled(False)
    .extra_attributes({"data-x": "1"})
    .view("orbit.custom")
    .column_span(2)
    .live()
    .dehydrated(True)
    .state_path("nested.demo")
    .default("hi")
    .helper_text("Helpful")
    .hint("Hint")
    .hint_icon("heroicon-o-information-circle")
    .configure(lambda c: c.label("Configured"))
```

`get_state_path()` returns the explicit path or falls back to the component name. `get_label()` title-cases the name when you don’t set one. `to_dict()` / `render(state, **ctx)` round out the base.

## Colors

```python
Color.PRIMARY   # and DANGER, GRAY, INFO, SUCCESS, WARNING
Colors.hex(Color.PRIMARY)       # "#f1511b"
Colors.css_class("success")     # "or-color-success"
```

## Icons

Outline Heroicons ship with Orbit (prefixed `heroicon-o-…`):

`users`, `home`, `cog-6-tooth`, `bell`, `plus`, `pencil-square`, `trash`, `magnifying-glass`, `x-mark`, `check`, `information-circle`, …

```python
icon("heroicon-o-users", size=20, css_class="or-icon")
Heroicon.outline("users")     # → "heroicon-o-users"
Heroicon.render("plus", size=16)
Heroicon.available()
```

## HTML

```python
e("<script>")  # escaped text
tag("div", "Hi", attrs={"class": "or-x"})
tag("img", void=True, attrs={"src": "/a.png", "alt": ""})
```

Small tools, big surface area — every field, column, and action leans on these.
