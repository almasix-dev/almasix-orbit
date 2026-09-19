---
title: Tags column
description: TagsColumn — turn a list (or delimited string) into a cluster of colored badges, with an overflow chip.
---

`TagsColumn` takes an iterable of labels — or a delimited string — and renders each one as a small `or-badge` chip. It's built for categories, skills, and other multi-value fields:

```python
from almasix.orbit.tables import TagsColumn

TagsColumn.make("tags")
```

State can be a `list`/`tuple` of strings, or a delimited string such as `"docs, ui, tables"`.

## Customizing the separator

By default, string state is split on commas. Change the delimiter with `.separator()`:

```python
TagsColumn.make("topics").separator(";")
```

## Customizing the color

All chips in the column share one color, chosen the same way as [`TextColumn.color()`](/tables/columns/text/#customizing-the-color):

```python
TagsColumn.make("tags").color("primary")
```

## Limiting the number of tags shown

`.limit()` caps how many chips render before the rest collapse into a `+N` overflow chip:

```python
TagsColumn.make("tags").limit(3)
```

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, TagsColumn

Table.make("articles").columns([
    TextColumn.make("title").searchable().sortable().weight("bold"),
    TagsColumn.make("tags").color("primary").limit(3),
    TagsColumn.make("topics").separator(";"),  # also accepts "python;html" strings
]).records([
    {
        "id": 1,
        "title": "Orbit tables",
        "tags": ["docs", "ui", "tables", "polish"],
        "topics": "python;html",
    },
    {"id": 2, "title": "Conduit hosts", "tags": ["live"], "topics": "conduit"},
])
```

Empty lists render an empty cell. Pair this column with a [`TagsInput`](/forms/tags-input/) on the form so create and edit stay in sync with the list.

## Key methods

| Method | Effect |
|--------|--------|
| `.separator(char)` | Delimiter used to split string state (defaults to `,`) |
| `.color(str \| callable)` | Chip color |
| `.limit(count)` | Max chips shown before a `+N` overflow chip |
| `.format_state_using(callback)` | Normalize dicts / objects → strings before splitting |
| `.label(...)` / `.align_start()` / `.toggleable(...)` / `.sortable()` | Inherited [shared helpers](/tables/columns/overview/) — sorting compares the raw state |

## Preview

![Tags column (light)](/examples/light/tables/tags-column.png)
![Tags column (dark)](/examples/dark/tables/tags-column.png)

![Tags / view (light)](/examples/light/tables/tags-view.png)
![Tags / view (dark)](/examples/dark/tables/tags-view.png)
