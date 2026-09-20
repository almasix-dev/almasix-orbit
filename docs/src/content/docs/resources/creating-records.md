---
title: Creating records
description: The create page — the resource form, what happens on submit, and how to shape defaults and validation.
---

Every resource gets a create page at `{resource}/create`. It renders the resource's [form](/forms/overview/) with a Create button, and the heading uses the singular label — **Create post**, not *Create Posts*.

![Orbit create page (light)](/examples/light/resources/creating.png)

![Orbit create page (dark)](/examples/dark/resources/creating.png)

## The form is the page

```python title="app/orbit/resources/post_resource.py"
class PostResource(Resource):
    model = Post
    model_label = "Post"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            TextInput.make("title").required().max_length(200),
            Select.make("status")
            .options({"draft": "Draft", "published": "Published"})
            .default("draft")
            .required(),
            Textarea.make("body").rows(6),
        ])
```

The same schema powers create and edit. Use the `operation` context in a field's callbacks when the two should differ — for example, a slug field that is editable on create and locked afterwards.

## What submit does

1. Field state lives on the page host, so every keystroke bound with `live()` updates the server-side state.
2. Create runs validation from the schema; failures re-render the form with messages in place.
3. For an ORM-backed resource, Orbit writes a row through the model (`id` and timestamp columns are stripped, and `fillable` is honoured).
4. An `orbit-record-created` event is dispatched and the browser is redirected to the new record's view page.

For a seed-list resource the new row is appended in memory instead, which is what the demo resources in the sample app do.

## Defaults

Set them on fields with `default(...)`, or fill state before rendering when the value depends on context:

```python
Select.make("status").options({...}).default("draft")
TextInput.make("author").default(lambda user=None, **_: getattr(user, "name", ""))
```

## Read-only resources

A resource whose records are not mutable shows an explanatory note instead of a form:

```python
class AuthorResource(Resource):
    records_mutable = False
```

Resources backed by an ORM model are mutable by default; seed lists are not unless you set `records_mutable = True`.

## Page width

Create, edit, and view pages use a narrower content width than the list page so forms stay readable. Override per resource:

```python
class PostResource(Resource):
    form_content_max_width = "screen-md"
```

## Related pages

- [Forms overview](/forms/overview/) — every field type and layout
- [Validation](/forms/validation/) — rules, messages, and custom checks
- [Editing records](/resources/editing-records/) — the same schema after the record exists
