---
title: Closures
description: Callable labels, options, defaults, visibility, and disabled state on Orbit fields.
---

Static config is fine until the field needs to know about the record, the user, or the weather on Mars. Orbit evaluates callables at render / validation time via `almasix.orbit.support.evaluate`.

Deep dive on the helper itself: [Support closures](/support/closures/).

## What can be a callable?

On fields (and most components):

| Surface | Example |
|---------|---------|
| `.label(...)` | `lambda record=None, **_: record["name"]` |
| `.helper_text(...)` / `.hint(...)` | Context-aware help |
| `.placeholder(...)` | Dynamic hint text |
| `.default(...)` | Prefill from request / tenant |
| `.options(...)` | Load choices lazily |
| `.visible(...)` / `.disabled(...)` | Show/hide or lock |
| `.required(...)` | Conditionally required |

```python
from almasix.orbit.forms import Select, TextInput

Select.make("assignee_id")
    .label(lambda **_: "Assignee")
    .options(lambda **ctx: load_assignees(ctx.get("tenant")))
    .visible(lambda record=None, **_: bool(record))
    .disabled(lambda user=None, **_: not getattr(user, "is_manager", False))

TextInput.make("slug")
    .required(lambda data=None, **_: bool((data or {}).get("publish")))
    .helper_text(lambda **_: "Locked after publish")
```

## Passing context

Whatever you pass into `field.render(state, **ctx)` (or the form’s render) becomes keyword args for the callable:

```python
form.render(form.get_state(), record=post, user=request.user, tenant=tenant)
```

Match parameter names to what you pass (`record=`, `user=`, …). Extra kwargs are fine — `evaluate` tries a few call shapes.

## Options that aren’t static

```python
Select.make("status").options({
    "draft": "Draft",
    "published": "Published",
})

# Same idea, deferred:
Select.make("status").options(lambda **_: fetch_statuses())
```

`get_options(**ctx)` always returns a plain `dict`.

## Invisible ≠ deleted

`.visible(False)` (or a callable that returns false) skips HTML. Dehydration still respects `.dehydrated()` — hide chrome carefully if the value must round-trip.

## Related

- [Support closures](/support/closures/) — `evaluate` behaviour
- [Standalone forms](/components/form/)
- [Forms overview](/forms/overview/)

## Preview

![Orbit forms/overview (light)](/examples/light/forms/overview.png)

![Orbit forms/overview (dark)](/examples/dark/forms/overview.png)
