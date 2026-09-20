---
title: Validation
description: Exhaustive Orbit Field validation helpers, Form.validate behavior, messages, and rule catalog.
---

## Introduction

Orbit validates with `Form.validate(data, **ctx)`, walking nested layouts (Section, Tabs, Wizard, Repeater schemas) via `iter_fields`. For each visible field with a state path it resolves the value, builds the rule list from `Field.get_rules()` (injecting `required` when `is_required()` is true), then:

1. **Callable rules** — evaluated through `evaluate`; `True` / `None` pass, `False` uses the default invalid message, any other value becomes the error string.
2. **String rules** — checked by `_check_rule` in `form.py` (Laravel-style tokens such as `email`, `max:255`, `required_if:role,admin`).

Errors return as `field_path → [messages]`. Database-backed `unique` / `exists` need checkers registered with `Form.unique_using(...)` and `Form.exists_using(...)` (or passed in `**ctx`).

Each subsection below includes explanation, a Python example, and screenshots of related form chrome.

## Running validation

Call `validate` with the submitted (or in-memory) state dict. Invisible fields are skipped. Nested paths use dot notation when reading state.

```python title="app/orbit/resources/user_resource.py"
from almasix.orbit.forms import Form, TextInput

form = Form.make().schema([
    TextInput.make('email').required().email().unique('users', 'email'),
    TextInput.make('password').required().confirmed(),
    TextInput.make('password_confirmation').required(),
    TextInput.make('role').default('user'),
    TextInput.make('admin_code').required_if('role', 'admin'),
])

errors = form.validate({
    'email': 'a',
    'password': 'x',
    'password_confirmation': 'y',
    'role': 'admin',
})
```

![Orbit Running validation (light)](/examples/light/forms/overview.png)

![Orbit Running validation (dark)](/examples/dark/forms/overview.png)

## Attaching rules

`.rules(*rules)` appends string tokens and/or callables. Fluent helpers below are thin wrappers that call `.rules(...)` (and sometimes set input `type`). Empty values skip most rules except presence-style ones (`required`, `filled`, `accepted`, and the conditional required/prohibited family).

```python title="app/orbit/resources/product_resource.py"
TextInput.make('sku')
    .rules('alpha_dash', 'max:32')
    .rules(lambda value, **_: True if value != 'root' else 'SKU is reserved.')
```

![Orbit Attaching rules (light)](/examples/light/forms/text-input/basic.png)

![Orbit Attaching rules (dark)](/examples/dark/forms/text-input/basic.png)

## Required and mark as required

`.required(condition=True)` accepts a bool or callable and injects a `required` rule when true at validation time. `.mark_as_required()` only controls the asterisk via `shows_required_asterisk()` without adding a rule — useful when validation is conditional but the UI should still look mandatory (or the reverse).

```python title="app/orbit/resources/post_resource.py"
TextInput.make('title')
    .label('Title')
    .required()

TextInput.make('slug')
    .label('Slug')
    .mark_as_required()
    .required(lambda data=None, **_: bool((data or {}).get('publish')))
```

![Orbit Required (light)](/examples/light/forms/text-input/required.png)

![Orbit Required (dark)](/examples/dark/forms/text-input/required.png)

## Length helpers

| Helper | Rule token | Enforced by `Form.validate` today |
|--------|------------|-----------------------------------|
| `.min_length(n)` | `min:n` | Yes (numeric or string length) |
| `.max_length(n)` | `max:n` | Yes |
| `.length(n)` | `size:n` | Fluent registers the rule; prefer min/max until `size:` is handled |
| `.between(lo, hi)` | `between:lo,hi` | Yes (number or string length) |

```python title="app/orbit/resources/profile_resource.py"
TextInput.make('username')
    .min_length(3)
    .max_length(30)
    .between(3, 30)

TextInput.make('pin')
    .length(4)
```

![Orbit Length helpers (light)](/examples/light/forms/text-input/length.png)

![Orbit Length helpers (dark)](/examples/dark/forms/text-input/length.png)

## Email, URL, numeric, integer, tel

`.email()`, `.url()`, and `.numeric()` set the HTML input type **and** append matching rules. `.integer()` chains numeric + `integer`. `.tel()` only sets `type="tel"` — add `.tel_regex(pattern)` or `.regex(pattern)` for format checks (`regex:` is enforced).

