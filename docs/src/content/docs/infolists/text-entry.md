---
title: Text entry
description: TextEntry is the default Infolist entry — badges, icons, URLs, dates, money, markdown, lists, and typography helpers.
---

## Introduction

`TextEntry` is the workhorse for read-only strings and formatted values. It inherits the shared [Entry chrome](/infolists/overview/) (label, helper, hint, placeholder, copyable, slots) and adds Filament-parity formatters for badges, icons, links, dates, money, numeric display, markdown / HTML / prose, and list layouts.

Each variation below includes a short explanation, the fluent API to paste into your schema, and light/dark screenshots.

## Basic text entry

Resolve state from the record by name and render it as text.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("title").label("Title")
```

![Orbit Text entry basic (light)](/examples/light/infolists/text-entry/basic.png)

![Orbit Text entry basic (dark)](/examples/dark/infolists/text-entry/basic.png)

## Badges

`.badge()` wraps the value in an `or-badge`. Pair with `.color(...)` (`success`, `danger`, `warning`, `info`, `primary`, `gray`, or a callable).

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("status").label("Status").badge().color("success")
```

![Orbit Text entry badge (light)](/examples/light/infolists/text-entry/badge.png)

![Orbit Text entry badge (dark)](/examples/dark/infolists/text-entry/badge.png)

## Color without a badge

`.color(...)` also tints plain text via `or-color-*` classes.

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("status").label("Status").color("info").weight("medium")
```

![Orbit Text entry color (light)](/examples/light/infolists/text-entry/color.png)

![Orbit Text entry color (dark)](/examples/dark/infolists/text-entry/color.png)

## Icons

`.icon(...)` places a Heroicon before (default) or after the text. `.icon_position("after")` and `.icon_color(...)` control placement and tint.

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("email")
    .label("Email")
    .icon("heroicon-o-envelope")
    .icon_color("primary")
```

![Orbit Text entry icon (light)](/examples/light/infolists/text-entry/icon.png)

![Orbit Text entry icon (dark)](/examples/dark/infolists/text-entry/icon.png)

## URLs

`.url(...)` wraps the value in a link. Pass a string or callable (`state`, `record`, …). `.open_url_in_new_tab()` adds `target="_blank"`.

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("website")
    .label("Website")
    .url(lambda state, **_: str(state))
    .open_url_in_new_tab()
    .color("primary")
```

![Orbit Text entry url (light)](/examples/light/infolists/text-entry/url.png)

![Orbit Text entry url (dark)](/examples/dark/infolists/text-entry/url.png)

## Size, weight, and font family

`.size("sm" | "md" | "lg" | …)`, `.weight("bold" | "medium" | …)`, and `.font_family("monospace")` map to Orbit typography utilities.

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("title").label("Title").size("lg").weight("bold")
TextEntry.make("slug").label("Slug").font_family("monospace")
```

![Orbit Text entry size + weight (light)](/examples/light/infolists/text-entry/size-weight.png)

![Orbit Text entry size + weight (dark)](/examples/dark/infolists/text-entry/size-weight.png)

![Orbit Text entry font family (light)](/examples/light/infolists/text-entry/font-family.png)

![Orbit Text entry font family (dark)](/examples/dark/infolists/text-entry/font-family.png)

## Line clamp and wrap

`.line_clamp(n)` truncates to *n* lines with CSS line-clamp. `.wrap()` allows soft wrapping on long unbroken strings.

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("bio").label("Bio").line_clamp(2).wrap()
```

![Orbit Text entry line clamp (light)](/examples/light/infolists/text-entry/line-clamp.png)

![Orbit Text entry line clamp (dark)](/examples/dark/infolists/text-entry/line-clamp.png)

## Lists — line breaks, bullets, separators

When state is a list (or you split a string with `.separator(...)`):

| Method | Behavior |
|--------|----------|
| `.list_with_line_breaks()` | One item per line |
| `.bulleted()` | Alias — prefix each item with `•` |
| `.separator(",")` | Join with the given separator; with `.badge()` renders a badge list |

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("tags").label("Tags").list_with_line_breaks()
TextEntry.make("tags").label("Tags").bulleted()
TextEntry.make("skills").label("Skills").separator(",").badge().color("gray")
```

