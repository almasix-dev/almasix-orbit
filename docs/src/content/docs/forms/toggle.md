---
title: Toggle
description: Toggle is a styled switch built on Checkbox semantics — same boolean binding, richer on/off chrome.
---

## Introduction

Toggle shares Checkbox’s boolean wire binding and validation surface, but renders as a switch. Use it for settings panels, feature flags, and anywhere an on/off metaphor reads clearer than a tick box. Pair toggles in Flex rows for compact preference lists.

Each variation below includes a short explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic toggle

Label beside a switch. Checked state dehydrates as `True`; unchecked as `False`.

```python title="app/orbit/resources/user_resource.py"
Toggle.make('active')
    .label('Active account')
```

![Orbit Basic toggle (light)](/examples/light/forms/toggle/basic.png)

![Orbit Basic toggle (dark)](/examples/dark/forms/toggle/basic.png)

## On and off colors

`.on_color()` and `.off_color()` map to Orbit/Filament color tokens (`success`, `danger`, `warning`, `primary`, …) so the track communicates state beyond position alone.

```python title="app/orbit/resources/user_resource.py"
Toggle.make('is_admin')
    .label('Administrator')
    .on_color('success')
    .off_color('danger')
```

![Orbit On and off colors (light)](/examples/light/forms/toggle/colors.png)

![Orbit On and off colors (dark)](/examples/dark/forms/toggle/colors.png)

## On and off icons

`.on_icon()` and `.off_icon()` place Heroicons inside the thumb for each state — useful when color alone is not enough (e.g. bolt vs user).

```python title="app/orbit/resources/user_resource.py"
Toggle.make('is_admin')
    .label('Administrator')
    .on_icon('heroicon-m-bolt')
    .off_icon('heroicon-m-user')
```

![Orbit On and off icons (light)](/examples/light/forms/toggle/icons.png)

![Orbit On and off icons (dark)](/examples/dark/forms/toggle/icons.png)

## Inline label

Like Checkbox, toggles default to an adjacent label. `.inline(False)` stacks the label above the switch when aligning with other stacked fields.

```python title="app/orbit/resources/user_resource.py"
Toggle.make('notifications')
    .label('Email notifications')
    .inline(False)
```

![Orbit Inline label (light)](/examples/light/forms/toggle/inline.png)

![Orbit Inline label (dark)](/examples/dark/forms/toggle/inline.png)

## Default value

`.default(True)` turns the switch on for new records before the user interacts. Combine with helper text when the default has side effects.

```python title="app/orbit/resources/user_resource.py"
Toggle.make('newsletter')
    .label('Weekly newsletter')
    .default(True)
    .helper_text('You can change this later in settings.')
```

![Orbit Default value (light)](/examples/light/forms/toggle/default.png)

![Orbit Default value (dark)](/examples/dark/forms/toggle/default.png)

## Required and disabled

`.required()` demands the toggle be on; `.disabled()` freezes the control for audit or permission-gated views. Both APIs match Checkbox.

```python title="app/orbit/resources/user_resource.py"
Toggle.make('tos')
    .label('I accept the terms')
    .required()

Toggle.make('locked_flag')
    .label('System flag')
    .disabled()
```

![Orbit Required and disabled (light)](/examples/light/forms/toggle/required-disabled.png)

![Orbit Required and disabled (dark)](/examples/dark/forms/toggle/required-disabled.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
