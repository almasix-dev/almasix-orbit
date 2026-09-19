---
title: Text input
description: TextInput is the workhorse field for single-line strings — titles, slugs, emails, and numeric values.
---

## Introduction

TextInput is the workhorse field for single-line strings — titles, slugs, emails, and numeric values. Orbit wraps native inputs with consistent label, hint, helper, prefix/suffix affixes, and validation rules that dehydrate with the form. Variants below show type modifiers, affix chrome, and interaction states you can combine on one field.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic text input

Label, placeholder, and helper text — the default starting point.

```python
TextInput.make('title')
    .label('Title')
    .placeholder('Enter a title…')
    .helper_text('Shown on the public page.')
```

![Orbit Basic text input (light)](/examples/light/forms/text-input/basic.png)

![Orbit Basic text input (dark)](/examples/dark/forms/text-input/basic.png)

## Email

Sets input type to email and adds an email validation rule.

```python
TextInput.make('email')
    .email()
    .label('Email')
    .placeholder('you@acme.test')
```

![Orbit Email (light)](/examples/light/forms/text-input/email.png)

![Orbit Email (dark)](/examples/dark/forms/text-input/email.png)

## Password (revealable)

Password type with an optional reveal toggle for accessibility.

```python
TextInput.make('password')
    .password()
    .revealable()
    .label('Password')
```

![Orbit Password (revealable) (light)](/examples/light/forms/text-input/password.png)

![Orbit Password (revealable) (dark)](/examples/dark/forms/text-input/password.png)

## URL

URL input type with built-in url validation.

```python
TextInput.make('website')
    .url()
    .label('Website')
    .placeholder('https://')
```

![Orbit URL (light)](/examples/light/forms/text-input/url.png)

![Orbit URL (dark)](/examples/dark/forms/text-input/url.png)

## Telephone

Tel input type for phone numbers.

```python
TextInput.make('phone')
    .tel()
    .label('Phone')
```

![Orbit Telephone (light)](/examples/light/forms/text-input/tel.png)

![Orbit Telephone (dark)](/examples/dark/forms/text-input/tel.png)

## Numeric

Number input with optional min/max bounds.

```python
TextInput.make('quantity')
    .numeric()
    .label('Quantity')
    .min_value(0)
    .max_value(99)
```

![Orbit Numeric (light)](/examples/light/forms/text-input/numeric.png)

![Orbit Numeric (dark)](/examples/dark/forms/text-input/numeric.png)

## Prefix text

Static text before the control — common for currency symbols.

```python
TextInput.make('price')
    .label('Price')
    .prefix('$')
    .numeric()
```

![Orbit Prefix text (light)](/examples/light/forms/text-input/prefix.png)

![Orbit Prefix text (dark)](/examples/dark/forms/text-input/prefix.png)

## Suffix text

Static text after the control — units, domains, etc.

```python
TextInput.make('weight')
    .label('Weight')
    .suffix('kg')
    .numeric()
```

![Orbit Suffix text (light)](/examples/light/forms/text-input/suffix.png)

![Orbit Suffix text (dark)](/examples/dark/forms/text-input/suffix.png)

## Prefix icon

Heroicon rendered inside the affix rail.

```python
TextInput.make('search')
    .label('Search')
    .prefix_icon('heroicon-o-magnifying-glass')
```

![Orbit Prefix icon (light)](/examples/light/forms/text-input/prefix-icon.png)

![Orbit Prefix icon (dark)](/examples/dark/forms/text-input/prefix-icon.png)

## Suffix icon

Trailing icon affix for links, locks, or status.

```python
TextInput.make('slug')
    .label('Slug')
    .suffix_icon('heroicon-o-link')
```

![Orbit Suffix icon (light)](/examples/light/forms/text-input/suffix-icon.png)

![Orbit Suffix icon (dark)](/examples/dark/forms/text-input/suffix-icon.png)

## Required

Shows the required asterisk and injects a required rule.

```python
TextInput.make('name')
    .label('Name')
    .required()
```

![Orbit Required (light)](/examples/light/forms/text-input/required.png)

