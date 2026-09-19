---
title: Split
description: Place schema columns side by side above a breakpoint — notes beside uploads, preview beside editor.
---

## Introduction

`Split` renders children as side-by-side panes that stack below a breakpoint. Ideal for notes beside uploads, a preview beside an editor, or any two (or more) schema columns that should share a row on large screens. Each child is wrapped in `or-schema-split-item`.

```python title="app/orbit/schemas/split_basic.py"
from almasix.orbit.schemas import Split
from almasix.orbit.forms import Textarea, FileUpload

Split.make()
    .from_breakpoint("md")
    .schema([
        Textarea.make("notes"),
        FileUpload.make("attachment"),
    ])
```

![Basic split (light)](/examples/light/schemas/split/basic.png)
![Basic split (dark)](/examples/dark/schemas/split/basic.png)

## Breakpoint helpers

`.from_breakpoint("md")` and `.from_("md")` are equivalent — use whichever reads better in your chain. The modifier class is `or-schema-split-from-{breakpoint}`:

```python title="app/orbit/schemas/split_from.py"
Split.make().from_("lg").schema([...])
Split.make().from_breakpoint("sm").schema([...])
```

Without a breakpoint, the split stays in its default side-by-side class set (no `or-schema-split-from-*` modifier).

## Split vs Flex vs Group

| Component | Best for |
|-----------|----------|
| **Split** | Distinct panes (editor \| preview) that stack |
| **Flex** | Field rows that grow and share one flex line |
| **Group** | Fusing related fields with optional columns, no panes |

```python title="app/orbit/schemas/split_fieldsets.py"
from almasix.orbit.schemas import Split, Fieldset
from almasix.orbit.forms import TextInput

Split.make().from_("lg").schema([
    Fieldset.make().label("Contact").schema([TextInput.make("email")]),
    Fieldset.make().label("Notes").schema([TextInput.make("notes")]),
])
```

![Group + split (light)](/examples/light/schemas/group-split.png)
![Group + split (dark)](/examples/dark/schemas/group-split.png)

## Dense and gap

```python title="app/orbit/schemas/split_gap.py"
Split.make().dense().gap("sm").from_breakpoint("md").schema([...])
```

## API reference

| Method | Role |
|--------|------|
| `.from_breakpoint` / `.from_` | Stack below this breakpoint |
| `.schema` | Child panes |
| `.dense` / `.gap` / `.defer_loading` | Shared layout helpers |

See [Layouts](/schemas/layouts/) for full composition examples.
