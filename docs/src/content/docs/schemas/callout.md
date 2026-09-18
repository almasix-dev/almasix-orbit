---
title: Callout
description: Callout surfaces info, success, warning, or danger messages inside a form — tips before save, destructive confirmations, or success banners.
---

## Introduction

Callout surfaces info, success, warning, or danger messages inside a form — tips before save, destructive confirmations, or success banners.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Info callout

![Orbit Info callout (light)](/examples/light/schemas/callout/info.png)

![Orbit Info callout (dark)](/examples/dark/schemas/callout/info.png)

Neutral guidance.

```python
Callout.make()
    .info()
    .label('Tip')
    .description('Fill these fields before saving.')
```

## Danger callout

![Orbit Danger callout (light)](/examples/light/schemas/callout/danger.png)

![Orbit Danger callout (dark)](/examples/dark/schemas/callout/danger.png)

Destructive action warning.

```python
Callout.make()
    .danger()
    .label('Danger')
    .description('This action cannot be undone.')
```

## Success callout

![Orbit Success callout (light)](/examples/light/schemas/callout/success.png)

![Orbit Success callout (dark)](/examples/dark/schemas/callout/success.png)

Confirmation feedback.

```python
Callout.make()
    .success()
    .label('Saved')
    .description('Your changes were published.')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
