---
title: Checkbox list
description: CheckboxList allows many selections from a static option map.
---

## Introduction

CheckboxList allows many selections from a static option map. Bulk toggle adds select-all / deselect-all links; descriptions mirror Radio.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic checkbox list

![Orbit Basic checkbox list (light)](/examples/light/forms/checkbox-list/basic.png)

![Orbit Basic checkbox list (dark)](/examples/dark/forms/checkbox-list/basic.png)

Feature flags or permissions.

```python
(
    CheckboxList.make('features')
    .label('Features')
    .options({'api': 'API access', 'sso': 'SSO'})
)
```

## Bulk toggle

![Orbit Bulk toggle (light)](/examples/light/forms/checkbox-list/bulk-toggle.png)

![Orbit Bulk toggle (dark)](/examples/dark/forms/checkbox-list/bulk-toggle.png)

Select all / deselect all controls.

```python
(
    CheckboxList.make('features')
    .label('Features')
    .options({...})
    .bulk_toggleable()
    .options_columns(2)
)
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