![Orbit Required (dark)](/examples/dark/forms/text-input/required.png)

## Disabled

Non-interactive state for read-only contexts.

```python
TextInput.make('locked')
    .label('Locked field')
    .disabled()
```

![Orbit Disabled (light)](/examples/light/forms/text-input/disabled.png)

![Orbit Disabled (dark)](/examples/dark/forms/text-input/disabled.png)

## Readonly

Value visible but not editable — good for generated IDs.

```python
TextInput.make('id')
    .label('Record ID')
    .readonly()
```

![Orbit Readonly (light)](/examples/light/forms/text-input/readonly.png)

![Orbit Readonly (dark)](/examples/dark/forms/text-input/readonly.png)

## Copyable

Adds a one-click copy button beside the input.

```python
TextInput.make('token')
    .label('API token')
    .copyable()
    .readonly()
```

![Orbit Copyable (light)](/examples/light/forms/text-input/copyable.png)

![Orbit Copyable (dark)](/examples/dark/forms/text-input/copyable.png)

## Input mask

Client-side mask pattern for structured values like card numbers.

```python
TextInput.make('card')
    .label('Card number')
    .mask('9999 9999 9999 9999')
```

![Orbit Input mask (light)](/examples/light/forms/text-input/mask.png)

![Orbit Input mask (dark)](/examples/dark/forms/text-input/mask.png)

## Datalist suggestions

Native datalist autocomplete from a string list.

```python
TextInput.make('city')
    .label('City')
    .datalist(['Nairobi', 'London', 'Berlin'])
```

![Orbit Datalist suggestions (light)](/examples/light/forms/text-input/datalist.png)

![Orbit Datalist suggestions (dark)](/examples/dark/forms/text-input/datalist.png)

## With hint

Inline hint text and optional hint icon above the control.

```python
TextInput.make('slug')
    .label('Slug')
    .hint('Used in the public URL.')
    .hint_icon('heroicon-o-information-circle')
```

![Orbit With hint (light)](/examples/light/forms/text-input/with-hint.png)

![Orbit With hint (dark)](/examples/dark/forms/text-input/with-hint.png)

## Trim

`.trim()` marks the field so dehydrate strips leading and trailing whitespace before any custom `.dehydrate_state_using()` callback runs. It does not change the live input type or strip characters mid-typing — only the value that leaves the form. Use it on titles, slugs, and free-text fields where accidental spaces would break uniqueness or URLs.

```python title="app/orbit/resources/post_resource.py"
TextInput.make('title')
    .label('Title')
    .trim()
```

![Orbit Trim (light)](/examples/light/forms/text-input/trim.png)

![Orbit Trim (dark)](/examples/dark/forms/text-input/trim.png)

## Strip characters

`.strip_characters()` removes every listed character from the dehydrated string. Pass a string (each char is stripped) or a sequence of strings that are joined into the removal set. Strip runs before trim inside `apply_dehydrate_transforms`, so you can clear dashes/spaces and then trim leftovers. Ideal for SKUs, IBAN paste clean-up, and phone numbers that should store digits only.

```python title="app/orbit/resources/product_resource.py"
TextInput.make('sku')
    .label('SKU')
    .strip_characters(['-', ' '])
    .trim()
```

![Orbit Strip characters (light)](/examples/light/forms/text-input/strip-characters.png)

![Orbit Strip characters (dark)](/examples/dark/forms/text-input/strip-characters.png)

## Exact length

`.length(n)` records an exact character length and appends a `size:n` validation rule (Filament `length`). Pair it with `.mask()` or OTP-style inputs when the UI already constrains width. Prefer `.min_length()` / `.max_length()` (mapped to enforced `min:` / `max:` rules) when you need a range — `Form.validate` currently enforces `min`/`max`/`between`/`regex`, while `size:` is registered by the fluent helper for Filament parity.

```python title="app/orbit/resources/auth_resource.py"
TextInput.make('pin')
    .label('PIN')
    .length(4)
    .numeric()
```

![Orbit Exact length (light)](/examples/light/forms/text-input/length.png)

