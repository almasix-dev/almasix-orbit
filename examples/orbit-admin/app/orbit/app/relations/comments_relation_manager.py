"""Comments relation manager — nested table on the Posts view/edit pages."""

from __future__ import annotations

from almasix.orbit import RelationManager
from almasix.orbit.forms import Form, Select, Textarea, TextInput
from almasix.orbit.tables import BadgeColumn, Table, TextColumn

from app.models.comment import Comment


class CommentsRelationManager(RelationManager):
    relationship = "comments"
    title = "Comments"
    description = "Reader replies attached to this post."
    record_title_attribute = "author"
    related_model = Comment
    foreign_key = "post_id"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("author").required().max_length(80),
                Textarea.make("body").rows(3).required(),
                Select.make("status")
                .options({"visible": "Visible", "hidden": "Hidden"})
                .default("visible"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("author").searchable().sortable(),
                TextColumn.make("body").limit(60).wrap(),
                BadgeColumn.make("status").colors(
                    {"visible": "success", "hidden": "gray"}
                ),
            ]
        )
