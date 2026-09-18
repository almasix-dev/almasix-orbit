---
title: Closures
description: Callable labels, options, defaults, visibility, and disabled state on Orbit fields.
---

## Introduction

Static config is enough until a field must react to the record, tenant, or operation. Orbit evaluates callables at render and validation time through `almasix.orbit.support.evaluate`, injecting whatever keyword context you pass into `render()` / `validate()`.

![Orbit text input (light)](/examples/light/forms/text-input/basic.png)

![Orbit text input (dark)](/examples/dark/forms/text-input/basic.png)

Deep dive on the helper itself: [Support closures](/support/closures/).

## What can be a callable?

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

Whatever you pass into `field.render(state, **ctx)` (or the form’s render) becomes keyword args for the callable. Resource pages typically pass `record`, `operation`, and auth-related values from the Conduit host.
