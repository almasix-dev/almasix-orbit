"""Kitchen-sink profile — SQLite row behind the forms demo."""

from __future__ import annotations

from almasix.orm import Model

from app.models.user import User


class KitchenSink(Model):
    fillable = (
        "name",
        "email",
        "role",
        "bio",
        "plan",
        "features",
        "tags",
        "amount",
        "color",
        "active",
        "priority",
        "joined",
        "reviewed_at",
        "opens_at",
        "sprint_week",
        "billing_month",
        "vintage",
        "native_day",
        "avatar",
        "owner",
        "manager_id",
        "links",
        "meta",
        "blocks",
        "body",
        "terms",
    )
    casts = {
        "features": "array",
        "tags": "array",
        "links": "array",
        "meta": "json",
        "blocks": "array",
        "owner": "json",
        "active": "bool",
        "terms": "bool",
        "amount": "float",
    }

    def manager(self):
        return self.belongs_to(User, "manager_id")
