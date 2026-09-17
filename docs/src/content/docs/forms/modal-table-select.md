---
title: Modal table select
description: Orbit ModalTableSelect — browse records via mountTableSelect.
---

Readonly display + Browse button that mounts a table picker modal.

## Standalone

```python
from almasix.orbit.forms import Form, ModalTableSelect

form = Form.make("demo").schema([
        ModalTableSelect.make("post_id").label("Post")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, ModalTableSelect

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            ModalTableSelect.make("assignee_id")
                .label("Assignee")
                .required(),
        ])
```

## Key methods

- `.label(...) / .required(...)`
- `.disabled(...) / .visible(...)`
- `Renders readonly input + Browse (`wire:click="mountTableSelect(...)")``
- `State is the selected id/display value you wire in`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).


## Preview

![Orbit forms/select (light)](/examples/light/forms/select.png)

![Orbit forms/select (dark)](/examples/dark/forms/select.png)
