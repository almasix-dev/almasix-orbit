---
title: Tables overview
description: Define Orbit tables — columns, search, sort, filters, actions, pagination, and empty states — with a fluent Python API.
---

## Introduction

A **table** is how Orbit lists records in the admin UI: one row per record, columns for fields, and toolbar chrome for search, filters, and actions. You configure the table in Python with a fluent API (`Table.make(...).columns([...]).filters([...])` and so on). Orbit renders HTML; the Conduit list host hydrates interactivity (typing in search, clicking sort headers, changing page, bulk-selecting rows).

You usually attach a table to a [Resource](/resources/listing-records/) so list / create / edit pages stay wired together — the list page is often the first screen operators live in. You can also embed a [standalone table](/components/table/) on a custom page or inside a [table widget](/widgets/tables/). Column types, filters, actions, grouping, summaries, and cell layouts each have dedicated guides (see [Guides](#guides) below).

![Table overview (light)](/examples/light/tables/overview.png)

![Table overview (dark)](/examples/dark/tables/overview.png)

## Defining table columns

The basis of any table is rows and columns. Feed rows with `.records([...])` (dicts or objects) or store a `.query(...)` for your app layer. You define the columns that appear in each row.

Orbit ships many column types — see the [columns catalog](/tables/columns/overview/). Pass them to `.columns([...])`:

```python
from almasix.orbit.tables import Table, TextColumn, IconColumn

table = (
    Table.make("posts")
    .columns([
        TextColumn.make("title"),
        TextColumn.make("slug"),
        IconColumn.make("featured").boolean(),
    ])
)
```

In this example there are three columns: title and slug as text, and a boolean icon for “featured”.

![Columns (light)](/examples/light/tables/overview-columns.png)

![Columns (dark)](/examples/dark/tables/overview-columns.png)

### Making columns sortable and searchable

Chain configurators onto a column. `.searchable()` adds a search field to the table toolbar and matches that column’s values (you can mark several columns searchable — one query searches them all):

```python
from almasix.orbit.tables import TextColumn

TextColumn.make("title").searchable()
```

![Searchable column (light)](/examples/light/tables/overview-searchable.png)

![Searchable column (dark)](/examples/dark/tables/overview-searchable.png)

`.sortable()` adds a sort control on the column header; clicking it sorts the table by that column:

```python
TextColumn.make("title").sortable()
```

![Sortable column (light)](/examples/light/tables/overview-sortable.png)

![Sortable column (dark)](/examples/dark/tables/overview-sortable.png)

Use `.default_sort("title", "desc")` on the table for the initial sort until the user picks another column. For full-text or otherwise custom search, call `.search_using(callback)` or mark the whole table `.searchable()` when no column is searchable yet.

### Accessing related data from columns

Display nested data with **dot notation**. For a post that has an `author` dict (or object) with a `name`, use:

```python
TextColumn.make("author.name")
```

Orbit resolves each segment (`author`, then `name`) on dicts and objects. The same paths work for search and sort when the column is searchable/sortable.

![Relationship column (light)](/examples/light/tables/overview-relationships.png)

![Relationship column (dark)](/examples/dark/tables/overview-relationships.png)

### Adding columns alongside existing ones

`.columns([...])` replaces the full column list. To **append** without wiping prior configuration (handy with global defaults), use `.push_columns([...])`:

```python
from almasix.orbit.tables import Table, TextColumn

Table.configure_using(lambda t: t.push_columns([
    TextColumn.make("created_at")
    .label("Created")
    .sortable()
    .toggleable(is_toggled_hidden_by_default=True),
]))
```

## Defining table filters

Beyond column search, filters let users narrow rows in other ways. Attach them with `.filters([...])`:

```python
from almasix.orbit.tables import SelectFilter, Filter

table.filters([
    Filter.make("featured").query(lambda records, value: [
        r for r in records if r.get("featured")
    ] if value else records),
    SelectFilter.make("status").options({
        "draft": "Draft",
        "review": "Review",
        "published": "Published",
    }),
])
```

A filter icon appears in the toolbar. Opening it shows each filter’s control (checkbox, select, and so on). See [Filters](/tables/filters/overview/) for `TernaryFilter`, `TrashedFilter`, groups, and `.defer_filters()`.

![Filters (light)](/examples/light/tables/filters.png)

![Filters (dark)](/examples/dark/tables/filters.png)

## Defining table actions

Actions are buttons that run a callback (or open a URL / modal). On a table they live in three places:

| Placement | Method | When to use |
|-----------|--------|-------------|
| Per row | `.record_actions([...])` (alias `.actions([...])`) | Edit, view, delete, or custom verbs for one record |
| Header | `.header_actions([...])` | Create and other table-wide shortcuts |
| Bulk toolbar | `.toolbar_actions([...])` (alias `.bulk_actions([...])`) | Operate on every selected row at once |

```python
from almasix.orbit.actions import Action, CreateAction, DeleteBulkAction, EditAction

table = (
    Table.make("posts")
    .columns([TextColumn.make("title")])
    .record_actions([
        Action.make("feature")
        .action(lambda record, **_: record.__setitem__("featured", True))
        .hidden(lambda record, **_: bool(record.get("featured"))),
        EditAction.make(),
    ])
    .toolbar_actions([DeleteBulkAction.make()])
    .header_actions([CreateAction.make()])
)
```

When bulk actions are present, each row gets a checkbox and a selection bar appears once rows are selected. Actions can confirm, open modals, and collect forms — see [table actions](/tables/actions/) and [panel actions](/panels/actions/).

![Row / bulk actions (light)](/examples/light/tables/actions.png)

![Row / bulk actions (dark)](/examples/dark/tables/actions.png)

## Pagination

Tables are paginated by default (per-page options **5 / 10 / 25 / 50**). Users change page size and move between pages from the footer chrome.

![Pagination (light)](/examples/light/tables/overview-pagination.png)

![Pagination (dark)](/examples/dark/tables/overview-pagination.png)

### Customizing pagination options

Pass options to `.paginated([...])`. Include `"all"` to offer a full list (use carefully on large datasets):

```python
table.paginated([10, 25, 50, 100, "all"])
```

### Default page size

```python
table.default_pagination_page_option(25)
```

Make sure that value appears in the options list.

### First / last page links

```python
table.extreme_pagination_links()
```

Adds « / » controls beside the usual previous / next buttons.

### Simple or cursor modes

```python
from almasix.orbit.tables import PaginationMode

table.pagination_mode(PaginationMode.SIMPLE)   # prev / next only
table.pagination_mode(PaginationMode.CURSOR)   # same chrome; cursor semantics for DB hosts
```

### Query string identifier

When several tables share a page, give each a unique id so pagination state does not clash:

```python
table.query_string_identifier("users")
```

### Disabling pagination

```python
table.paginated(False)
```

The footer chrome (result range, per-page select, and page links) is omitted and every record is shown.

![Pagination disabled (light)](/examples/light/tables/overview-pagination-disabled.png)

![Pagination disabled (dark)](/examples/dark/tables/overview-pagination-disabled.png)

Persist the user’s per-page choice with `.persist_records_per_page_in_session()` (or `.persist_in_session()` for search, sort, filters, columns, and per-page together).

## Record URLs (clickable rows)

Make an entire row clickable:

```python
table.record_url(lambda record: f"/posts/{record['id']}")
table.open_record_url_in_new_tab()  # optional
```

On resource tables the list host often supplies a view/edit URL already; `.record_url()` overrides it. Individual columns can still use `.url(...)` for cell links.

## Reordering records

Allow drag-style reordering by storing order in a column (e.g. `sort`):

```python
table.reorderable("sort")
table.paginated_while_reordering()  # keep pagination while reordering (off by default)
table.before_reordering(lambda order: ...)
table.after_reordering(lambda order: ...)
```

A toolbar control toggles reorder mode (`ListRecordsHost.toggleReordering()`). Apply a new order with `table.apply_reorder(ids)`.

![Reorder (light)](/examples/light/tables/overview-reorder.png)

![Reorder (dark)](/examples/dark/tables/overview-reorder.png)

Customize the trigger with `.reorder_records_trigger_action(lambda action, is_reordering: ...)`.

## Customizing the table header

Add a heading and optional description above the toolbar:

```python
table.heading("Clients").description("Manage your clients here.")
```

![Heading (light)](/examples/light/tables/overview-heading.png)

![Heading (dark)](/examples/dark/tables/overview-heading.png)

Replace the whole header block with custom HTML:

```python
table.header("<div class='…'>…</div>")
# or table.header(lambda **ctx: "…")
```

## Polling table content

Refresh the table on an interval (hosts honor `data-poll`):

```python
table.poll("10s")
```

## Deferring loading

For heavy lists, mark the table to load asynchronously:

```python
table.defer_loading()
```

## Searching with a custom callback

When you control search outside column `.searchable()` (e.g. a full-text index), pass a callback:

```python
table.search_using(lambda records, search: [
    r for r in records if search.lower() in str(r.get("title", "")).lower()
])
# Show the search field even with no searchable columns:
table.searchable()
```

## Persisting table state in the session

Remember filters, search, sort, column visibility, and per-page across visits:

```python
table.persist_in_session()       # all on
table.persist_in_session(False)  # all off
# or: persist_filters_in_session / persist_search_in_session /
#     persist_sort_in_session / persist_records_per_page_in_session
```

Flags are emitted as `data-persist-*` attributes for the list host / front-end to store.

## Styling table rows

### Striped rows

```python
table.striped()  # default is already striped; pass False to disable
```

### Custom row classes

```python
table.record_classes(
    lambda record: "or-row-draft" if record.get("status") == "draft" else None
)
```

![Striped / row classes (light)](/examples/light/tables/overview-striped.png)

![Striped / row classes (dark)](/examples/dark/tables/overview-striped.png)

## Empty state

When there are no rows after filters/search:

```python
table.empty_state_heading("No posts yet")
table.empty_state_description("Create your first post to get going.")
table.empty_state_icon("heroicon-o-document-text")
table.empty_state_actions([CreateAction.make()])
# or fully custom markup:
table.empty_state("<div class='…'>…</div>")
```

![Empty state (light)](/examples/light/tables/empty.png)

![Empty state (dark)](/examples/dark/tables/empty.png)

## Global settings

Register defaults for every table (e.g. in a service provider boot hook):

```python
from almasix.orbit.tables import Table, PaginationMode

Table.configure_using(lambda t: (
    t.paginated([10, 25, 50])
    .pagination_mode(PaginationMode.DEFAULT)
    .striped()
))
```

## Feeding records

| Method | Role |
|--------|------|
| `.records([...])` | In-memory list (dicts or objects) |
| `.query(any)` | Store a query object for your app / ORM layer |

`get_records()` / `get_total()` filter, search, sort, then paginate the in-memory list. Push filtering to the database when you use `.query()` with your own loader.

## Guides

| Page | What you’ll find |
|------|------------------|
| [Columns catalog](/tables/columns/overview/) | Every column type |
| [Text / money](/tables/columns/text/) | Search, sort, badge, currency, copyable, markdown |
| [Editable columns](/tables/columns/select/) | Inline select / toggle / text / checkbox |
| [Filters](/tables/filters/overview/) | Select, ternary, groups, deferred apply |
| [Actions](/tables/actions/) | Row, bulk, header, and dropdowns |
| [Layout](/tables/layout/) | Split, Stack, Panel, Grid, View |
| [Summaries](/tables/summaries/) | Sum, Average, Count, Range |
| [Grouping](/tables/grouping/) | `default_group` and collapsible groups |
| [Standalone tables](/components/table/) | Tables outside a Resource |

Live sample: **Tables overview** in `examples/orbit-admin` (`TablesOverviewResource`).
