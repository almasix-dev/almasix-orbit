---
title: Support toolkit
description: Component base, colors, icons, HtmlString, evaluate, and HTML helpers shared across Orbit.
---

`almasix-orbit-support` is the foundation every other Orbit package stands on — fluent components, brand colors, Heroicons, HTML escaping, and the `evaluate()` switch that turns a value-or-callable into a value.

```python
from almasix.orbit.support import (
    Component,
    Color,
    Colors,
    Heroicon,
    HtmlString,
    classes,
    e,
    evaluate,
    icon,
    register_icon,
    tag,
)
```

![Orbit support chrome (light)](/examples/light/support/overview.png)

![Orbit support chrome (dark)](/examples/dark/support/overview.png)

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
    .saved(True)                   # alias of dehydrated
    .state_path("nested.demo")
    .key("demo-row")               # data-key; defaults to the state path
    .grow()                        # flex-grow in layouts
    .default("hi")
    .helper_text("Helpful")
    .hint("Hint")
    .hint_icon("heroicon-o-information-circle")
    .hidden_label()
    .inline_label()
    .when(True, lambda c: c.label("Configured"))
    .configure(lambda c: c.label("Configured"))
```

`get_state_path()` returns the explicit path or falls back to the component name. `get_label()` title-cases the name when you don’t set one. `to_dict()` / `render(state, **ctx)` round out the base. `.when(condition, callback)` runs the callback only if the condition is true (bool or zero-arg callable) — handy for optional chrome without a second schema.

`.live(on_blur=True)` and `.live(debounce=250)` change the Conduit / Livewire model directive (`model.blur`, `model.live.debounce.250ms`). `wire_model_attrs(name)` emits both `conduit:` and `wire:` attributes.

Callables for label / helper / default / visible / disabled / extra_attributes are documented in [Closures](/support/closures/).

## Colors

Six semantic tokens: `primary`, `danger`, `gray`, `info`, `success`, `warning`. Hex values can also be passed through — unknown names are returned unchanged so you can use a custom brand hex.

```python
Color.PRIMARY   # and DANGER, GRAY, INFO, SUCCESS, WARNING
Colors.hex(Color.PRIMARY)       # "#f1511b"
Colors.css_class("success")     # "or-color-success"
Colors.css_var("danger", 500)   # "var(--or-danger-500)"
Colors.palette("#f1511b")       # {50: "#…", …, 500: "#f1511b", …, 950: "#…"}
```

`palette()` mixes the source toward white (50–400) and black (600–950). Shade `500` is the original hex. Use the map for charts, badges, or CSS custom properties on a panel.

![Orbit color tokens (light)](/examples/light/support/colors.png)

![Orbit color tokens (dark)](/examples/dark/support/colors.png)

## Icons

Outline Heroicons ship with Orbit (prefixed `heroicon-o-…`):

`users`, `home`, `cog-6-tooth`, `bell`, `plus`, `pencil-square`, `trash`, `magnifying-glass`, `x-mark`, `check`, `information-circle`, …

```python
icon("heroicon-o-users", size=20, css_class="or-icon")
Heroicon.outline("users")     # → "heroicon-o-users"
Heroicon.render("plus", size=16)
Heroicon.available()

register_icon("actions::delete", "heroicon-o-trash")
icon("actions::delete")       # same SVG as trash
```

Unknown names render an empty span with `data-missing-icon` so a missing glyph is obvious in tests and in the DOM. `Heroicon.reset_aliases()` (or `reset_icon_aliases()`) clears aliases — use that in test setup.

![Orbit Heroicons (light)](/examples/light/support/icons.png)

![Orbit Heroicons (dark)](/examples/dark/support/icons.png)

## HTML

```python
e("<script>")                          # escaped text
e(HtmlString("<em>trusted</em>"))      # left intact
classes("or-btn", {"or-btn-primary": True, "or-hidden": False})
tag("div", "Hi", attrs={"class": "or-x"})
tag("img", void=True, attrs={"src": "/a.png", "alt": ""})
```

`e()` escapes everything except `None` (empty string) and objects that implement `__html__` — `HtmlString` is the built-in. Pass `HtmlString` into `.label()`, `.helper_text()`, or `.hint()` when the copy already contains markup. Anything untrusted must go through `e()` first.

`classes()` joins tokens and `{name: include?}` dicts, skipping falsy values.

![Orbit HTML helpers (light)](/examples/light/support/html.png)

![Orbit HTML helpers (dark)](/examples/dark/support/html.png)

## URLs

`resolve_public_url()` turns a configured logo or favicon into a root-relative path so assets load from the host the browser actually used. Absolute `http(s)`, protocol-relative `//`, `data:`, and `blob:` values pass through.

Small tools, big surface area — every field, column, and action leans on these.
