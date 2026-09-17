---
title: Testing
description: Assert Orbit resource shape with LiveResource.
---

Orbit ships a tiny helper for resource tests — assert the form and table look right, and that validation fires.

```python
from almasix.orbit.testing import LiveResource

from app.orbit.post_resource import PostResource


def test_post_resource():
    live = LiveResource(PostResource)

    live.assert_form_has_field("title")
    live.assert_table_has_column("title")

    errors = live.fill_form({})
    assert "title" in errors

    errors = live.fill_form({"title": "Hello", "slug": "hello"})
    assert errors == {}
```

## What it does

| Method | Behaviour |
|--------|-----------|
| `assert_form_has_field(name)` | Field exists on `get_form()` |
| `assert_table_has_column(name)` | Column exists on `get_table()` |
| `fill_form(data)` | Returns `form.validate(data)` |

Import from `almasix.orbit.testing` — it’s not re-exported on the top-level `almasix.orbit` package.

## Tips

- Test permissions with real user fixtures and `Resource.can_*`.
- For HTML smoke tests, call `.render()` on forms/tables and assert on `.or-*` class names.
- Keep resource classes free of request state so `LiveResource` stays a pure unit check.

Pair with Almasix’s HTTP and console test guides in the [main docs](https://docs.almasix.com/testing/).
