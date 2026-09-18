---
title: Forms overview
description: Build Filament-familiar forms with Orbit fields, nested schemas, validation, and Conduit-powered interactivity.
---

## Introduction

Orbit forms mirror Filament’s fluent field API on Almasix: compose a `Form` (or any `Schema`), nest layouts, and render HTML that Conduit hosts hydrate. Fields share chrome — labels, hints, helpers, prefixes, suffixes, and validation — and dehydrate into a plain dict for create/edit pages.

Start with a field page such as [Text input](/forms/text-input/) for every variation screenshot, or compose several fields inside [Sections](/schemas/sections/), [Tabs](/schemas/tabs/), and [Wizards](/schemas/wizards/).

```python
from almasix.orbit.forms import Form, TextInput, Select, Toggle
from almasix.orbit.schemas import Section

form = (
    Form.make("post")
    .schema([
        Section.make("basics").heading("Basics").schema([
            TextInput.make("title").required().max_length(200),
            Select.make("status").options({
                "draft": "Draft",
                "published": "Published",
            }),
            Toggle.make("featured").label("Featured"),
        ]),
    ])
)
```

![Orbit Forms overview (light)](/examples/light/forms/overview.png)

![Orbit Forms overview (dark)](/examples/dark/forms/overview.png)

## Field catalog

| Field | Use when |
|-------|----------|
| [Text input](/forms/text-input/) | Single-line strings, email, password, URL, numeric |
| [Textarea](/forms/textarea/) | Multi-line plain text |
| [Select](/forms/select/) / [Multi select](/forms/multi-select/) | Fixed option lists |
| [Checkbox](/forms/checkbox/) / [Toggle](/forms/toggle/) | Booleans |
| [Checkbox list](/forms/checkbox-list/) / [Radio](/forms/radio/) | Enumerated choices |
| [Date](/forms/date-picker/) / [Date-time](/forms/date-time-picker/) / [Time](/forms/time-picker/) | Temporal values |
| [File upload](/forms/file-upload/) | Files and images |
| [Repeater](/forms/repeater/) / [Builder](/forms/builder/) | Nested item lists |
| [Money input](/forms/money-input/) | Currency amounts |
| [Rich editor](/forms/rich-editor/) | HTML body copy |

## Validation & closures

See [Validation](/forms/validation/) for the rule catalog (including `required_if` / `prohibited`), and [Closures](/forms/closures/) for dynamic labels, visibility, and defaults.