![Orbit Exact length (dark)](/examples/dark/forms/text-input/length.png)

## Telephone regex

`.tel()` only sets `type="tel"` for the mobile keyboard. `.tel_regex(pattern)` stores the pattern and adds a `regex:…` rule that `Form.validate` enforces. Combine both when you want native tel chrome plus a project-specific E.164 or national format.

```python title="app/orbit/resources/contact_resource.py"
TextInput.make('phone')
    .label('Phone')
    .tel()
    .tel_regex(r'^\+?[0-9\s\-]{7,20}$')
```

![Orbit Telephone regex (light)](/examples/light/forms/text-input/tel-regex.png)

![Orbit Telephone regex (dark)](/examples/dark/forms/text-input/tel-regex.png)

## Autocapitalize

`.autocapitalize(value)` emits the HTML `autocapitalize` attribute on the input (for example `sentences`, `words`, `characters`, or `none`). Browsers on mobile honor it for soft-keyboard behavior; desktop may ignore it. It does not rewrite state on dehydrate — pair with `.trim()` if you also want whitespace normalized.

```python title="app/orbit/resources/person_resource.py"
TextInput.make('full_name')
    .label('Full name')
    .autocapitalize('words')
```

![Orbit Autocapitalize (light)](/examples/light/forms/text-input/autocapitalize.png)

![Orbit Autocapitalize (dark)](/examples/dark/forms/text-input/autocapitalize.png)

## Mark as required

`.mark_as_required()` controls the required asterisk independently of the `required` validation rule. Use it when the field is visually mandatory (asterisk) but validation is conditional via `.required(callable)` or sibling rules, or to hide the asterisk while still validating with `.required()`. `shows_required_asterisk()` prefers `_mark_as_required` when set; otherwise it mirrors `is_required()`.

```python title="app/orbit/resources/profile_resource.py"
TextInput.make('nickname')
    .label('Nickname')
    .mark_as_required()
    .helper_text('Shown as required, but only validated when publishing.')
```

![Orbit Mark as required (light)](/examples/light/forms/text-input/mark-as-required.png)

![Orbit Mark as required (dark)](/examples/dark/forms/text-input/mark-as-required.png)

## Prefix and suffix icon colors

`.prefix_icon_color()` / `.suffix_icon_color()` add an `or-color-{color}` class on the affix icon span when a matching `.prefix_icon()` / `.suffix_icon()` is present. Colors follow Orbit’s semantic tokens (`primary`, `success`, `warning`, `danger`, `gray`, …). Text affixes (`.prefix()` / `.suffix()`) are unchanged — these helpers only tint icon chrome.

```python title="app/orbit/resources/invoice_resource.py"
TextInput.make('amount')
    .label('Amount')
    .numeric()
    .prefix_icon('heroicon-o-currency-dollar')
    .prefix_icon_color('success')
    .suffix_icon('heroicon-o-check-circle')
    .suffix_icon_color('primary')
```

![Orbit Prefix and suffix icon colors (light)](/examples/light/forms/text-input/prefix-icon-color.png)

![Orbit Prefix and suffix icon colors (dark)](/examples/dark/forms/text-input/prefix-icon-color.png)

## Content slots

Every `Field` can inject HTML around the label, control, and error region via nine slots: `.above_label()`, `.below_label()`, `.before_label()`, `.after_label()`, `.above_content()`, `.below_content()`, `.before_content()`, `.after_content()`, and `.below_error()`. Slot bodies accept strings or callables and are **not** HTML-escaped (unlike labels), so you can drop muted captions, badges, or small links. Prefer slots over wrapping the field in a custom layout when you only need adjacent chrome.

```python title="app/orbit/resources/author_resource.py"
TextInput.make('bio')
    .label('Bio')
    .above_label('<span class="or-badge">Public</span>')
    .below_label('Shown on the author page.')
    .above_content('Keep it under two sentences.')
    .below_error('Fix validation before saving.')
```

![Orbit Content slots (light)](/examples/light/forms/text-input/content-slots.png)

![Orbit Content slots (dark)](/examples/dark/forms/text-input/content-slots.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, content slots, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
