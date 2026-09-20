---
title: Key-value
description: KeyValue edits a dictionary as rows of key and value inputs, with add, rename, delete, and lock-keys controls.
---

## Introduction

`KeyValue` is the field for a map of strings: metadata, HTTP headers, feature flags. Each entry is a row. The host keeps the dict in form state through four methods:

- `addKeyValueRow(name)` — append a unique empty key
- `setKeyValueKey(name, old, new)` — rename a key without losing its value
- `setKeyValueValue` via `wire:model="{name}.{key}"`
- `removeKeyValueRow(name, key)`

Empty state shows one blank row so the operator has somewhere to type. `.editable_keys(False)` locks names; `.addable(False)` / `.deletable(False)` hide those actions.

```python title="app/orbit/resources/post_resource.py"
KeyValue.make("meta")
    .label("Metadata")
    .key_label("Attribute")
    .value_label("Value")
    .add_action_label("Add attribute")
```

Each variation below includes the fluent API and light/dark screenshots of the rendered control.

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

## Editing rows

Rename a key, change a value, or remove a row. The host rewrites the dict in place so the next render shows the new keys.

```python title="app/orbit/resources/example_resource.py"
KeyValue.make("meta")
    .label("Metadata")
    .key_label("Attribute")
    .value_label("Detail")
    .add_action_label("Add attribute")
    .reorderable()
```

![Orbit Editing rows (light)](/examples/light/forms/key-value/editing.png)

![Orbit Editing rows (dark)](/examples/dark/forms/key-value/editing.png)

## Locked keys

`.editable_keys(False)` makes the key column readonly. Combine with `.addable(False)` and `.deletable(False)` when the map’s shape is fixed (for example a settings blob the operator may only fill in).

```python title="app/orbit/resources/example_resource.py"
KeyValue.make("seo")
    .label("SEO")
    .editable_keys(False)
    .addable(False)
    .deletable(False)
```

![Orbit Locked keys (light)](/examples/light/forms/key-value/locked-keys.png)

![Orbit Locked keys (dark)](/examples/dark/forms/key-value/locked-keys.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
