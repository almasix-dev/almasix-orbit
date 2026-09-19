---
title: Key-value
description: KeyValue edits a dictionary as rows of key and value inputs with an Add row action.
---

## Introduction

`KeyValue` expects dict state. Each entry renders two inputs; empty state seeds one blank row. Values bind with `wire:model="{name}.{key}"`. The Add button calls `addKeyValueRow`. Use it for metadata maps, HTTP headers, and feature flags without defining a Repeater schema.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic key-value

Empty editor with one blank row and an Add row button.

```python title="app/orbit/resources/example_resource.py"
KeyValue.make('meta')
    .label('Metadata')
    .helper_text('Arbitrary string keys and values.')
```

![Orbit Basic key-value (light)](/examples/light/forms/key-value/basic.png)

![Orbit Basic key-value (dark)](/examples/dark/forms/key-value/basic.png)

## Populated key-value

When state is a dict, rows hydrate from keys and values. Keys are submitted as `{name}_key_{i}` companions for host normalization.

```python title="app/orbit/resources/example_resource.py"
KeyValue.make('headers')
    .label('Headers')
    .default({'Accept': 'application/json', 'X-Request-Id': ''})
```

![Orbit Populated key-value (light)](/examples/light/forms/key-value/populated.png)

![Orbit Populated key-value (dark)](/examples/dark/forms/key-value/populated.png)

## Required metadata

Mark the field required when at least one pair must exist; enforce richer shapes with callable `.rules()` that inspect the dict.

```python title="app/orbit/resources/example_resource.py"
KeyValue.make('settings')
    .label('Settings')
    .required()
    .rules(lambda value, **_: True if value else 'Add at least one setting.')
```

![Orbit Required metadata (light)](/examples/light/forms/key-value/required.png)

![Orbit Required metadata (dark)](/examples/dark/forms/key-value/required.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