```python title="app/orbit/resources/contact_resource.py"
TextInput.make('email').email().required()
TextInput.make('website').url()
TextInput.make('quantity').numeric().min_value(0)
TextInput.make('count').integer()
TextInput.make('phone').tel().tel_regex(r'^\+?[0-9\s\-]+$')
```

![Orbit Email URL numeric (light)](/examples/light/forms/text-input/email.png)

![Orbit Email URL numeric (dark)](/examples/dark/forms/text-input/email.png)

## Regex

`.regex(pattern)` and `.tel_regex(pattern)` both append `regex:{pattern}`. Patterns are tested with `re.search` (not fullmatch) against the string value.

```python title="app/orbit/resources/account_resource.py"
TextInput.make('slug')
    .regex(r'^[a-z0-9\-]+$')
```

![Orbit Regex (light)](/examples/light/forms/text-input/mask.png)

![Orbit Regex (dark)](/examples/dark/forms/text-input/mask.png)

## Unique and exists

`.unique(table, column=None, ignore=None)` builds `unique:table,column,ignore`. `.exists(table, column=None)` builds `exists:table,column`. Register checkers once:

```python title="app/providers/orbit_panel_provider.py"
Form.unique_using(lambda value, table, column, **ctx: not db.exists(table, column, value, ignore=ctx.get('ignore')))
Form.exists_using(lambda value, table, column, **ctx: db.exists(table, column, value))
```

```python title="app/orbit/resources/user_resource.py"
TextInput.make('email')
    .email()
    .unique('users', 'email', ignore=lambda **ctx: ctx.get('record_id'))

TextInput.make('country_id')
    .exists('countries', 'id')
```

![Orbit Unique and exists (light)](/examples/light/forms/text-input/email.png)

![Orbit Unique and exists (dark)](/examples/dark/forms/text-input/email.png)

## Distinct

`.distinct()` appends `distinct`. Enforcement expects sibling values in validation context when the host provides them; otherwise the rule may no-op. Use for repeater rows that must not repeat a key.

```python title="app/orbit/resources/order_resource.py"
TextInput.make('sku')
    .distinct()
```

![Orbit Distinct (light)](/examples/light/forms/repeater/basic.png)

![Orbit Distinct (dark)](/examples/dark/forms/repeater/basic.png)

## Conditional required

| Helper | Rule |
|--------|------|
| `.required_if(field, value)` | `required_if:field,value` |
| `.required_unless(field, value)` | `required_unless:field,value` |
| `.required_with(*fields)` | `required_with:a,b` |
| `.required_with_all(*fields)` | `required_with_all:a,b` |
| `.required_without(*fields)` | `required_without:a,b` |
| `.required_without_all(*fields)` | `required_without_all:a,b` |
| `.required_if_accepted(field)` | `required_if_accepted:field` |

`required_if` / `required_unless` are enforced today. The `required_with*` / `required_if_accepted` helpers register rule tokens for hosts and future `_check_rule` coverage — prefer callable `.required(lambda state, **_: …)` when you need guaranteed enforcement of complex sibling logic now.

```python title="app/orbit/resources/account_resource.py"
TextInput.make('admin_code')
    .required_if('role', 'admin')

TextInput.make('company')
    .required_unless('account_type', 'personal')

TextInput.make('vat_number')
    .required_with('company')
```

![Orbit Conditional required (light)](/examples/light/forms/text-input/with-hint.png)

![Orbit Conditional required (dark)](/examples/dark/forms/text-input/with-hint.png)

## Prohibited

| Helper | Rule |
|--------|------|
| `.prohibited()` | `prohibited` |
| `.prohibited_if(field, value)` | `prohibited_if:field,value` |
| `.prohibits(*fields)` | `prohibits:a,b` |

`prohibited` / `prohibited_if` are enforced. `.prohibits()` registers the token for hosts and future enforcement; use a callable rule if you must block sibling fields today.

```python title="app/orbit/resources/account_resource.py"
TextInput.make('guest_note')
    .prohibited_if('role', 'admin')

TextInput.make('legacy_code')
    .prohibited()
```

