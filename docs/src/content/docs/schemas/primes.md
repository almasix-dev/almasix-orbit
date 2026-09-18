---
title: Primes
description: Primes are read-only display components — text badges, icons, images, and lists — for infolists and inline form summaries without editable state.
---

## Introduction

Primes are read-only display components — text badges, icons, images, and lists — for infolists and inline form summaries without editable state.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Text prime

Badge-styled status text.

```python
Text.make()
    .content('Published')
    .badge()
    .color('success')
```

![Orbit Text prime (light)](/examples/light/schemas/primes/text.png)

![Orbit Text prime (dark)](/examples/dark/schemas/primes/text.png)

## Icon prime

Heroicon with color and size.

```python
Icon.make()
    .icon('heroicon-o-check')
    .color('success')
    .size('lg')
```

![Orbit Icon prime (light)](/examples/light/schemas/primes/icon.png)

![Orbit Icon prime (dark)](/examples/dark/schemas/primes/icon.png)

## Image prime

Avatar or thumbnail display.

```python
Image.make()
    .src('https://api.dicebear.com/9.x/shapes/svg?seed=orbit')
    .image_size(48)
```

![Orbit Image prime (light)](/examples/light/schemas/primes/image.png)

![Orbit Image prime (dark)](/examples/dark/schemas/primes/image.png)

## List prime

Bulleted unordered list.

```python
UnorderedList.make()
    .items(['Tables', 'Forms', 'Panels'])
    .bullet_size('sm')
```

![Orbit List prime (light)](/examples/light/schemas/primes/list.png)

![Orbit List prime (dark)](/examples/dark/schemas/primes/list.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
