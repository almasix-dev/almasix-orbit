---
title: Code editor
description: CodeEditor is a Textarea with language metadata for client highlighters.
---

## Introduction

CodeEditor is a Textarea with language metadata for client highlighters. Use it for JSON configs, snippets, and template bodies when a full IDE is unnecessary but monospace editing matters.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Code editor

![Orbit Code editor (light)](/examples/light/forms/markdown-editor/basic.png)

![Orbit Code editor (dark)](/examples/dark/forms/markdown-editor/basic.png)

Language-tagged monospace surface.

```python
CodeEditor.make('config').label('Config').language('json')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
