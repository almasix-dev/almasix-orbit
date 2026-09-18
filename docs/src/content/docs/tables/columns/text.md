---
title: Text column
description: TextColumn — search, sort, badge, money, dates, copyable, markdown, icons, URLs, and alignment.
---

`TextColumn` is the default table column. Use it for plain text, or enable money, badge, date, markdown, and related helpers as needed.

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn

table = (
    Table.make("orders")
    .columns([
        TextColumn.make("title").searchable().sortable().weight("bold"),
        TextColumn.make("status").badge().color("primary"),
        TextColumn.make("amount").money("USD").align_end().sortable(),
        TextColumn.make("cents").money("USD", divide_by=100).align_end(),
        TextColumn.make("sku").copyable().limit(12),
    ])
    .records(records)
)
```

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn

class OrderResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("title")
                .searchable()
                .sortable()
                .description(lambda record=None, **_: record.get("subtitle", "")),
            TextColumn.make("amount").money("USD").align_end().sortable(),
            TextColumn.make("published_at").date("%b %d, %Y").sortable(),
            TextColumn.make("notes").markdown().wrap().toggleable(
                is_toggled_hidden_by_default=True,
            ),
        ])
```

## Money

Store major units or cents — Orbit formats either:

```python
TextColumn.make("amount").money("USD")
TextColumn.make("cents").money("USD", divide_by=100).align_end()
```

`divide_by=100` turns `1999` into `USD 19.99`. Use `.align_end()` to right-align numeric values.

![Money (light)](/examples/light/tables/money.png)
![Money (dark)](/examples/dark/tables/money.png)

## Text features

![Text features (light)](/examples/light/tables/text-features.png)
![Text features (dark)](/examples/dark/tables/text-features.png)

### Search, sort, toggle

```python
TextColumn.make("title").searchable().sortable()
TextColumn.make("internal_notes").toggleable(is_toggled_hidden_by_default=True)
```

### Badge & color

```python
TextColumn.make("status").badge().color("success")
TextColumn.make("priority").badge().color(
    lambda state=None, **_: "danger" if state == "urgent" else "gray"
)
```

### Dates & numeric

```python
TextColumn.make("published_at").date("%Y-%m-%d")
TextColumn.make("updated_at").date_time("%Y-%m-%d %H:%M")
TextColumn.make("score").numeric(decimal_places=1).align_end()
```

### Description, copyable, weight, wrap

```python
TextColumn.make("email")
    .description("Primary contact")
    .copyable()
    .weight("medium")

TextColumn.make("bio").wrap().limit(80)
```

### Markdown, icon, URL, alignment

```python
TextColumn.make("blurb").markdown()  # **bold**, *italic*, newlines
TextColumn.make("name").icon("heroicon-o-user")
TextColumn.make("title").url(lambda record=None, **_: f"/posts/{record['id']}")
TextColumn.make("amount").money("USD").align_end()
TextColumn.make("status").align_center()
```

### Lists

```python
(
    TextColumn.make("tags")
    .list_with_line_breaks()
)  # • one per line
```

## Key methods

| Method | Effect |
|--------|--------|
| `.searchable()` / `.sortable()` / `.toggleable(...)` | Toolbar & column picker |
| `.money(currency, *, divide_by=1)` | Currency display |
| `.date(...)` / `.date_time(...)` / `.numeric(...)` | Typed formatting |
| `.badge()` / `.boolean()` / `.color(...)` | Visual treatment |
| `.limit(n)` / `.wrap()` / `.weight(...)` | Truncation & typography |
| `.description(...)` / `.copyable()` | Subtext & clipboard |
| `.markdown()` / `.html()` / `.icon(...)` | Rich content |
| `.url(...)` / `.align_end()` etc. | Links & alignment |
| `.format_state_using(fn)` / `.summarize(...)` | Custom transform / footer |

## Preview

![Text & money (light)](/examples/light/tables/money.png)
![Text & money (dark)](/examples/dark/tables/money.png)

![Text features (light)](/examples/light/tables/text-features.png)
![Text features (dark)](/examples/dark/tables/text-features.png)
