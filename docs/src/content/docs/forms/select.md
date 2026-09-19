---
title: Select
description: Select fields render native or searchable dropdowns with static options, grouped options, enums, or relationship-backed search.
---

## Introduction

Select is the primary control for choosing one value (or many, when `multiple` is enabled) from a known set. Orbit mirrors Filament’s fluent API: static maps, nested option groups, Python enums, BelongsTo-style relationships, AJAX search, and modal create/edit flows. Pair Select with [Multi select](/forms/multi-select/) when the field always stores a list, or call `.multiple()` on Select itself.

Each variation below includes a short explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic select

The default control is a native HTML `<select>` bound to form state. Pass a flat `dict` of value → label to `.options()`. Labels dehydrate as the stored keys, not the display text.

```python title="app/orbit/resources/post_resource.py"
Select.make('status')
    .label('Status')
    .options({
        'draft': 'Draft',
        'reviewing': 'Reviewing',
        'published': 'Published',
    })
```

![Orbit Basic select (light)](/examples/light/forms/select/basic.png)

![Orbit Basic select (dark)](/examples/dark/forms/select/basic.png)

## Native vs custom select

`.native(True)` (the default) keeps the browser select. Call `.native(False)` when you need Orbit’s richer dropdown chrome — search, HTML labels, create/edit actions, and wrapping — instead of the platform control.

```python title="app/orbit/resources/post_resource.py"
Select.make('status')
    .label('Status')
    .options({
        'draft': 'Draft',
        'reviewing': 'Reviewing',
        'published': 'Published',
    })
    .native(False)
```

![Orbit Native vs custom select (light)](/examples/light/forms/select/native.png)

![Orbit Native vs custom select (dark)](/examples/dark/forms/select/native.png)

## Searching options

Long option lists benefit from a filter input. `.searchable()` enables client- or server-driven filtering depending on whether options are static or relationship-backed.

```python title="app/orbit/resources/post_resource.py"
Select.make('author_id')
    .label('Author')
    .options({
        1: 'Ada Lovelace',
        2: 'Grace Hopper',
        3: 'Katherine Johnson',
    })
    .searchable()
```

![Orbit Searching options (light)](/examples/light/forms/select/searchable.png)

![Orbit Searching options (dark)](/examples/dark/forms/select/searchable.png)

## Custom search results

When options come from a database or external API, skip a static `.options()` map and supply `.get_search_results_using()`. Return a value → label dict for the current search string. Pair with `.get_option_label_using()` so the currently selected value still has a label before the user searches.

```python title="app/orbit/resources/post_resource.py"
Select.make('author_id')
    .label('Author')
    .searchable()
    .get_search_results_using(
        lambda search, **_: {
            a.id: a.name
            for a in Author.query().where('name', 'like', f'%{search}%').limit(50)
        }
    )
    .get_option_label_using(
        lambda value, **_: Author.find(value).name if value else None
    )
```

![Orbit Custom search results (light)](/examples/light/forms/select/custom-search.png)

![Orbit Custom search results (dark)](/examples/dark/forms/select/custom-search.png)

## Search prompt and messages

Customize the empty-search placeholder and async feedback strings. `.search_prompt()` sets the hint before typing; `.loading_message()`, `.searching_message()`, and `.no_search_results_message()` cover loading and empty states.

```python title="app/orbit/resources/post_resource.py"
Select.make('author_id')
    .label('Author')
    .relationship('author', 'name')
    .searchable()
    .search_prompt('Search authors by name')
    .loading_message('Loading authors…')
    .searching_message('Searching authors…')
    .no_search_results_message('No authors found.')
```

![Orbit Search prompt and messages (light)](/examples/light/forms/select/messages.png)

![Orbit Search prompt and messages (dark)](/examples/dark/forms/select/messages.png)

## Grouping options

Nest a dict of groups under `.options()`: outer keys become group headings, inner dicts are the selectable values. Groups work with searchable and native selects alike.

```python title="app/orbit/resources/post_resource.py"
Select.make('status')
    .label('Status')
    .searchable()
    .options({
        'In process': {
            'draft': 'Draft',
            'reviewing': 'Reviewing',
        },
        'Reviewed': {
            'published': 'Published',
            'rejected': 'Rejected',
        },
    })
```

