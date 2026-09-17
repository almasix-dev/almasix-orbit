---
title: Infolists
description: Read-only record views with typed entries — and a form fallback when you skip infolist().
---

**Infolists** are the “show” side of a resource — a definition list of entries over a record.

```python
from almasix.orbit.infolists import (
    Infolist, TextEntry, ImageEntry, CodeEntry, KeyValueEntry, RepeatableEntry,
)

infolist = Infolist.make("post").schema([
    TextEntry.make("title").badge().color("success"),
    TextEntry.make("slug").copyable(),
    TextEntry.make("body").prose().markdown(),
    ImageEntry.make("cover"),
    CodeEntry.make("payload"),
    KeyValueEntry.make("meta"),
    RepeatableEntry.make("tags").schema([
        TextEntry.make("name"),
    ]),
])

html = infolist.render(post)
```

Markup is a `<dl class="or-infolist">` — semantic, styleable, no surprise div soup.

## Entry API

```python
TextEntry.make("email")
    .label("Email")
    .format_state_using(lambda v: v.lower())
    .url("mailto:{state}")
    .copyable()
    .badge()
    .color("info")
    .icon("heroicon-o-envelope")
    .date_time()
    .markdown()
    .prose()
```

| Entry | Role |
|-------|------|
| `TextEntry` | Default |
| `IconEntry` | Icon-forward |
| `ImageEntry` | Image |
| `ColorEntry` | Color swatch |
| `CodeEntry` | Monospace / code block |
| `KeyValueEntry` | Dict-ish display |
| `RepeatableEntry` | Nested entry schema |

## On a resource

```python
@classmethod
def infolist(cls, infolist: Infolist) -> Infolist:
    return infolist.schema([
        TextEntry.make("title"),
        TextEntry.make("status").badge(),
    ])
```

Then `PostResource.get_infolist().render(record)` on your view page.

## Empty infolist → readonly form fallback

Leave `infolist()` empty (or return the untouched builder) and Orbit still gives you a show page. `get_infolist()` notices there are no components and **projects the form schema** into read-only `TextEntry`s:

```python
@classmethod
def form(cls, form: Form) -> Form:
    return form.schema([
        TextInput.make("title").required(),
        TextInput.make("slug").required(),
        Textarea.make("body"),
    ])

@classmethod
def infolist(cls, infolist: Infolist) -> Infolist:
    return infolist  # empty on purpose
```

Under the hood:

1. `get_form().readonly()` — same fields, edit chrome dialed down.
2. Walk nested layouts / repeaters for every `Field`.
3. Emit `TextEntry.make(name).label(field.get_label())` for each.

So create/edit and view stay in sync until you’re ready to hand-craft badges, prose, and copyable slugs. Define an explicit `.schema([...])` whenever the show page should look different from the form — the fallback politely steps aside.
