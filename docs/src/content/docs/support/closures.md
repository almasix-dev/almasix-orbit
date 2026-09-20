---
title: Closures & evaluate
description: Dynamic labels, helpers, visibility, and defaults via almasix.orbit.support.evaluate.
---

Orbit is happiest when configuration can be either a value or a small function. `evaluate()` is the shared switch: if it’s callable, call it; otherwise return it as-is.

```python
from almasix.orbit.support.evaluate import evaluate

evaluate("static")                         # "static"
evaluate(lambda record=None, **_: record["title"], record={"title": "Hi"})
# "Hi"
```

![Orbit evaluate closures (light)](/examples/light/support/closures.png)

![Orbit evaluate closures (dark)](/examples/dark/support/closures.png)

## Resolution order

When the candidate is callable, `evaluate` first **filters** `**ctx` to parameter names the callable actually declares (so `lambda record: …` is not broken by extra utilities). Then it tries:

1. `candidate(**filtered_ctx)`
2. `candidate(*args)` (if positional args were passed)
3. `candidate(*args, **filtered_ctx)`
4. `candidate()`
5. If all raise `TypeError`, returns the callable unchanged

Callables that accept `**kwargs` receive the full context. Builtins without a usable signature get the full context as well.

That means you can write `lambda record=None, **_:` *or* a zero-arg function *or* something that only accepts `record` — Orbit will meet you halfway.

## Where callables show up

On almost every fluent component (`Component` and friends):

| Method | Callable? | Notes |
|--------|-----------|-------|
| `.label(...)` | yes | Falls back to title-cased name |
| `.helper_text(...)` / `.hint(...)` / `.hint_icon(...)` | yes | |
| `.default(...)` | yes | Evaluated via `get_default(**ctx)` |
| `.visible(...)` / `.disabled(...)` | yes | Bool result |
| `.extra_attributes({...})` | values yes | Each value is evaluated |
| Field `.placeholder(...)` / `.required(...)` / `.options(...)` | yes | |
| Action `.url(...)` / `.color(...)` / `.icon(...)` / `.authorize(...)` | yes | |
| Column `.color(...)` / `.url(...)` | yes | Often get `record` + `state` |

```python
from almasix.orbit.forms import TextInput
from almasix.orbit.tables import TextColumn
from almasix.orbit.actions import Action

TextInput.make("slug")
    .label(lambda record=None, **_: "Slug" if record else "New slug")
    .helper_text(lambda **ctx: "Locked" if ctx.get("published") else "Editable")
    .disabled(lambda record=None, **_: bool(record and record.get("published")))
    .default(lambda **_: "untitled")
    .extra_attributes({"data-id": lambda record=None, **_: record and record.get("id")})

TextColumn.make("status").color(
    lambda record=None, state=None, **_: "success" if state == "published" else "gray"
)

Action.make("publish").authorize(lambda user=None, **_: user and user.is_editor)
```

## Passing context

Render / resolve methods take `**ctx` — pass what your callables need:

```python
field.render(state, record=post, user=request.user, published=post.is_published)
column.render_cell(record, user=request.user)
action.render(record=record, user=request.user)
```

Invisible components return empty HTML. Disabled ones still render, but won’t take input.

## Mental model

Think of closures as stage directions, not a second schema language. Same field tree; manners that depend on who’s in the room. For form-focused examples see [Form closures](/forms/closures/). Trusted markup in a label or helper uses [`HtmlString`](/support/overview/#html) so `e()` does not escape it.
