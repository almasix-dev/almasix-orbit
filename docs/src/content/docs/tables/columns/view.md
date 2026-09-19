---
title: View column
description: ViewColumn — custom HTML for cells that don't fit a stock column type, with optional link wrapping.
---

When no stock column fits, `ViewColumn` lets you render arbitrary HTML — a string, or a callback that returns one:

```python
from almasix.orbit.tables import ViewColumn

ViewColumn.make("progress").content(
    lambda state=None, **_: (
        f'<div class="or-progress" role="progressbar" aria-valuenow="{int(state or 0)}">'
        f'<span style="width:{int(state or 0)}%"></span></div>'
    ),
)
```

This is distinct from the layout [`View`](/tables/layout/) component — `ViewColumn` is a **column type** (one value, one cell). Layout `View` wraps several *child columns* inside one cell. Reach for `ViewColumn` first; move to layout `View` only when you need to compose multiple columns together.

## Setting the content

`.content()` accepts a plain string for static markup, or a callback that receives `record` / `state` for dynamic markup. Escape any untrusted values yourself, e.g. with `almasix.orbit.support.html.e`:

```python
from almasix.orbit.support.html import e

ViewColumn.make("contact").content(
    lambda record=None, **_: (
        f'<strong>{e(record.get("name", ""))}</strong><br />'
        f'<a href="mailto:{e(record.get("email", ""))}">{e(record.get("email", ""))}</a>'
    ),
)
```

The result is inserted inside a wrapping `<div class="or-view-column">` — add your own classes inside the content for further styling.

## Opening a URL

`ViewColumn` supports the same [`.url()`](/tables/columns/text/#opening-urls) helper as `TextColumn` — the whole rendered cell becomes a link:

```python
ViewColumn.make("progress")
    .content(lambda state=None, **_: f"{int(state or 0)}%")
    .url(lambda record=None, **_: f"/projects/{record['id']}")
    .open_url_in_new_tab()
```

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, ViewColumn
from almasix.orbit.support.html import e

Table.make("customers").columns([
    TextColumn.make("company").searchable().sortable(),
    ViewColumn.make("contact").content(
        lambda record=None, **_: (
            f'<strong>{e(record.get("name", ""))}</strong><br />'
            f'<a href="mailto:{e(record.get("email", ""))}">{e(record.get("email", ""))}</a>'
        ),
    ),
    ViewColumn.make("progress")
        .label("Progress")
        .content(lambda state=None, **_: f"{int(state or 0)}%")
        .url(lambda record=None, **_: f"/projects/{record['id']}"),
]).records([
    {
        "id": 1,
        "company": "Acme",
        "name": "Ada Lovelace",
        "email": "ada@acme.test",
        "progress": 80,
    },
    {
        "id": 2,
        "company": "Orbit Labs",
        "name": "Grace Hopper",
        "email": "grace@orbitlabs.test",
        "progress": 45,
    },
])
```

## Key methods

| Method | Effect |
|--------|--------|
| `.content(str \| callable)` | HTML body for the cell |
| `.url(str \| callable)` / `.open_url_in_new_tab()` | Wrap the cell in a link |
| `.label(...)` / `.toggleable(...)` / `.align_start()` | Inherited [shared helpers](/tables/columns/overview/) |
| Callable kwargs | Commonly `record`, `state` |

## Preview

![View column (light)](/examples/light/tables/view-column.png)
![View column (dark)](/examples/dark/tables/view-column.png)

![Tags / view (light)](/examples/light/tables/tags-view.png)
![Tags / view (dark)](/examples/dark/tables/tags-view.png)
