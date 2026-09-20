---
title: Testing
description: Assert resource shape with LiveResource, smoke-render HTML, and check permissions without a browser.
---

Orbit tests are ordinary pytest. You do not need a running panel to prove a resource’s form, table, or page host is wired the way you think. Reach for a browser only when you care about Alpine clicks and Conduit round trips.

## LiveResource

`LiveResource` is a tiny double around a [resource](/resources/overview/) class. It builds the form and table once and asserts on their shape.

```python title="tests/test_post_resource.py"
from almasix.orbit.testing import LiveResource

from app.orbit.resources.post_resource import PostResource


def test_post_resource():
    live = LiveResource(PostResource)

    live.assert_form_has_field("title")
    live.assert_table_has_column("title")

    errors = live.fill_form({})
    assert "title" in errors

    errors = live.fill_form({"title": "Hello", "slug": "hello"})
    assert errors == {}
```

![Orbit LiveResource checks a form (light)](/examples/light/testing/live-resource.png)

![Orbit LiveResource checks a form (dark)](/examples/dark/testing/live-resource.png)

Import from `almasix.orbit.testing` — it is not re-exported on the top-level `almasix.orbit` package.

### What it does

| Method | Behaviour |
|--------|-----------|
| `form()` | `resource.get_form()` |
| `table()` | `resource.get_table()` |
| `assert_form_has_field(name)` | `name` is in `form.get_components()` |
| `assert_table_has_column(name)` | `name` is in the table’s columns |
| `fill_form(data)` | `form.fill(data)` then `form.validate(data)` — returns the error map |

`fill_form` is the cheapest way to prove required fields and custom rules fire. Nested repeaters and relationship fields still validate through the same `Form.validate` path.

## HTML smoke tests

Call `.render()` on forms, tables, infolists, and [page hosts](/resources/pages/) and assert on Orbit’s `.or-*` classes. This catches missing labels, empty schemas, and layout regressions without Playwright.

```python title="tests/test_post_html.py"
from almasix.orbit.panels.pages import ListRecords, CreateRecord, ViewRecord

from app.orbit.resources.post_resource import PostResource


class PostList(ListRecords):
    resource = PostResource


class PostCreate(CreateRecord):
    resource = PostResource


class PostView(ViewRecord):
    resource = PostResource


def test_list_renders_table():
    html = PostList.render(records=[{"id": 1, "title": "Hello"}])
    assert "or-table" in html
    assert "Hello" in html


def test_create_renders_form():
    html = PostCreate.render(state={"title": ""})
    assert "or-form" in html
    assert 'name="title"' in html or "title" in html


def test_view_renders_infolist():
    html = PostView.render(record={"id": 1, "title": "Hello", "slug": "hello"})
    assert "or-page-view" in html
```

![Orbit HTML smoke on a list page (light)](/examples/light/testing/html-smoke.png)

![Orbit HTML smoke on a list page (dark)](/examples/dark/testing/html-smoke.png)

Keep resource classes free of request objects so these checks stay unit tests. Pass `user=...` or `operation="create"` in `**ctx` when a field’s `.visible()` / `.disabled()` closure needs it.

## Permissions

`Resource.can_view_any`, `can_create`, `can_update`, and `can_delete` are plain callables. Fixture a user and assert:

```python title="tests/test_post_permissions.py"
def test_editors_can_update(editor, post):
    assert PostResource.can_update(editor, post)


def test_guests_cannot_delete(guest, post):
    assert not PostResource.can_delete(guest, post)
```

Action authorization is the same idea: `.authorize(...)` plus `.can(**ctx)` — see [Actions](/actions/overview/).

## Notifications

Flash toasts are in-memory until you persist them. In a test, send through `Notifier` and assert on `get_notifications()` (or your store):

```python title="tests/test_post_toasts.py"
from almasix.orbit.notifications import Notification, get_notifier


def test_created_toast():
    notifier = get_notifier()
    notifier.send(Notification.make(title="Post created").success())
    titles = [n.title for n in notifier.peek_flash()]
    assert "Post created" in titles
```

Database and live adapters have their own stores — see [Database notifications](/notifications/database-notifications/) and [Broadcast notifications](/notifications/broadcast-notifications/).

## Tips

- Prefer `LiveResource` for schema shape; prefer `.render()` for chrome; prefer HTTP tests for hosts that mutate records.
- Reset process-global registries (`clear_render_hooks()`, notification store, broadcast hub) in `setup_function` when tests share a process.
- Pair with Almasix’s HTTP and console guides in the [framework testing docs](https://docs.almasix.com/testing/).
