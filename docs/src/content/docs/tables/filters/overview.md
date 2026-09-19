---
title: Table filters
description: Select, ternary, checkbox/toggle, trashed, and grouped filters for Orbit tables — Filament-style chrome, indicators, and session persist.
---

Filters narrow which rows appear in a table. Put them on `Table.filters([...])`; the index host keeps `table_filters` and applies them when rendering.

```python
from almasix.orbit.tables import (
    Table, TextColumn, Filter, SelectFilter, TernaryFilter, FilterGroup,
)

table = (
    Table.make("posts")
    .columns([TextColumn.make("title").searchable()])
    .filters([
        SelectFilter.make("status")
            .label("Status")
            .options({
                "draft": "Draft",
                "published": "Published",
            }),
        # Filter name ≠ column: point at the attribute
        SelectFilter.make("author")
            .attribute("author_id")
            .options(lambda **ctx: ctx.get("authors", {})),
        TernaryFilter.make("featured").label("Featured"),
        Filter.make("mine")
            .label("Mine only")
            .query(lambda q, value: [r for r in q if r.get("mine")]),
    ])
)
```

![Filters (light)](/examples/light/tables/filters.png)
![Filters (dark)](/examples/dark/tables/filters.png)

Live selects call `setTableFilter(name, value)` on the host (Conduit only supports top-level props, so nested `table_filters.*` model paths are not used). Orbit defaults to **live** filters; call `.defer_filters()` when you want an Apply button instead (Filament defaults the other way).

## Available filters

| Class | Chrome | Role |
|-------|--------|------|
| `Filter` | Checkbox (or `.toggle()`) | Custom `.query(callback)` when the control is on |
| `SelectFilter` | `<select>` | Equality on `attribute` / name; optional `.multiple()` |
| `TernaryFilter` | Tri-state select | All / Yes / No for booleans |
| `TrashedFilter` | Tri-state select | Soft-delete scopes |
| `FilterGroup` | Fieldset section | Nest filters under a labeled group |
| `QueryBuilderFilter` | Builder UI | See [Query builder](/query-builder/overview/) |

`.apply()` is a no-op when the value is inactive (`None`, `""`, `[]`, or off for boolean filters), unless a custom `.query()` / ternary `queries()` handles empty on purpose.

## Checkbox and toggle filters

A plain `Filter` without `.options()` renders a checkbox. When checked, `.query()` scopes the rows — same idea as Filament’s default filter:

```python
from almasix.orbit.tables import Filter

Filter.make("featured")
    .label("Featured")
    .query(lambda q, value: [r for r in q if r.get("featured")])
```

Swap the checkbox for a switch with `.toggle()`:

```python
Filter.make("featured").label("Featured").toggle().query(...)
```

## Select filters

```python
from almasix.orbit.tables import SelectFilter

SelectFilter.make("status")
    .options({"draft": "Draft", "published": "Published"})

SelectFilter.make("status")
    .multiple()
    .selectable_placeholder(False)
    .options({"draft": "Draft", "published": "Published"})
```

`.multiple()` keeps a list of selected keys and matches with `in`. `.selectable_placeholder(False)` drops the blank “All” option.

## Ternary and trashed

```python
from almasix.orbit.tables import TernaryFilter, TrashedFilter

TernaryFilter.make("featured")
    .true_label("Featured")
    .false_label("Not featured")
    .placeholder("Any")
    .nullable()  # treat null attribute as “false”

TernaryFilter.make("featured").queries(
    true=lambda q, value: [...],
    false=lambda q, value: [...],
    blank=lambda q, value: q,
)

table.filters([TrashedFilter.make()])
```

![Ternary + trashed (light)](/examples/light/tables/filters-ternary.png)
![Ternary + trashed (dark)](/examples/dark/tables/filters-ternary.png)

## Filter groups

```python
from almasix.orbit.tables import FilterGroup, SelectFilter, Filter

FilterGroup.make("visibility").label("Visibility").filters([
    SelectFilter.make("status").options({
        "draft": "Draft",
        "published": "Published",
    }),
    Filter.make("featured").label("Featured").toggle().query(...),
])
```

Groups render as a fieldset in the panel and flatten for apply / indicators.

## Labels, defaults, and indicators

```python
SelectFilter.make("status")
    .label("Status")
    .default("published")
    .indicate_using(lambda state, **_: f"is {state}" if state else None)

Filter.make("featured").indicate(False)  # no chip

table.hidden_filter_indicators()  # hide the whole chip bar
```

Defaults seed `table_filters` on first mount and again after **Reset filters**.

## Persist and defer

```python
table.persist_filters_in_session()           # sessionStorage round-trip
table.persist_filters_in_session(key="posts")
table.defer_filters()                        # Apply filters button
table.deselect_all_records_when_filtered(False)
```

![Deferred filters (light)](/examples/light/tables/filters-deferred.png)
![Deferred filters (dark)](/examples/dark/tables/filters-deferred.png)

## Index chrome

List pages render a funnel **Filters** trigger with a badge count, a dropdown panel, and indicator chips for active values. Search sits on the **right** of the same toolbar row.

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn, Filter, FilterGroup, SelectFilter

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns([
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status").badge(),
            ])
            .filters([
                FilterGroup.make("visibility").label("Visibility").filters([
                    SelectFilter.make("status").options({
                        "draft": "Draft",
                        "review": "Review",
                        "published": "Published",
                    }),
                    Filter.make("has_body")
                        .label("Has body")
                        .toggle()
                        .query(lambda q, value: [
                            r for r in q
                            if (r.get("body") if isinstance(r, dict) else getattr(r, "body", None))
                        ]),
                ]),
            ])
            .defer_filters()
            .persist_filters_in_session()
        )
```

## Empty after filtering

When filters match no rows, the empty state still renders. Customize the copy on the table:

```python
table.empty_state_heading("No matches")
table.empty_state_description("Try clearing filters or broadening search.")
```

![Empty after filters (light)](/examples/light/tables/empty.png)
![Empty after filters (dark)](/examples/dark/tables/empty.png)

See also [Tables overview](/tables/overview/), [Query builder](/query-builder/overview/), and [standalone tables](/components/table/).
