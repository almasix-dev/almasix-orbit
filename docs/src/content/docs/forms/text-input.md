---
title: Text input
description: TextInput is the workhorse field for single-line strings — titles, slugs, emails, and numeric values.
---

## Introduction

TextInput is the workhorse field for single-line strings — titles, slugs, emails, and numeric values. Orbit wraps native inputs with consistent label, hint, helper, prefix/suffix affixes, and validation rules that dehydrate with the form. Variants below show type modifiers, affix chrome, and interaction states you can combine on one field.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic text input

![Orbit Basic text input (light)](/examples/light/forms/text-input/basic.png)

![Orbit Basic text input (dark)](/examples/dark/forms/text-input/basic.png)

Label, placeholder, and helper text — the default starting point.

```python
TextInput.make('title').label('Title').placeholder('Enter a title…').helper_text('Shown on the public page.')
```

## Email

![Orbit Email (light)](/examples/light/forms/text-input/email.png)

![Orbit Email (dark)](/examples/dark/forms/text-input/email.png)

Sets input type to email and adds an email validation rule.

```python
TextInput.make('email').email().label('Email').placeholder('you@acme.test')
```

## Password (revealable)

![Orbit Password (revealable) (light)](/examples/light/forms/text-input/password.png)

![Orbit Password (revealable) (dark)](/examples/dark/forms/text-input/password.png)

Password type with an optional reveal toggle for accessibility.

```python
TextInput.make('password').password().revealable().label('Password')
```

## URL

![Orbit URL (light)](/examples/light/forms/text-input/url.png)

![Orbit URL (dark)](/examples/dark/forms/text-input/url.png)

URL input type with built-in url validation.

```python
TextInput.make('website').url().label('Website').placeholder('https://')
```

## Telephone

![Orbit Telephone (light)](/examples/light/forms/text-input/tel.png)

![Orbit Telephone (dark)](/examples/dark/forms/text-input/tel.png)

Tel input type for phone numbers.

```python
TextInput.make('phone').tel().label('Phone')
```

## Numeric

![Orbit Numeric (light)](/examples/light/forms/text-input/numeric.png)

![Orbit Numeric (dark)](/examples/dark/forms/text-input/numeric.png)

Number input with optional min/max bounds.

```python
TextInput.make('quantity').numeric().label('Quantity').min_value(0).max_value(99)
```

## Prefix text

![Orbit Prefix text (light)](/examples/light/forms/text-input/prefix.png)

![Orbit Prefix text (dark)](/examples/dark/forms/text-input/prefix.png)

Static text before the control — common for currency symbols.

```python
TextInput.make('price').label('Price').prefix('$').numeric()
```

## Suffix text

![Orbit Suffix text (light)](/examples/light/forms/text-input/suffix.png)

![Orbit Suffix text (dark)](/examples/dark/forms/text-input/suffix.png)

Static text after the control — units, domains, etc.

```python
TextInput.make('weight').label('Weight').suffix('kg').numeric()
```

## Prefix icon

![Orbit Prefix icon (light)](/examples/light/forms/text-input/prefix-icon.png)

![Orbit Prefix icon (dark)](/examples/dark/forms/text-input/prefix-icon.png)

Heroicon rendered inside the affix rail.

```python
TextInput.make('search').label('Search').prefix_icon('heroicon-o-magnifying-glass')
```

## Suffix icon

![Orbit Suffix icon (light)](/examples/light/forms/text-input/suffix-icon.png)

![Orbit Suffix icon (dark)](/examples/dark/forms/text-input/suffix-icon.png)

Trailing icon affix for links, locks, or status.

```python
TextInput.make('slug').label('Slug').suffix_icon('heroicon-o-link')
```

## Required

![Orbit Required (light)](/examples/light/forms/text-input/required.png)

![Orbit Required (dark)](/examples/dark/forms/text-input/required.png)

Shows the required asterisk and injects a required rule.

```python
TextInput.make('name').label('Name').required()
```

## Disabled

![Orbit Disabled (light)](/examples/light/forms/text-input/disabled.png)

![Orbit Disabled (dark)](/examples/dark/forms/text-input/disabled.png)

Non-interactive state for read-only contexts.

```python
TextInput.make('locked').label('Locked field').disabled()
```

## Readonly

![Orbit Readonly (light)](/examples/light/forms/text-input/readonly.png)

![Orbit Readonly (dark)](/examples/dark/forms/text-input/readonly.png)

Value visible but not editable — good for generated IDs.

```python
TextInput.make('id').label('Record ID').readonly()
```

## Copyable

![Orbit Copyable (light)](/examples/light/forms/text-input/copyable.png)

![Orbit Copyable (dark)](/examples/dark/forms/text-input/copyable.png)

Adds a one-click copy button beside the input.

```python
TextInput.make('token').label('API token').copyable().readonly()
```

## Input mask

![Orbit Input mask (light)](/examples/light/forms/text-input/mask.png)

![Orbit Input mask (dark)](/examples/dark/forms/text-input/mask.png)

Client-side mask pattern for structured values like card numbers.

```python
TextInput.make('card').label('Card number').mask('9999 9999 9999 9999')
```

## Datalist suggestions

![Orbit Datalist suggestions (light)](/examples/light/forms/text-input/datalist.png)

![Orbit Datalist suggestions (dark)](/examples/dark/forms/text-input/datalist.png)

Native datalist autocomplete from a string list.

```python
TextInput.make('city').label('City').datalist(['Nairobi', 'London', 'Berlin'])
```

## With hint

![Orbit With hint (light)](/examples/light/forms/text-input/with-hint.png)

![Orbit With hint (dark)](/examples/dark/forms/text-input/with-hint.png)

Inline hint text and optional hint icon above the control.

```python
TextInput.make('slug').label('Slug').hint('Used in the public URL.').hint_icon('heroicon-o-information-circle')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
