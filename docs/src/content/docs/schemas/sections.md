---
title: Sections
description: Section groups related fields under a heading — description, icon, aside, compact, secondary, and collapsible body with optional persist.
---

## Introduction

`Section` is the primary titled panel for forms and infolists. Put related fields under a heading, optionally add a description and icon, then nest any schema children — grids, flex rows, fields, or primes.

```python title="app/orbit/schemas/profile_section.py"
from almasix.orbit.schemas import Section
from almasix.orbit.forms import TextInput

Section.make("profile")
    .heading("Profile")
    .description("Public details for this account.")
    .icon("heroicon-o-user")
    .schema([
        TextInput.make("name").label("Name"),
        TextInput.make("bio").label("Bio"),
    ])
```

![Section (light)](/examples/light/schemas/section.png)
![Section (dark)](/examples/dark/schemas/section.png)

## Basic section

Heading plus nested schema:

```python title="app/orbit/schemas/basic_section.py"
Section.make("profile")
    .heading("Profile")
    .schema([TextInput.make("name").label("Name")])
```

![Basic section (light)](/examples/light/schemas/section/basic.png)
![Basic section (dark)](/examples/dark/schemas/section/basic.png)

If you omit `.heading(...)`, the section falls back to `.label(...)` / the component name for the title.

## Description and icon

```python title="app/orbit/schemas/section_chrome.py"
Section.make("billing")
    .heading("Billing")
    .description("Invoices are emailed on the 1st of each month.")
    .icon("heroicon-o-credit-card")
    .schema([...])
```

## Collapsible section

Make the body toggle open/closed. Pair `.collapsed()` when advanced blocks should start shut:

```python title="app/orbit/schemas/collapsible_section.py"
Section.make("advanced")
    .heading("Advanced")
    .collapsible()
    .collapsed()
    .schema([Toggle.make("debug")])
```

![Collapsible section (light)](/examples/light/schemas/section/collapsible.png)
![Collapsible section (dark)](/examples/dark/schemas/section/collapsible.png)

### Persist collapsed state

Remember open/closed across visits via `data-persist-collapsed` (keyed by the section name):

```python title="app/orbit/schemas/persist_section.py"
Section.make("advanced")
    .heading("Advanced")
    .collapsible()
    .persist_collapsed()
    .schema([...])
```

## Compact section

Tighten vertical rhythm for dense admin forms:

```python title="app/orbit/schemas/compact_section.py"
Section.make("profile")
    .heading("Profile")
    .compact()
    .icon("heroicon-o-user")
    .schema([...])
```

![Compact section (light)](/examples/light/schemas/section/compact.png)
![Compact section (dark)](/examples/dark/schemas/section/compact.png)

## Aside and secondary

`.aside()` shifts chrome toward a sidebar-style layout. `.secondary()` uses muted / secondary styling:

```python title="app/orbit/schemas/aside_section.py"
Section.make("meta")
    .heading("Metadata")
    .aside()
    .secondary()
    .schema([TextInput.make("slug")])
```

## API reference

| Method | Role |
|--------|------|
| `.heading` | Section title |
| `.description` | Muted copy under the title |
| `.icon` | Heroicon (or registered icon) beside the title |
| `.collapsible` | Enable open/close toggle |
| `.collapsed` | Start collapsed (usually with `.collapsible`) |
| `.persist_collapsed` | Persist open/closed in the host |
| `.compact` | Denser spacing |
| `.aside` | Aside / sidebar chrome |
| `.secondary` | Muted secondary chrome |
| `.schema` | Nested child components |

Shared layout helpers also apply: `.dense`, `.gap`, `.defer_loading` — see [Layouts](/schemas/layouts/).