![Orbit Grouping options (light)](/examples/light/forms/select/grouped.png)

![Orbit Grouping options (dark)](/examples/dark/forms/select/grouped.png)

## Enum options

`.enum()` builds the options map from a Python `Enum` (member value → humanized name). Useful when the field stores enum values already used elsewhere in the app.

```python title="app/orbit/resources/post_resource.py"
from enum import Enum

class Status(str, Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'

Select.make('status')
    .label('Status')
    .enum(Status)
```

![Orbit Enum options (light)](/examples/light/forms/select/enum.png)

![Orbit Enum options (dark)](/examples/dark/forms/select/enum.png)

## Multiple selection

`.multiple()` stores a list of selected keys instead of a single value. Prefer [MultiSelect](/forms/multi-select/) when the field is always multi; both share the same Select APIs (search, relationships, limits, reorder).

```python title="app/orbit/resources/post_resource.py"
Select.make('technologies')
    .label('Technologies')
    .multiple()
    .options({
        'tailwind': 'Tailwind CSS',
        'alpine': 'Alpine.js',
        'laravel': 'Laravel',
    })
```

![Orbit Multiple selection (light)](/examples/light/forms/select/multiple.png)

![Orbit Multiple selection (dark)](/examples/dark/forms/select/multiple.png)

## Relationship selects

`.relationship()` loads options from a related model (Filament BelongsTo / BelongsToMany style). Pass the relationship name and title attribute, or `option_label='{name} - {country}'` for multi-column labels. Without `.preload()`, searchable relationship selects fetch pages of `.options_limit()` results (default **50**) as the user types.

```python title="app/orbit/resources/album_resource.py"
Select.make('artist_id')
    .label('Artist')
    .relationship('artist', option_label='{name} - {country}')
    .searchable()
```

![Orbit Relationship selects (light)](/examples/light/forms/select/relationship.png)

![Orbit Relationship selects (dark)](/examples/dark/forms/select/relationship.png)

## Preloading relationship options

`.preload()` eagerly loads a capped option set on first render instead of waiting for search. Combine with `.searchable()` so users can still filter the preloaded list.

```python title="app/orbit/resources/album_resource.py"
Select.make('artist_id')
    .label('Artist')
    .relationship('artist', 'name')
    .searchable()
    .preload()
```

![Orbit Preloading relationship options (light)](/examples/light/forms/select/preload.png)

![Orbit Preloading relationship options (dark)](/examples/dark/forms/select/preload.png)

## Options limit

`.options_limit()` caps how many relationship or AJAX results are returned per request (default 50). Raise it for denser catalogs; keep it modest to protect query cost.

```python title="app/orbit/resources/album_resource.py"
Select.make('artist_id')
    .label('Artist')
    .relationship('artist', 'name')
    .searchable()
    .options_limit(100)
```

![Orbit Options limit (light)](/examples/light/forms/select/options-limit.png)

![Orbit Options limit (dark)](/examples/dark/forms/select/options-limit.png)

## Boolean options

`.boolean()` replaces custom options with Yes / No (`1` / `0`). Ideal for quick affirmative fields that still need a select rather than a checkbox.

```python title="app/orbit/resources/post_resource.py"
Select.make('featured')
    .label('Featured on homepage?')
    .boolean()
```

![Orbit Boolean options (light)](/examples/light/forms/select/boolean.png)

![Orbit Boolean options (dark)](/examples/dark/forms/select/boolean.png)

## Disabling specific options

`.disable_option_when()` receives each option value and returns `True` when that option should be non-selectable — retired statuses, sold-out SKUs, and similar.

```python title="app/orbit/resources/post_resource.py"
Select.make('status')
    .label('Status')
    .options({
        'draft': 'Draft',
        'published': 'Published',
        'archived': 'Archived',
    })
    .disable_option_when(lambda value, **_: value == 'archived')
```

![Orbit Disabling specific options (light)](/examples/light/forms/select/disable-option.png)

![Orbit Disabling specific options (dark)](/examples/dark/forms/select/disable-option.png)

## Wrapping option labels

Long labels can truncate awkwardly in the dropdown. `.wrap()` allows option text to wrap onto multiple lines inside the custom select.

