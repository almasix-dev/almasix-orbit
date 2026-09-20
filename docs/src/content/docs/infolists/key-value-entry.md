---
title: Key-value entry
description: KeyValueEntry displays a dict as a two-column table with customizable key and value headers.
---

## Introduction

`KeyValueEntry` turns a mapping into an `or-key-value` table — useful for meta blobs, settings maps, and sparse attribute bags.

## Basic key-value entry

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import KeyValueEntry

KeyValueEntry.make("meta").label("Meta")
```

![Orbit Key-value entry basic (light)](/examples/light/infolists/key-value-entry/basic.png)

![Orbit Key-value entry basic (dark)](/examples/dark/infolists/key-value-entry/basic.png)

## Custom column labels

`.key_label(...)` and `.value_label(...)` rename the header cells (defaults `Key` / `Value`).

```python title="app/orbit/resources/post_resource.py"
KeyValueEntry.make("meta")
    .label("Meta")
    .key_label("Property")
    .value_label("Content")
```

![Orbit Key-value entry labels (light)](/examples/light/infolists/key-value-entry/labels.png)

![Orbit Key-value entry labels (dark)](/examples/dark/infolists/key-value-entry/labels.png)

## API cheat sheet

| Method | Notes |
|--------|-------|
| `.key_label` | Header for the key column |
| `.value_label` | Header for the value column |
| Shared chrome | Label, helper, hint — see [overview](/infolists/overview/) |
