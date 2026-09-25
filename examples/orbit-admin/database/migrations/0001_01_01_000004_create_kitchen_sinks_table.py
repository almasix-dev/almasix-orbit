"""Kitchen-sink form demo — one row per profile, JSON for nested fields."""

from __future__ import annotations

from almasix.orm import Blueprint, Migration, Schema


class CreateKitchenSinksTable(Migration):
    """Profiles used by Demos → Kitchen sink (ORM-backed resource)."""

    async def up(self) -> None:
        await Schema.create("teams", self.teams)
        await Schema.create("kitchen_sinks", self.kitchen_sinks)

    async def down(self) -> None:
        await Schema.drop_if_exists("kitchen_sinks")
        await Schema.drop_if_exists("teams")

    def teams(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.timestamps()

    def kitchen_sinks(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("email").nullable()
        table.string("role").nullable()
        table.text("bio").nullable()
        table.string("plan").nullable()
        table.json("features").nullable()
        table.json("tags").nullable()
        table.decimal("amount", 10, 2).nullable()
        table.string("color").nullable()
        table.boolean("active").default(False)
        table.string("priority").nullable()
        table.string("joined").nullable()
        table.string("reviewed_at").nullable()
        table.string("opens_at").nullable()
        table.string("sprint_week").nullable()
        table.string("billing_month").nullable()
        table.string("vintage").nullable()
        table.string("native_day").nullable()
        table.string("avatar").nullable()
        table.json("owner").nullable()
        table.integer("manager_id").nullable()
        table.json("links").nullable()
        table.json("meta").nullable()
        table.json("blocks").nullable()
        table.text("body").nullable()
        table.boolean("terms").default(False)
        table.timestamps()
