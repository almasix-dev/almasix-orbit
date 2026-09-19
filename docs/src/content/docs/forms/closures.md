---
title: Closures
description: Utility injection cookbook for Orbit form field callables — labels, options, visibility, rules, and dehydrate.
---

## Introduction

Static config is enough until a field must react to the record, tenant, operation, or sibling state. Orbit evaluates callables through `almasix.orbit.support.evaluate`: if the value is callable, it is invoked with a **filtered** keyword context (only parameters the callable declares, unless it accepts `**kwargs`). That is Filament-style utility injection — write `lambda record: …` even when the host passes dozens of extras.

Deep dive on the helper itself: [Support closures](/support/closures/). This page is the forms cookbook.

Each pattern below includes explanation, Python, and screenshots of related chrome.

## How evaluate filters utilities

`evaluate(candidate, *args, **ctx)` tries, in order: `candidate(**filtered)`, `candidate(*args)`, `candidate(*args, **filtered)`, then `candidate()`. If the callable declares `**kwargs`, the full context is passed. Otherwise only named parameters present in `ctx` are injected.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.support.evaluate import evaluate

evaluate(lambda record: record['title'], record={'title': 'Hi'}, unused=1)
# 'Hi' — unused is ignored because the lambda does not declare it
```

![Orbit How evaluate filters utilities (light)](/examples/light/forms/text-input/basic.png)

![Orbit How evaluate filters utilities (dark)](/examples/dark/forms/text-input/basic.png)

## Label, helper, hint, placeholder

Almost every copy surface on `Component` / `Field` accepts a callable: `.label()`, `.helper_text()`, `.hint()`, `.hint_icon()`, `.placeholder()`, `.prefix()`, `.suffix()`, and content slots.

```python title="app/orbit/resources/post_resource.py"
TextInput.make('slug')
    .label(lambda record=None, **_: 'Slug' if record else 'New slug')
    .helper_text(lambda **ctx: 'Locked' if ctx.get('published') else 'Editable')
    .placeholder(lambda operation=None, **_: 'generated-after-save' if operation == 'create' else '')
```

![Orbit Label helper hint placeholder (light)](/examples/light/forms/text-input/with-hint.png)

![Orbit Label helper hint placeholder (dark)](/examples/dark/forms/text-input/with-hint.png)

## Conditional required

`.required()` accepts a bool or callable. The callable is evaluated in `is_required(**ctx)` during both render (asterisk, unless overridden by `.mark_as_required()`) and `get_rules()`.

```python title="app/orbit/resources/post_resource.py"
TextInput.make('slug')
    .required(lambda data=None, operation=None, **_: (
        operation == 'create' or bool((data or {}).get('publish'))
    ))
```

![Orbit Conditional required (light)](/examples/light/forms/text-input/required.png)

![Orbit Conditional required (dark)](/examples/dark/forms/text-input/required.png)

## Visibility and disabled

`.visible()` / `.disabled()` take bools or callables. Field also offers `.disabled_on(*operations)`, `.hidden_on(*operations)`, and `.visible_on(*operations)` for create/edit/view without writing lambdas.

```python title="app/orbit/resources/invoice_resource.py"
TextInput.make('refund_reason')
    .visible(lambda record=None, **_: bool(record and record.get('status') == 'refunded'))

TextInput.make('external_id')
    .disabled_on('edit', 'view')
    .visible_on('create', 'edit')
```

![Orbit Visibility and disabled (light)](/examples/light/forms/text-input/disabled.png)

![Orbit Visibility and disabled (dark)](/examples/dark/forms/text-input/disabled.png)

## Dynamic options

`.options()` may be a mapping or a callable evaluated at render (and when resolving option groups). Relationship selects use `.relationship()` instead of hand-rolled options when the related model is known.

```python title="app/orbit/resources/task_resource.py"
from almasix.orbit.forms import Select

Select.make('assignee_id')
    .label('Assignee')
    .options(lambda tenant=None, **_: load_assignees(tenant))
    .searchable()
```

![Orbit Dynamic options (light)](/examples/light/forms/select/searchable.png)

![Orbit Dynamic options (dark)](/examples/dark/forms/select/searchable.png)

## Defaults

`.default()` stores a static value or callable. Hosts evaluate via `get_default(**ctx)` when filling empty state.

```python title="app/orbit/resources/ticket_resource.py"
TextInput.make('priority')
    .default(lambda **_: 'medium')

Hidden.make('account_id')
    .default(lambda user=None, **_: getattr(user, 'account_id', None))
```

![Orbit Defaults (light)](/examples/light/forms/hidden/basic.png)

![Orbit Defaults (dark)](/examples/dark/forms/hidden/basic.png)

## After state updated

`.after_state_updated(callback)` stores a Python callback for the host to run when state changes. `.after_state_updated_js(script)` attaches a JS snippet attribute for Alpine-side reactions.

```python title="app/orbit/resources/product_resource.py"
TextInput.make('title')
    .live()
    .after_state_updated(lambda state, set_state=None, **_: (
        set_state('slug', slugify(state)) if set_state and state else None
    ))
    .after_state_updated_js('console.debug($event)')
