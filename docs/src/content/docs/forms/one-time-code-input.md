---
title: One-time code input
description: OneTimeCodeInput is a TextInput preconfigured with autocomplete=one-time-code for OTP and MFA flows.
---

## Introduction

`OneTimeCodeInput` subclasses `TextInput`, forces `type="text"`, and sets `autocomplete="one-time-code"` so mobile browsers and password managers can offer SMS/app OTP autofill. All TextInput helpers apply — mask, length, numeric, revealable (rarely useful), trim, and validation.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic one-time code

Minimal OTP field ready for authenticator or SMS codes.

```python title="app/orbit/resources/example_resource.py"
OneTimeCodeInput.make('otp')
    .label('Authentication code')
    .placeholder('123456')
```

![Orbit Basic one-time code (light)](/examples/light/forms/one-time-code-input/basic.png)

![Orbit Basic one-time code (dark)](/examples/dark/forms/one-time-code-input/basic.png)

## Fixed length PIN

`.length(6)` registers exact-length intent; combine with `.numeric()` and `.mask()` for digit-only UX.

```python title="app/orbit/resources/example_resource.py"
OneTimeCodeInput.make('code')
    .label('Code')
    .length(6)
    .numeric()
    .mask('999999')
```

![Orbit Fixed length PIN (light)](/examples/light/forms/one-time-code-input/mask.png)

![Orbit Fixed length PIN (dark)](/examples/dark/forms/one-time-code-input/mask.png)

## Required OTP

Require the code on submit and autofocus for keyboard-first flows.

```python title="app/orbit/resources/example_resource.py"
OneTimeCodeInput.make('otp')
    .label('One-time code')
    .required()
    .autofocus()
    .autocomplete('one-time-code')
```

![Orbit Required OTP (light)](/examples/light/forms/one-time-code-input/required.png)

![Orbit Required OTP (dark)](/examples/dark/forms/one-time-code-input/required.png)

## Trim pasted codes

Users often paste codes with spaces — `.trim()` and `.strip_characters(' ')` clean dehydrate state.

```python title="app/orbit/resources/example_resource.py"
OneTimeCodeInput.make('otp')
    .label('Code')
    .trim()
    .strip_characters(' ')
    .length(6)
```

![Orbit Trim pasted codes (light)](/examples/light/forms/one-time-code-input/trim.png)

![Orbit Trim pasted codes (dark)](/examples/dark/forms/one-time-code-input/trim.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
