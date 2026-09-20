---
title: Code entry
description: CodeEntry renders monospace blocks for source or JSON, with optional grammar hints and copyable wrappers.
---

## Introduction

`CodeEntry` wraps content in `<pre class="or-code"><code>…</code></pre>`. Dicts and lists are pretty-printed as JSON. Strings render as-is (escaped).

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
