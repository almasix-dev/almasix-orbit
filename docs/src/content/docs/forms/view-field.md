---
title: View field
description: ViewField renders custom HTML or callable content beside a label without dehydrating by default.
---

## Introduction

`ViewField` is the escape hatch for read-only custom markup inside a schema. `.content()` accepts a string or callable evaluated with `state` and render context. Defaults `_dehydrated = False`. Content is inserted into `or-view-field` without automatic escaping when you return HTML from a callable — sanitize untrusted data yourself. For interactive controls, subclass `Field` instead (see [Custom fields](/forms/custom-fields/)).

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic view field

Static HTML summary with a label.

```python title="app/orbit/resources/example_resource.py"
ViewField.make('summary')
    .label('Summary')
    .content('<strong>3</strong> open invoices')
```

![Orbit Basic view field (light)](/examples/light/forms/view-field/basic.png)

![Orbit Basic view field (dark)](/examples/dark/forms/view-field/basic.png)

## Callable content

Build markup from record/state at render time. Return a safe HTML string.

```python title="app/orbit/resources/example_resource.py"
ViewField.make('balance')
    .label('Balance')
    .content(lambda state=None, record=None, **_: f'<span class="or-money">{state or 0}</span>')
```

![Orbit Callable content (light)](/examples/light/forms/view-field/callable.png)

![Orbit Callable content (dark)](/examples/dark/forms/view-field/callable.png)

## Hidden when empty

Use `.visible()` closures to omit the field when there is nothing to show.

```python title="app/orbit/resources/example_resource.py"
ViewField.make('warning')
    .label('Warning')
    .content(lambda record=None, **_: getattr(record, 'warning_html', ''))
    .visible(lambda record=None, **_: bool(getattr(record, 'warning_html', None)))
```

![Orbit Hidden when empty (light)](/examples/light/forms/view-field/conditional.png)

![Orbit Hidden when empty (dark)](/examples/dark/forms/view-field/conditional.png)

## Dehydrated view value

If you need the view payload in dehydrated state (for example a signed summary string), opt into dehydration.

```python title="app/orbit/resources/example_resource.py"
ViewField.make('checksum')
    .label('Checksum')
    .content(lambda state=None, **_: state or '')
    .dehydrated(True)
```

![Orbit Dehydrated view value (light)](/examples/light/forms/view-field/dehydrated.png)

![Orbit Dehydrated view value (dark)](/examples/dark/forms/view-field/dehydrated.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
