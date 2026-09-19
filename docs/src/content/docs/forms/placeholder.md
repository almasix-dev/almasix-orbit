---
title: Placeholder
description: Placeholder shows read-only content in the form without dehydrating by default.
---

## Introduction

`Placeholder` is a non-input field: it renders `or-placeholder` with a paragraph of content. Defaults `_dehydrated = False` so it does not participate in save payloads unless you call `.dehydrated(True)`. Use `.content()` for static copy, or let state fill the paragraph when content is empty. Prefer [View field](/forms/view-field/) when you need arbitrary HTML or callables.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic placeholder

Static instructional or summary text between real inputs.

```python title="app/orbit/resources/example_resource.py"
Placeholder.make('billing_note')
    .content('Invoices are emailed on the 1st of each month.')
```

![Orbit Basic placeholder (light)](/examples/light/forms/placeholder/basic.png)

![Orbit Basic placeholder (dark)](/examples/dark/forms/placeholder/basic.png)

## Content from state

When `.content()` is empty, render falls back to the field state string — useful for computed summaries filled into form state.

```python title="app/orbit/resources/example_resource.py"
Placeholder.make('plan_summary')
    .label('Plan')
    .default('Pro · billed annually')
```

![Orbit Content from state (light)](/examples/light/forms/placeholder/from-state.png)

![Orbit Content from state (dark)](/examples/dark/forms/placeholder/from-state.png)

## Visible only on edit

Combine with `.visible_on('edit')` / `.hidden_on('create')` so help text appears only for existing records.

```python title="app/orbit/resources/example_resource.py"
Placeholder.make('edit_hint')
    .content('Changing the slug will break existing links.')
    .visible_on('edit')
```

![Orbit Visible only on edit (light)](/examples/light/forms/placeholder/visible-on.png)

![Orbit Visible only on edit (dark)](/examples/dark/forms/placeholder/visible-on.png)

## Dehydrated placeholder

Rarely, you may want placeholder text included in dehydrated state — opt in with `.dehydrated(True)`.

```python title="app/orbit/resources/example_resource.py"
Placeholder.make('snapshot_label')
    .content('legacy-import')
    .dehydrated(True)
```

![Orbit Dehydrated placeholder (light)](/examples/light/forms/placeholder/dehydrated.png)

![Orbit Dehydrated placeholder (dark)](/examples/dark/forms/placeholder/dehydrated.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
