---
title: Code editor
description: CodeEditor is a Textarea with code-editor chrome and an optional data-language attribute — not Monaco/CodeMirror yet.
---

## Introduction

**Honest scope:** `CodeEditor` subclasses `Textarea`, swaps classes to `or-field-CodeEditor` / `or-textarea or-editor or-editor-code`, and optionally sets `data-language`. There is no Monaco or CodeMirror bundle in the forms package today. Use `.language()` so hosts or future assets can attach a real editor; until then users edit plain text in a monospace-styled textarea.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic code editor

Multiline code field with editor chrome classes. Rows default like Textarea.

```python title="app/orbit/resources/example_resource.py"
CodeEditor.make('script')
    .label('Script')
    .rows(12)
    .helper_text('Plain text until a host editor attaches.')
```

![Orbit Basic code editor (light)](/examples/light/forms/code-editor/basic.png)

![Orbit Basic code editor (dark)](/examples/dark/forms/code-editor/basic.png)

## Language attribute

`.language('python')` adds `data-language="python"` for syntax highlighters or Monaco bootstrapping in panel assets.

```python title="app/orbit/resources/example_resource.py"
CodeEditor.make('policy')
    .label('Policy (Rego)')
    .language('rego')
    .rows(16)
```

![Orbit Language attribute (light)](/examples/light/forms/code-editor/language.png)

![Orbit Language attribute (dark)](/examples/dark/forms/code-editor/language.png)

## Autosize code

Inherited `.autosize()` works the same as Textarea for growing with content when no external editor is mounted.

```python title="app/orbit/resources/example_resource.py"
CodeEditor.make('snippet')
    .label('Snippet')
    .language('javascript')
    .autosize()
    .rows(6)
```

![Orbit Autosize code (light)](/examples/light/forms/code-editor/autosize.png)

![Orbit Autosize code (dark)](/examples/dark/forms/code-editor/autosize.png)

## Required code

Validate presence and size with Field helpers while the control remains a textarea under the hood.

```python title="app/orbit/resources/example_resource.py"
CodeEditor.make('dockerfile')
    .label('Dockerfile')
    .language('dockerfile')
    .required()
    .min_length(10)
```

![Orbit Required code (light)](/examples/light/forms/code-editor/required.png)

![Orbit Required code (dark)](/examples/dark/forms/code-editor/required.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
