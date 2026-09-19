---
title: Checkbox list
description: CheckboxList lets users pick many values from a static option map, with descriptions, columns, and bulk toggle.
---

## Introduction

CheckboxList dehydrates a list of selected option keys — permissions, feature flags, or tag-like sets that should stay visible as checkboxes rather than a multi select. Cast the model attribute to a list/JSON array. For mutually exclusive choices use [Radio](/forms/radio/); for compact multi-pick UIs prefer [Multi select](/forms/multi-select/).

Each variation below includes a short explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic checkbox list

Pass a value → label map to `.options()`. Selected keys are stored as a list in form state.

```python title="app/orbit/resources/app_resource.py"
CheckboxList.make('features')
    .label('Features')
    .options({
        'api': 'API access',
        'sso': 'SSO',
        'webhooks': 'Webhooks',
    })
```

![Orbit Basic checkbox list (light)](/examples/light/forms/checkbox-list/basic.png)

![Orbit Basic checkbox list (dark)](/examples/dark/forms/checkbox-list/basic.png)

## Option descriptions

`.descriptions()` adds helper copy under matching option keys. Use the same keys as `.options()` so each description aligns with its label.

```python title="app/orbit/resources/app_resource.py"
CheckboxList.make('technologies')
    .label('Technologies')
    .options({
        'tailwind': 'Tailwind CSS',
        'alpine': 'Alpine.js',
        'laravel': 'Laravel',
    })
    .descriptions({
        'tailwind': 'Utility-first CSS for rapid UI work.',
        'alpine': 'Lightweight behavior in your markup.',
        'laravel': 'The PHP framework for web artisans.',
    })
```

![Orbit Option descriptions (light)](/examples/light/forms/checkbox-list/descriptions.png)

![Orbit Option descriptions (dark)](/examples/dark/forms/checkbox-list/descriptions.png)

## Multi-column layout

`.options_columns(n)` lays options out in an `n`-column grid so dense permission lists stay scannable without a long vertical stack.

```python title="app/orbit/resources/app_resource.py"
CheckboxList.make('technologies')
    .label('Technologies')
    .options({
        'tailwind': 'Tailwind CSS',
        'alpine': 'Alpine.js',
        'laravel': 'Laravel',
        'livewire': 'Livewire',
    })
    .options_columns(2)
```

![Orbit Multi-column layout (light)](/examples/light/forms/checkbox-list/columns.png)

![Orbit Multi-column layout (dark)](/examples/dark/forms/checkbox-list/columns.png)

## Bulk toggle

`.bulk_toggleable()` adds select-all / deselect-all controls above the list — essential when dozens of options would otherwise require tedious clicking.

```python title="app/orbit/resources/app_resource.py"
CheckboxList.make('features')
    .label('Features')
    .options({
        'api': 'API access',
        'sso': 'SSO',
        'webhooks': 'Webhooks',
        'audit': 'Audit log',
    })
    .bulk_toggleable()
    .options_columns(2)
```

![Orbit Bulk toggle (light)](/examples/light/forms/checkbox-list/bulk-toggle.png)

![Orbit Bulk toggle (dark)](/examples/dark/forms/checkbox-list/bulk-toggle.png)

## Disabling specific options

`.disable_option_when()` receives each option value and returns `True` when that checkbox should be non-interactive — plan-gated features, deprecated flags, etc.

```python title="app/orbit/resources/app_resource.py"
CheckboxList.make('technologies')
    .label('Technologies')
    .options({
        'tailwind': 'Tailwind CSS',
        'alpine': 'Alpine.js',
        'livewire': 'Livewire',
    })
    .disable_option_when(lambda value, **_: value == 'livewire')
```

![Orbit Disabling specific options (light)](/examples/light/forms/checkbox-list/disable-option.png)

![Orbit Disabling specific options (dark)](/examples/dark/forms/checkbox-list/disable-option.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
