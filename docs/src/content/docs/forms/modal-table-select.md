---
title: Modal table select
description: ModalTableSelect shows a readonly summary input and a Browse button that calls mountTableSelect — not an in-package modal table.
---

## Introduction

**Honest scope:** `ModalTableSelect` does **not** embed an Orbit table or ship a modal. It renders a readonly text input bound with `wire:model` plus a Browse button that fires `wire:click="mountTableSelect('{name}')"`. The Conduit host must implement `mountTableSelect` (open a modal, table, or drawer) and write the chosen key back into form state. Fluent Select APIs exist on the class hierarchy but this render path ignores option HTML — document and use the display + Browse chrome.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic modal table select

Readonly value display with a Browse action. Empty state shows a blank input until the host fills state.

```python title="app/orbit/resources/example_resource.py"
ModalTableSelect.make('author_id')
    .label('Author')
    .helper_text('Browse opens the host table picker.')
```

![Orbit Basic modal table select (light)](/examples/light/forms/modal-table-select/basic.png)

![Orbit Basic modal table select (dark)](/examples/dark/forms/modal-table-select/basic.png)

## With existing value

When state is set (id or label string), the readonly input shows it. Hosts often store the primary key and resolve labels separately.

```python title="app/orbit/resources/example_resource.py"
ModalTableSelect.make('product_id')
    .label('Product')
    .default('sku_100')
```

![Orbit With existing value (light)](/examples/light/forms/modal-table-select/populated.png)

![Orbit With existing value (dark)](/examples/dark/forms/modal-table-select/populated.png)

## Required browse field

`.required()` still injects validation so save fails until the host writes a value after Browse.

```python title="app/orbit/resources/example_resource.py"
ModalTableSelect.make('customer_id')
    .label('Customer')
    .required()
```

![Orbit Required browse field (light)](/examples/light/forms/modal-table-select/required.png)

![Orbit Required browse field (dark)](/examples/dark/forms/modal-table-select/required.png)

## Disabled on view

Use `.disabled_on('view')` so Browse is inactive on view operations while still showing the summary.

```python title="app/orbit/resources/example_resource.py"
ModalTableSelect.make('invoice_id')
    .label('Invoice')
    .disabled_on('view')
```

![Orbit Disabled on view (light)](/examples/light/forms/modal-table-select/disabled-on-view.png)

![Orbit Disabled on view (dark)](/examples/dark/forms/modal-table-select/disabled-on-view.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
