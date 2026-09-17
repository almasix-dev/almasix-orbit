---
title: Placeholder
description: Orbit Placeholder — display-only content that is not dehydrated.
---

Read-only copy inside the form — tips, computed summaries, gentle reminders.

## Standalone

```python
from almasix.orbit.forms import Form, Placeholder

form = Form.make("demo").schema([
        Placeholder.make("hint")
            .content("Slugs can’t change after publish.")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Placeholder

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Placeholder.make("stats")
                .content("Word count updates after save.")
                .label("Stats"),
        ])
```

## Key methods

- `.content(text) — static HTML-escaped body`
- `Not dehydrated by default (`_dehydrated = False`)`
- `.label(...) optional; body can fall back to state`
- `.visible(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/forms/overview.png)

![Orbit form example (dark)](/examples/dark/forms/overview.png)

