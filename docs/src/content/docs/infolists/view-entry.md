---
title: View entry
description: ViewEntry is the escape hatch for custom HTML inside an Infolist — static markup or callable content with entry chrome.
---

## Introduction

`ViewEntry` is the escape hatch for custom HTML inside an infolist. Supply markup with `.view(...)` or `.content(...)` (aliases). Content is not auto-escaped — sanitize untrusted data yourself. Shared [Entry chrome](/infolists/overview/) (label, helper, hidden label) still wraps the custom markup.

## Basic view entry

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import ViewEntry

ViewEntry.make("summary")
    .label("Summary")
    .content("<strong>3</strong> modules ready")
```

![Orbit View entry basic (light)](/examples/light/infolists/view-entry/basic.png)

![Orbit View entry basic (dark)](/examples/dark/infolists/view-entry/basic.png)

## Callable content

Build markup from `state` / `record` at render time.

```python title="app/orbit/resources/post_resource.py"
ViewEntry.make("title")
    .label("Headline")
    .content(
        lambda state=None, **_: f'<span class="or-badge or-color-success">{state}</span>'
    )
```

![Orbit View entry callable (light)](/examples/light/infolists/view-entry/callable.png)

![Orbit View entry callable (dark)](/examples/dark/infolists/view-entry/callable.png)

## Hidden label

```python title="app/orbit/resources/post_resource.py"
ViewEntry.make("custom").view("<i>static</i>").hidden_label()
```

## API cheat sheet

| Method | Notes |
|--------|-------|
| `.view` / `.content` | HTML string or callable |
| `.hidden_label` | Screen-reader-only label |
| Shared chrome | Helper, hint, tooltip — see [overview](/infolists/overview/) |