![Orbit Prohibited (light)](/examples/light/forms/text-input/disabled.png)

![Orbit Prohibited (dark)](/examples/dark/forms/text-input/disabled.png)

## Confirmed, same, different

`.confirmed()` expects `{path}_confirmation` to match. `.same(field)` / `.different(field)` compare against another state path — all three are enforced.

```python title="app/orbit/resources/user_resource.py"
TextInput.make('password').password().confirmed()
TextInput.make('password_confirmation').password()
TextInput.make('email').same('email_confirmation')
TextInput.make('backup_email').different('email')
```

![Orbit Confirmed same different (light)](/examples/light/forms/text-input/password.png)

![Orbit Confirmed same different (dark)](/examples/dark/forms/text-input/password.png)

## Filled and present

`.filled()` requires a non-empty value (enforced). `.present()` registers the `present` token for hosts and future `_check_rule` coverage; prefer `.filled()` or `.required()` when you need enforcement today.

```python title="app/orbit/resources/profile_resource.py"
TextInput.make('display_name')
    .filled()
```

![Orbit Filled and present (light)](/examples/light/forms/text-input/basic.png)

![Orbit Filled and present (dark)](/examples/dark/forms/text-input/basic.png)

## String character classes

| Helper | Rule | Enforced |
|--------|------|----------|
| `.alpha()` | `alpha` | Yes |
| `.alpha_num()` | `alpha_num` | Yes |
| `.alpha_dash()` | `alpha_dash` | Yes |
| `.ascii()` | `ascii` | Token registered |
| `.starts_with(*values)` | `starts_with:a,b` | Yes |
| `.ends_with(*values)` | `ends_with:a,b` | Yes |
| `.doesnt_start_with(*values)` | `doesnt_start_with:…` | Token registered |
| `.doesnt_end_with(*values)` | `doesnt_end_with:…` | Token registered |

```python title="app/orbit/resources/catalog_resource.py"
TextInput.make('code')
    .alpha_dash()
    .starts_with('sku-', 'SKU-')
    .doesnt_end_with('-tmp')
```

![Orbit String character classes (light)](/examples/light/forms/text-input/prefix.png)

![Orbit String character classes (dark)](/examples/dark/forms/text-input/prefix.png)

## Network and identity formats

| Helper | Rule | Enforced |
|--------|------|----------|
| `.ip()` | `ip` | Yes (loose v4/v6) |
| `.ipv4()` / `.ipv6()` | `ipv4` / `ipv6` | Tokens registered |
| `.mac_address()` | `mac_address` | Token registered |
| `.url()` / `.active_url()` | `url` / `active_url` | `url` yes; `active_url` token |
| `.uuid()` / `.ulid()` | `uuid` / `ulid` | `uuid` yes; `ulid` token |
| `.json()` | `json` | Yes |
| `.hex_color()` | `hex_color` | Token registered |

```python title="app/orbit/resources/network_resource.py"
TextInput.make('host').ip()
TextInput.make('webhook').url().active_url()
TextInput.make('id').uuid()
TextInput.make('payload').json()
ColorPicker.make('tint')  # native color; or TextInput.make('tint').hex_color()
```

![Orbit Network and identity formats (light)](/examples/light/forms/color-picker/basic.png)

![Orbit Network and identity formats (dark)](/examples/dark/forms/color-picker/basic.png)

## Numeric extras

`.multiple_of(value)` registers `multiple_of:{value}`. `.between()`, `.min_value()` / `.max_value()` (HTML attrs) and raw `.rules('gt:…')` etc. cover ranges. `_check_rule` also understands raw `gt:`, `gte:`, `lt:`, `lte:`, `digits:`, `in:`, `not_in:` via `.rules(...)` without dedicated fluent wrappers.

```python title="app/orbit/resources/pricing_resource.py"
TextInput.make('quantity')
    .integer()
    .multiple_of(5)
    .rules('gte:5', 'lte:100')
```

![Orbit Numeric extras (light)](/examples/light/forms/text-input/numeric.png)

![Orbit Numeric extras (dark)](/examples/dark/forms/text-input/numeric.png)

## Date comparison helpers

