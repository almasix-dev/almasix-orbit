---
title: Global search
description: One search box in the topbar that finds records across every resource on a panel.
---

Global search puts a single box in the panel topbar. Type two characters and Orbit searches every resource that opted in, groups the hits by resource, and links straight to each record's view page.

![Orbit global search results (light)](/examples/light/resources/global-search.png)

![Orbit global search results (dark)](/examples/dark/resources/global-search.png)

## Opt a resource in

A resource joins global search the moment it declares which attributes to match:

```python title="app/orbit/resources/post_resource.py"
class PostResource(Resource):
    model = Post
    record_title_attribute = "title"
    global_search_attributes = ("title", "body")
    global_search_result_details = ("status", "author")
```

- `global_search_attributes` — attributes matched against the search term (case-insensitive substring).
- `global_search_result_details` — attributes shown as small labelled pairs under each result. Empty values are skipped.
- `record_title_attribute` — what the result is called. Without a value Orbit falls back to `Post #12`.

Resources that declare nothing stay out of search entirely, so there is no accidental exposure of models you have not thought about.

## Customise a result

Every part of a result row is a classmethod you can override:

```python
class OrderResource(Resource):
    global_search_attributes = ("reference", "customer_email")

    @classmethod
    def get_global_search_result_title(cls, record) -> str:
        return f"Order {record['reference']}"

    @classmethod
    def get_global_search_result_details(cls, record) -> dict:
        return {"Customer": record["customer_email"], "Total": f"${record['total']}"}

    @classmethod
    def get_global_search_result_url(cls, record) -> str:
        return cls.page_url("edit", record)
```

Cap how many rows one resource may contribute with `global_search_result_limit` (default `5`).

## Panel configuration

The box is on by default and appears as soon as one resource is searchable:

```python title="app/orbit/app/panel.py"
panel = (
    Panel.make("app")
    .global_search(True, debounce=250, placeholder="Search posts, authors…", limit=8)
    .resources([PostResource, AuthorResource])
)
```

| Method | Role |
|--------|------|
| `global_search(condition, *, debounce, placeholder, limit)` | Toggle and configure in one call |
| `global_search_debounce(ms)` | Wait this long after typing stops before searching |
| `global_search_placeholder(text)` | Placeholder inside the input |
| `global_search_limit(n)` | Total results shown across all resources |
| `has_global_search()` | True when search is on **and** a resource opted in |

Turn it off for a panel with `.global_search(False)`.

## How a search runs

1. The topbar box waits out the debounce, then fetches `{panel}/global-search?search=…`.
2. The route loads candidate records for every searchable resource — from the database for ORM-backed resources, from `get_records()` otherwise.
3. Resources the signed-in user cannot `view_any` are skipped, so results respect your [permissions](/resources/overview/#permissions).
4. Matches are grouped per resource, trimmed to the panel limit, and returned as ready-to-render HTML.

Because the endpoint returns HTML, nothing needs to be duplicated in JavaScript — the same server-side rendering you get everywhere else in Orbit.

## Searching outside the topbar

The building blocks are importable if you want search on a custom page:

```python
from almasix.orbit.panels.global_search import (
    collect_global_search_results,
    render_global_search_groups,
)

groups = collect_global_search_results(panel, "orbit", user=user)
html = render_global_search_groups(groups)
```

`collect_global_search_results` accepts `records_by_resource={PostResource: rows}` when you have already loaded the data.

## Related pages

- [Resources overview](/resources/overview/) — record titles and permissions
- [Panel configuration](/panels/configuration/) — the rest of the topbar
