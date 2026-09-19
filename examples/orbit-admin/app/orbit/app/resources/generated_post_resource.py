"""Posts resource — auto-generated from Schema.columns (``--generate`` demo).

Compare with hand-tuned ``post_resource.py``. Regenerate with::

    smith make:orbit-resource GeneratedPost --panel=app --model=Post --generate --force
"""

from __future__ import annotations

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput, Textarea
from almasix.orbit.tables import Table, TextColumn

from app.models.post import Post


class GeneratedPostResource(Resource):
    model = Post
    slug = "generated-posts"
    navigation_label = "Generated posts"
    navigation_group = "Demos"
    navigation_icon = "heroicon-o-sparkles"
    navigation_sort = 20
    record_title_attribute = "title"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").max_length(255),
                TextInput.make("status").max_length(255),
                Textarea.make("body").column_span("full"),
                TextInput.make("amount").integer(),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("id").sortable(),
                TextColumn.make("title").searchable().sortable(),
                TextColumn.make("status").searchable().sortable(),
                TextColumn.make("body").limit(50),
                TextColumn.make("amount").sortable(),
                TextColumn.make("created_at")
                .date_time()
                .sortable()
                .toggleable(is_toggled_hidden_by_default=True),
                TextColumn.make("updated_at")
                .date_time()
                .sortable()
                .toggleable(is_toggled_hidden_by_default=True),
            ]
        )
