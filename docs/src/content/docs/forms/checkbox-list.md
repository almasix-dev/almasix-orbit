---
title: Checkbox list
description: CheckboxList allows many selections from a static option map.
---

## Introduction

CheckboxList allows many selections from a static option map. Bulk toggle adds select-all / deselect-all links; descriptions mirror Radio.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic checkbox list

Feature flags or permissions.

```python
CheckboxList.make('features')
    .label('Features')
    .options({'api': 'API access', 'sso': 'SSO'})
```

![Orbit Basic checkbox list (light)](/examples/light/forms/checkbox-list/basic.png)

![Orbit Basic checkbox list (dark)](/examples/dark/forms/checkbox-list/basic.png)

## Bulk toggle

Select all / deselect all controls.

```python
CheckboxList.make('features')
    .label('Features')
    .options({...})
    .bulk_toggleable()
    .options_columns(2)
```

![Orbit Bulk toggle (light)](/examples/light/forms/checkbox-list/bulk-toggle.png)

![Orbit Bulk toggle (dark)](/examples/dark/forms/checkbox-list/bulk-toggle.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