```python title="app/orbit/resources/post_resource.py"
Select.make('policy')
    .label('Retention policy')
    .native(False)
    .options({
        '30d': 'Delete drafts older than 30 days after last edit',
        '90d': 'Archive published posts after 90 days of inactivity',
    })
    .wrap()
```

![Orbit Wrapping option labels (light)](/examples/light/forms/select/wrap.png)

![Orbit Wrapping option labels (dark)](/examples/dark/forms/select/wrap.png)

## Allowing HTML in labels

By default option labels are escaped. `.allow_html()` renders trusted HTML in labels (badges, emphasis). Only enable this for content you control — untrusted strings are an XSS risk.

```python title="app/orbit/resources/post_resource.py"
Select.make('priority')
    .label('Priority')
    .native(False)
    .options({
        'high': '<span class="text-danger">High</span>',
        'low': '<span class="text-muted">Low</span>',
    })
    .allow_html()
```

![Orbit Allowing HTML in labels (light)](/examples/light/forms/select/allow-html.png)

![Orbit Allowing HTML in labels (dark)](/examples/dark/forms/select/allow-html.png)

## Creating new options

`.create_option_form()` attaches a modal schema so users can insert a related record without leaving the form. `.create_option_using()` customizes persistence and must return the new option’s primary key.

```python title="app/orbit/resources/album_resource.py"
Select.make('artist_id')
    .label('Artist')
    .relationship('artist', 'name')
    .searchable()
    .create_option_form([
        TextInput.make('name').required(),
        TextInput.make('country'),
    ])
    .create_option_using(lambda data, **_: Artist.create(**data).id)
```

![Orbit Creating new options (light)](/examples/light/forms/select/create-option.png)

![Orbit Creating new options (dark)](/examples/dark/forms/select/create-option.png)

## Editing the selected option

`.edit_option_action()` exposes an action to open the selected related record for editing (Filament-style edit-option chrome). Pass `True` to enable the default action, or a named action string when you wire a custom handler.

```python title="app/orbit/resources/album_resource.py"
Select.make('artist_id')
    .label('Artist')
    .relationship('artist', 'name')
    .searchable()
    .edit_option_action()
```

![Orbit Editing the selected option (light)](/examples/light/forms/select/edit-option.png)

![Orbit Editing the selected option (dark)](/examples/dark/forms/select/edit-option.png)

## Selectable placeholder

When `.selectable_placeholder(True)` (default), the empty placeholder row can be chosen to clear the value. Disable it when a blank selection should not be allowed after the user picks a real option.

```python title="app/orbit/resources/post_resource.py"
Select.make('status')
    .label('Status')
    .placeholder('Choose a status')
    .options({
        'draft': 'Draft',
        'published': 'Published',
    })
    .selectable_placeholder(False)
```

![Orbit Selectable placeholder (light)](/examples/light/forms/select/selectable-placeholder.png)

![Orbit Selectable placeholder (dark)](/examples/dark/forms/select/selectable-placeholder.png)

## Limiting selection count

On multi selects, `.min_items()` and `.max_items()` constrain how many options may be chosen. Validation fails when the selection falls outside the range.

```python title="app/orbit/resources/post_resource.py"
Select.make('tags')
    .label('Tags')
    .multiple()
    .options({
        'orbit': 'Orbit',
        'forms': 'Forms',
        'tables': 'Tables',
    })
    .min_items(1)
    .max_items(3)
```

![Orbit Limiting selection count (light)](/examples/light/forms/select/min-max-items.png)

![Orbit Limiting selection count (dark)](/examples/dark/forms/select/min-max-items.png)

## Reordering selected options

`.reorderable()` lets users drag selected chips into a meaningful order when sequence matters (priority lists, display order). Requires `.multiple()`.

```python title="app/orbit/resources/post_resource.py"
Select.make('tags')
    .label('Tags')
    .multiple()
    .reorderable()
    .options({
        'orbit': 'Orbit',
        'forms': 'Forms',
        'tables': 'Tables',
    })
```

![Orbit Reordering selected options (light)](/examples/light/forms/select/reorderable.png)

![Orbit Reordering selected options (dark)](/examples/dark/forms/select/reorderable.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
