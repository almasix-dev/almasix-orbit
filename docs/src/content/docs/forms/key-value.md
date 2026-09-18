---
title: Key-value
description: KeyValue edits arbitrary string maps as editable rows with add-row actions.
---

## Introduction

KeyValue edits arbitrary string maps as editable rows with add-row actions. Empty state shows a blank row; populated state renders existing pairs.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Empty key-value

![Orbit Empty key-value (light)](/examples/light/forms/key-value/basic.png)

![Orbit Empty key-value (dark)](/examples/dark/forms/key-value/basic.png)

Metadata editor with no initial rows.

```python
KeyValue.make('meta').label('Metadata')
```

## Populated key-value

![Orbit Populated key-value (light)](/examples/light/forms/key-value/populated.png)

![Orbit Populated key-value (dark)](/examples/dark/forms/key-value/populated.png)

Existing key/value pairs.

```python
KeyValue.make('meta').label('Metadata')  # fill({'meta': {'version': '1.0'}})
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