| Helper | Rule | Enforced |
|--------|------|----------|
| `.after(date_or_field)` | `after:…` | Yes |
| `.before(date_or_field)` | `before:…` | Yes |
| `.after_or_equal(…)` | `after_or_equal:…` | Token registered |
| `.before_or_equal(…)` | `before_or_equal:…` | Token registered |
| `.date_equals(…)` | `date_equals:…` | Token registered |

Bounds may be ISO date strings or sibling field names. Raw `.rules('date')` is enforced when you need type checking without a fluent helper.

```python title="app/orbit/resources/event_resource.py"
DatePicker.make('starts_on').required()
DatePicker.make('ends_on')
    .after('starts_on')
    .before_or_equal('2027-01-01')
```

![Orbit Date comparison helpers (light)](/examples/light/forms/date-picker/min-max.png)

![Orbit Date comparison helpers (dark)](/examples/dark/forms/date-picker/min-max.png)

## Validation attribute and messages

`.validation_attribute('Email address')` replaces the attribute name in messages. `.validation_messages({key: template})` overrides per-rule templates. Placeholders `:attribute` / `{attribute}` and named `:key` / `{key}` are substituted by `format_validation_message()`.

```python title="app/orbit/resources/user_resource.py"
TextInput.make('email')
    .email()
    .required()
    .validation_attribute('Email address')
    .validation_messages({
        'required': 'Please enter an :attribute.',
        'email': 'That :attribute does not look valid.',
    })
```

![Orbit Validation messages (light)](/examples/light/forms/text-input/email.png)

![Orbit Validation messages (dark)](/examples/dark/forms/text-input/email.png)

## Callable rules cookbook

Return `True`/`None` to pass, `False` for the default invalid message, or a string for a custom message. Signatures can request `value`, `state`, `field`, `attribute`, `operation`, and any host-provided utilities.

```python title="app/orbit/resources/team_resource.py"
TextInput.make('slug')
    .rules(lambda value, state=None, **_: (
        True
        if not value or value not in (state or {}).get('reserved', [])
        else 'That slug is reserved.'
    ))
```

![Orbit Callable rules (light)](/examples/light/forms/text-input/basic.png)

![Orbit Callable rules (dark)](/examples/dark/forms/text-input/basic.png)

## Complete fluent helper index

Helpers that exist on `Field` today (Orbit Python API — not PHP). Chain freely; each returns `Self`.

```python title="app/orbit/resources/kitchen_sink_resource.py"
TextInput.make('email')
    .required()
    .email()
    .max_length(255)
    .unique('users', 'email')
    .validation_attribute('Email address')
    .validation_messages({'unique': 'That :attribute is taken.'})
```

![Orbit Complete fluent helper index (light)](/examples/light/forms/text-input/email.png)

![Orbit Complete fluent helper index (dark)](/examples/dark/forms/text-input/email.png)

Fluent helpers: `required`, `mark_as_required`, `rules`, `email`, `url`, `numeric`, `integer`, `tel` (type only), `password` (type only), `min_length`, `max_length`, `length`, `between`, `regex`, `tel_regex`, `unique`, `exists`, `distinct`, `required_if`, `required_unless`, `required_with`, `required_with_all`, `required_without`, `required_without_all`, `required_if_accepted`, `prohibited`, `prohibited_if`, `prohibits`, `confirmed`, `same`, `different`, `filled`, `present`, `alpha`, `alpha_num`, `alpha_dash`, `ascii`, `starts_with`, `ends_with`, `doesnt_start_with`, `doesnt_end_with`, `ip`, `ipv4`, `ipv6`, `mac_address`, `active_url`, `uuid`, `ulid`, `json`, `hex_color`, `multiple_of`, `after`, `after_or_equal`, `before`, `before_or_equal`, `date_equals`, `validation_attribute`, `validation_messages`, `format_validation_message`.

Raw tokens useful via `.rules(...)` without fluent wrappers: `nullable`, `accepted`, `boolean`, `array`, `date`, `in:`, `not_in:`, `digits:`, `gt:`, `gte:`, `lt:`, `lte:`, `max:`, `min:`, `mimes:` (when host checks files).

See also [Form closures](/forms/closures/) for conditional required/visibility and [Custom fields](/forms/custom-fields/) for adding rules on subclasses.
