---
title: Radio
description: Radio presents mutually exclusive options with optional descriptions, columns, and Yes/No boolean mode.
---

## Introduction

Radio stores a single selected key from a fixed option set — plans, statuses, or any exclusive choice that should stay visible rather than hidden in a dropdown. Prefer [Select](/forms/select/) for long lists, and [Checkbox list](/forms/checkbox-list/) when users may pick more than one.

Each variation below includes a short explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic radio

`.options()` maps values to labels. Exactly one radio in the group may be selected; state is that key (or empty when none is chosen).

```python title="app/orbit/resources/subscription_resource.py"
Radio.make('plan')
    .label('Plan')
    .options({
        'starter': 'Starter',
        'pro': 'Pro',
        'enterprise': 'Enterprise',
    })
```

![Orbit Basic radio (light)](/examples/light/forms/radio/basic.png)

![Orbit Basic radio (dark)](/examples/dark/forms/radio/basic.png)

## Option descriptions

`.descriptions()` adds secondary copy under each matching option. Keys must align with `.options()` so the right helper sits under the right label.

```python title="app/orbit/resources/subscription_resource.py"
Radio.make('plan')
    .label('Plan')
    .options({
        'starter': 'Starter',
        'pro': 'Pro',
        'enterprise': 'Enterprise',
    })
    .descriptions({
        'starter': 'For side projects and prototypes.',
        'pro': 'For growing teams shipping weekly.',
        'enterprise': 'SSO, audit logs, and dedicated support.',
    })
```

![Orbit Option descriptions (light)](/examples/light/forms/radio/with-descriptions.png)

![Orbit Option descriptions (dark)](/examples/dark/forms/radio/with-descriptions.png)

## Multi-column layout

`.options_columns(n)` arranges radios in a grid. Two or three columns work well for short plan names; keep descriptions concise so cells do not collide.

```python title="app/orbit/resources/subscription_resource.py"
Radio.make('plan')
    .label('Plan')
    .options({
        'starter': 'Starter',
        'pro': 'Pro',
        'enterprise': 'Enterprise',
        'custom': 'Custom',
    })
    .options_columns(2)
```

![Orbit Multi-column layout (light)](/examples/light/forms/radio/columns.png)

![Orbit Multi-column layout (dark)](/examples/dark/forms/radio/columns.png)

## Boolean options

`.boolean()` swaps custom options for Yes / No (`1` / `0`) — a radio-group alternative to Checkbox when you want both answers explicit and equally weighted.

```python title="app/orbit/resources/post_resource.py"
Radio.make('feedback')
    .label('Like this post?')
    .boolean()
```

![Orbit Boolean options (light)](/examples/light/forms/radio/boolean.png)

![Orbit Boolean options (dark)](/examples/dark/forms/radio/boolean.png)

## Disabling specific options

`.disable_option_when()` greys out individual radios when their value should not be choosable — for example a published status reserved for another workflow.

```python title="app/orbit/resources/post_resource.py"
Radio.make('status')
    .label('Status')
    .options({
        'draft': 'Draft',
        'scheduled': 'Scheduled',
        'published': 'Published',
    })
    .disable_option_when(lambda value, **_: value == 'published')
```

![Orbit Disabling specific options (light)](/examples/light/forms/radio/disable-option.png)

![Orbit Disabling specific options (dark)](/examples/dark/forms/radio/disable-option.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
