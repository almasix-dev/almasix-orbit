---
title: Hidden
description: Hidden stores a value in a bare hidden input without label or field wrapper chrome.
---

## Introduction

`Hidden` renders `<input type="hidden" …>` only — no `wrap_field`, label, or helper. Use it for tenant IDs, CSRF companions the host manages, or sticky foreign keys. Unlike most fields, its `render()` does not short-circuit on `is_visible()`; keep sensitive values server-side when possible.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic hidden

Carry a constant or defaulted value through submit/dehydrate without showing UI.

```python title="app/orbit/resources/example_resource.py"
Hidden.make('tenant_id')
    .default('tenant_acme')
```

![Orbit Basic hidden (light)](/examples/light/forms/hidden/basic.png)

![Orbit Basic hidden (dark)](/examples/dark/forms/hidden/basic.png)

## From record context

Set defaults from closures when filling edit forms so the key always posts with the payload.

```python title="app/orbit/resources/example_resource.py"
Hidden.make('owner_id')
    .default(lambda record=None, **_: getattr(record, 'owner_id', None))
```

![Orbit From record context (light)](/examples/light/forms/hidden/from-record.png)

![Orbit From record context (dark)](/examples/dark/forms/hidden/from-record.png)

## Custom state path

`.state_path()` remaps where the value lives in nested form state when the field name should differ from the wire path.

```python title="app/orbit/resources/example_resource.py"
Hidden.make('token')
    .state_path('meta.invite_token')
    .default('')
```

![Orbit Custom state path (light)](/examples/light/forms/hidden/state-path.png)

![Orbit Custom state path (dark)](/examples/dark/forms/hidden/state-path.png)

## With validation

Hidden fields still participate in `Form.validate` when they have a state path and rules — useful for required foreign keys.

```python title="app/orbit/resources/example_resource.py"
Hidden.make('account_id')
    .required()
    .rules('integer')
```

![Orbit With validation (light)](/examples/light/forms/hidden/validation.png)

![Orbit With validation (dark)](/examples/dark/forms/hidden/validation.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
