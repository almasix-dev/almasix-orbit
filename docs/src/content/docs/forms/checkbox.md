---
title: Checkbox
description: Checkbox renders a single boolean control with an inline or stacked label.
---

## Introduction

Checkbox stores a boolean — consent flags, feature toggles, and admin gates. Prefer [Toggle](/forms/toggle/) when you want switch styling, or [Checkbox list](/forms/checkbox-list/) when users pick many keys from a set. Cast the model attribute to `bool` so dehydrated `True` / `False` round-trip cleanly.

Each variation below includes a short explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic checkbox

The default layout places the label beside the box. The field name is the wire path; the label is display-only chrome.

```python title="app/orbit/resources/user_resource.py"
Checkbox.make('terms')
    .label('Accept terms and conditions')
```

![Orbit Basic checkbox (light)](/examples/light/forms/checkbox/basic.png)

![Orbit Basic checkbox (dark)](/examples/dark/forms/checkbox/basic.png)

## Inline label

`.inline()` is the default: the label sits beside the checkbox on one row. Pass `.inline(False)` to stack the label above the checkbox when the copy is long or you want field alignment with stacked text inputs.

```python title="app/orbit/resources/user_resource.py"
Checkbox.make('is_admin')
    .label('Administrator')
    .inline(False)
```

![Orbit Inline label (light)](/examples/light/forms/checkbox/inline.png)

![Orbit Inline label (dark)](/examples/dark/forms/checkbox/inline.png)

## Default value

`.default(True)` pre-checks the box on create forms when no dehydrated state exists yet. Use sparingly — defaults that opt users into marketing or elevated roles are easy to miss.

```python title="app/orbit/resources/user_resource.py"
Checkbox.make('subscribe')
    .label('Subscribe to product updates')
    .default(True)
```

![Orbit Default value (light)](/examples/light/forms/checkbox/default.png)

![Orbit Default value (dark)](/examples/dark/forms/checkbox/default.png)

## Required

`.required()` marks the field and adds a required validation rule so submit fails when the box is unchecked — typical for terms acceptance.

```python title="app/orbit/resources/user_resource.py"
Checkbox.make('terms')
    .label('I agree to the terms of service')
    .required()
```

![Orbit Required (light)](/examples/light/forms/checkbox/required.png)

![Orbit Required (dark)](/examples/dark/forms/checkbox/required.png)

## Disabled

`.disabled()` renders a non-interactive checkbox for read-only review screens or when permission checks forbid edits. State still dehydrates if present.

```python title="app/orbit/resources/user_resource.py"
Checkbox.make('verified')
    .label('Email verified')
    .disabled()
```

![Orbit Disabled (light)](/examples/light/forms/checkbox/disabled.png)

![Orbit Disabled (dark)](/examples/dark/forms/checkbox/disabled.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
