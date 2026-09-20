---
title: Code entry
description: CodeEntry renders monospace blocks for source or JSON, with optional grammar hints and copyable wrappers.
---

## Introduction

`CodeEntry` wraps content in `<pre class="or-code"><code>…</code></pre>` so payloads, snippets, and config blobs stay monospace and scannable on a show page. Dicts and lists are pretty-printed as JSON; strings render as-is (escaped).

Use it when operators need to inspect structured data without leaving the record view. Shared entry chrome (label above the block by default) still applies — see the [overview](/infolists/overview/). Pair with `.grammar(...)` for host highlighters and `.copyable()` when the payload should be one click from the clipboard.

## Basic code entry

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import CodeEntry

CodeEntry.make("payload").label("Payload")
```

![Orbit Code entry basic (light)](/examples/light/infolists/code-entry/basic.png)

![Orbit Code entry basic (dark)](/examples/dark/infolists/code-entry/basic.png)

## Grammar and copyable

`.grammar("python")` sets `data-language` for host highlighters. `.copyable()` adds the shared clipboard control.

```python title="app/orbit/resources/post_resource.py"
CodeEntry.make("source").label("Source").grammar("python").copyable()
```

![Orbit Code entry grammar (light)](/examples/light/infolists/code-entry/grammar.png)

![Orbit Code entry grammar (dark)](/examples/dark/infolists/code-entry/grammar.png)

## API cheat sheet

| Method | Notes |
|--------|-------|
| `.grammar` | `data-language` for syntax highlighters |
| `.copyable` / `.copy_message` / `.copy_message_duration` | Clipboard |
| Shared chrome | Label, helper, hint — see [overview](/infolists/overview/) |