![Orbit Text entry list (light)](/examples/light/infolists/text-entry/list.png)

![Orbit Text entry list (dark)](/examples/dark/infolists/text-entry/list.png)

![Orbit Text entry bulleted (light)](/examples/light/infolists/text-entry/bulleted.png)

![Orbit Text entry bulleted (dark)](/examples/dark/infolists/text-entry/bulleted.png)

![Orbit Text entry separator (light)](/examples/light/infolists/text-entry/separator.png)

![Orbit Text entry separator (dark)](/examples/dark/infolists/text-entry/separator.png)

## Dates and relative time

`.date(...)`, `.date_time(...)`, and `.time(...)` accept `strftime` formats. `.since()` renders human-relative time (`5 minutes ago`, `in 2 days`).

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("published_at").label("Published").date_time("%b %d, %Y %H:%M")
TextEntry.make("starts_at").label("Started").since()
```

![Orbit Text entry date (light)](/examples/light/infolists/text-entry/date.png)

![Orbit Text entry date (dark)](/examples/dark/infolists/text-entry/date.png)

![Orbit Text entry since (light)](/examples/light/infolists/text-entry/since.png)

![Orbit Text entry since (dark)](/examples/dark/infolists/text-entry/since.png)

## Money and numeric

`.money("USD", divide_by=100)` formats currency (optional `decimal_places`). `.numeric(2)` forces decimal places.

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("price").label("Price").money("USD", divide_by=100)
TextEntry.make("qty").label("Quantity").numeric(2)
```

![Orbit Text entry money (light)](/examples/light/infolists/text-entry/money.png)

![Orbit Text entry money (dark)](/examples/dark/infolists/text-entry/money.png)

![Orbit Text entry numeric (light)](/examples/light/infolists/text-entry/numeric.png)

![Orbit Text entry numeric (dark)](/examples/dark/infolists/text-entry/numeric.png)

## Markdown, HTML, and prose

`.markdown()` renders a small safe subset (`**bold**`, `*italic*`, newlines). `.html()` inserts raw HTML (sanitize untrusted input yourself). `.prose()` adds reading-width typography classes — often paired with markdown.

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("md").label("Summary").markdown()
TextEntry.make("html").label("HTML").html()
TextEntry.make("body").label("Body").prose().markdown()
```

![Orbit Text entry markdown (light)](/examples/light/infolists/text-entry/markdown.png)

![Orbit Text entry markdown (dark)](/examples/dark/infolists/text-entry/markdown.png)

![Orbit Text entry html (light)](/examples/light/infolists/text-entry/html.png)

![Orbit Text entry html (dark)](/examples/dark/infolists/text-entry/html.png)

![Orbit Text entry prose (light)](/examples/light/infolists/text-entry/prose.png)

![Orbit Text entry prose (dark)](/examples/dark/infolists/text-entry/prose.png)

## Limiting length

`.limit(n)` truncates characters; `.words(n)` truncates by word count. Both accept a custom `end` suffix (default `…`).

```python title="app/orbit/resources/post_resource.py"
TextEntry.make("bio").label("Bio").limit(48)
TextEntry.make("body").label("Body").words(8)
```

![Orbit Text entry limit (light)](/examples/light/infolists/text-entry/limit.png)

![Orbit Text entry limit (dark)](/examples/dark/infolists/text-entry/limit.png)

## API cheat sheet

| Method | Notes |
|--------|-------|
| `.badge` | Badge wrapper; callable condition supported |
| `.color` / `.icon` / `.icon_position` / `.icon_color` | Visual chrome |
| `.url` / `.open_url_in_new_tab` | Link the value |
| `.size` / `.weight` / `.font_family` / `.wrap` / `.line_clamp` | Typography |
| `.list_with_line_breaks` / `.bulleted` / `.separator` | List layouts |
| `.date` / `.date_time` / `.time` / `.since` | Temporal formatters |
| `.money` / `.numeric` | Currency / number display |
| `.markdown` / `.html` / `.prose` | Rich text modes |
| `.limit` / `.words` | Truncation |

Shared chrome (copyable, placeholder, slots, …) is documented on the [overview](/infolists/overview/).
