---
title: Modal table select
description: ModalTableSelect opens a browse modal backed by an Orbit table so users can search and pick records without leaving the form.
---

## Introduction

ModalTableSelect opens a browse modal backed by an Orbit table so users can search and pick records without leaving the form. The field shows a readonly summary input plus a Browse action that mounts mountTableSelect on the Conduit host.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Modal table select

![Orbit Modal table select (light)](/examples/light/forms/select/basic.png)

![Orbit Modal table select (dark)](/examples/dark/forms/select/basic.png)

Readonly value plus Browse button.

```python
ModalTableSelect.make('author_id')
    .label('Author')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