```

![Orbit After state updated (light)](/examples/light/forms/text-input/basic.png)

![Orbit After state updated (dark)](/examples/dark/forms/text-input/basic.png)

## Dehydrate transforms

`.trim()` and `.strip_characters()` run inside `apply_dehydrate_transforms` before `.dehydrate_state_using()`. Custom dehydrate callbacks receive the (possibly trimmed) value plus context.

```python title="app/orbit/resources/product_resource.py"
TextInput.make('sku')
    .strip_characters('- ')
    .trim()
    .dehydrate_state_using(lambda value, **_: (value or '').upper())
```

![Orbit Dehydrate transforms (light)](/examples/light/forms/text-input/trim.png)

![Orbit Dehydrate transforms (dark)](/examples/dark/forms/text-input/trim.png)

## Validation callables

Pass callables to `.rules()`. Validation context includes `value`, `state`, `field`, `attribute`, `operation`, and optional `unique` / `exists` checkers.

```python title="app/orbit/resources/team_resource.py"
TextInput.make('name')
    .rules(lambda value, **_: (
        True if value and value.lower() != 'admin' else 'That name is reserved.'
    ))
```

![Orbit Validation callables (light)](/examples/light/forms/text-input/required.png)

![Orbit Validation callables (dark)](/examples/dark/forms/text-input/required.png)

## Disable option when

Select-family fields support `.disable_option_when(callback)`. The callback receives `value`, `label`, `state`, and render context; returning true disables that `<option>`.

```python title="app/orbit/resources/order_resource.py"
Select.make('status')
    .options({'draft': 'Draft', 'paid': 'Paid', 'void': 'Void'})
    .disable_option_when(lambda value, record=None, **_: (
        value == 'void' and not getattr(record, 'is_manager', False)
    ))
```

![Orbit Disable option when (light)](/examples/light/forms/select/basic.png)

![Orbit Disable option when (dark)](/examples/dark/forms/select/basic.png)

## Repeater item labels

`.item_label()` on Repeater/Builder accepts callables with `index`, `item`, and `state`.

```python title="app/orbit/resources/customer_resource.py"
Repeater.make('addresses')
    .schema([TextInput.make('city')])
    .item_label(lambda index, item=None, **_: (item or {}).get('city') or f'Address {index + 1}')
```

![Orbit Repeater item labels (light)](/examples/light/forms/repeater/basic.png)

![Orbit Repeater item labels (dark)](/examples/dark/forms/repeater/basic.png)

## View field and content slots

`ViewField.content()` and Field content slots (`above_label`, `below_content`, …) accept callables. Slot/HTML content is not auto-escaped — sanitize untrusted input.

```python title="app/orbit/resources/invoice_resource.py"
ViewField.make('total')
    .content(lambda state=None, **_: f'<strong>{state or 0}</strong>')

TextInput.make('notes')
    .above_content(lambda operation=None, **_: 'Visible on invoices' if operation == 'edit' else '')
```

![Orbit View field and content slots (light)](/examples/light/forms/view-field/basic.png)

![Orbit View field and content slots (dark)](/examples/dark/forms/view-field/basic.png)

## Typical utility names

Hosts pass utilities as keyword arguments into render and validate. Declare only the names you need — `evaluate` drops the rest unless the callable accepts `**kwargs`. The table below is the usual vocabulary across Orbit resources.

```python title="app/orbit/pages/edit_post.py"
field.render(
    state.get('slug'),
    record=post,
    state=state,
    operation='edit',
    user=request.user,
    tenant=request.tenant,
    model=Post,
    resource=self,
)

errors = form.validate(state, operation='edit', record=post, user=request.user)
```

![Orbit Typical utility names (light)](/examples/light/forms/text-input/basic.png)

![Orbit Typical utility names (dark)](/examples/dark/forms/text-input/basic.png)

| Utility | Common sources |
|---------|----------------|
| `record` | Resource edit/view fill |
| `state` / `data` | Full form state |
| `value` | Current field value (validation, some callbacks) |
| `operation` | `create` / `edit` / `view` from Form or ctx |
| `model` / `resource` | Relationship resolution |
| `user` / `tenant` | Auth / tenancy from host |
| `index` / `item` | Repeater item label |
| `field` / `attribute` | Validation |

## Mental model

Treat closures as stage directions, not a second schema language. Same field tree; manners that depend on who is in the room. Prefer small lambdas that name their utilities explicitly over grabbing `**ctx` and digging.

```python title="app/orbit/resources/post_resource.py"
# Prefer:
TextInput.make('slug').disabled(lambda record=None, **_: bool(record and record.get('published')))

# Avoid opaque catch-alls unless you truly need every utility:
TextInput.make('slug').disabled(lambda **ctx: bool((ctx.get('record') or {}).get('published')))
```

![Orbit Mental model (light)](/examples/light/forms/text-input/disabled.png)

![Orbit Mental model (dark)](/examples/dark/forms/text-input/disabled.png)

For building new field types see [Custom fields](/forms/custom-fields/).
