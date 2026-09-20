---
title: Listing records
description: The index page of a resource — the table, its tabs, and the search, sort, filter, and pagination state behind it.
---

The list page is the front door of a [resource](/resources/overview/). It renders the resource's [table](/tables/overview/) with a page heading, header actions, and — when you add them — filter tabs across the top. Orbit mounts it at the resource root, for example `/admin/posts`.

You get a working list page for free: register a resource on a panel and the index route exists. Everything below is about shaping it.

## The table is the page

The list page renders whatever `Resource.table()` returns, so columns, filters, summaries, grouping, and row actions are all configured there:

```python title="app/orbit/resources/post_resource.py"
class PostResource(Resource):
    model = Post

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns([
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status").badge().sortable(),
            ])
            .filters([SelectFilter.make("status").options({"draft": "Draft", "published": "Published"})])
            .default_sort("created_at", "desc")
        )
```

If you define no row actions, Orbit adds View (plus Edit and Delete when records are mutable), a Create header action, and a bulk delete group. Define your own and yours win.

## Tabs

Tabs are saved filters shown as a row of buttons above the table. Define them on the resource:

```python
from almasix.orbit.panels.pages import Tab


class PostResource(Resource):
    @classmethod
    def get_tabs(cls) -> list[Tab]:
        return [
            Tab("all").label("All").badge(lambda records=None, **_: len(records or [])),
            Tab("published")
            .label("Published")
            .badge_color("success")
            .modify_query_using(lambda rows: [r for r in rows if r["status"] == "published"]),
            Tab("draft")
            .label("Draft")
            .modify_query_using(lambda rows: [r for r in rows if r["status"] == "draft"]),
        ]
```

| Tab method | Role |
|------------|------|
| `label(text)` | Button text |
| `icon(name)` | Heroicon before the label |
| `badge(value)` | Static value, or a callable receiving the current `records` |
| `badge_color(color)` | Badge color token |
| `modify_query_using(fn)` | Filter the rows this tab shows |

The first tab is active on load. Clicking one resets pagination and clears the current selection.

## Live state

The list page keeps its state on the page host, so every interaction is a server round trip without a page reload:

| State | Set by |
|-------|--------|
| `table_search` | The search box |
| `table_sort` / `table_sort_direction` | Clicking a sortable column header |
| `table_filters` | Filter form, chips, and reset |
| `page` / `per_page` | Pagination footer |
| `selected` / `select_all` | Row checkboxes, used by bulk actions |
| `toggled_columns` / `column_order` | The column manager |
| `active_tab` | The tab bar |

Filters can be deferred behind an Apply button and persisted per session — see [filters](/tables/filters/overview/).

## A custom list page

Point the resource at your own `ListRecords` subclass when you want to override rendering or compute tabs from a query:

```python
from almasix.orbit.panels.pages import ListRecords, Tab


class PostList(ListRecords):
    resource = PostResource

    @classmethod
    def get_tabs(cls) -> list[Tab]:
        return [Tab("all").label("Everything")]


class PostResource(Resource):
    list_page = PostList
```

## Related pages

- [Tables overview](/tables/overview/) — columns, filters, actions, summaries
- [Creating records](/resources/creating-records/) — where the Create action leads
- [Resource page hosts](/resources/pages/) — the page classes themselves
