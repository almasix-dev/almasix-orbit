---
title: One-time code input
description: OneTimeCodeInput optimizes for OTP and 2FA codes with autocomplete hints for password managers and SMS autofill.
---

## Introduction

OneTimeCodeInput optimizes for OTP and 2FA codes with autocomplete hints for password managers and SMS autofill.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic OTP input

![Orbit Basic OTP input (light)](/examples/light/forms/one-time-code-input/basic.png)

![Orbit Basic OTP input (dark)](/examples/dark/forms/one-time-code-input/basic.png)

Six-digit verification code.

```python
OneTimeCodeInput.make('code')
    .label('Verification code')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
