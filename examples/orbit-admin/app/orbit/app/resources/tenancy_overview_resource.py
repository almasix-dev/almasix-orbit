"""Tenancy showcase — switcher + two fake tenants + scoped project table."""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.orbit import Resource
from almasix.orbit.forms import Form, Select, TextInput
from almasix.orbit.tables import Table, TextColumn


class TenancyOverviewResource(Resource):
    """Focused sample for multi-tenancy docs — projects scoped by current tenant."""

    model = type("TenantProject", (), {})
    slug = "tenancy-overview"
    navigation_label = "Scoped projects"
    navigation_group = "Tenancy"
    navigation_icon = "heroicon-o-building-office-2"
    active_navigation_icon = "heroicon-s-building-office-2"
    navigation_sort = 0
    record_title_attribute = "title"
    records_mutable = False
    is_scoped_to_tenant = True

    records: ClassVar[list[dict[str, Any]]] = [
        {
            "id": 1,
            "title": "Launch site",
            "status": "Active",
            "tenant_id": 1,
            "owner": "Maya",
        },
        {
            "id": 2,
            "title": "Billing revamp",
            "status": "Draft",
            "tenant_id": 1,
            "owner": "Jordan",
        },
        {
            "id": 3,
            "title": "Support inbox",
            "status": "Active",
            "tenant_id": 1,
            "owner": "Alex",
        },
        {
            "id": 4,
            "title": "Beta onboarding",
            "status": "Active",
            "tenant_id": 2,
            "owner": "Sam",
        },
        {
            "id": 5,
            "title": "API sandbox",
            "status": "Draft",
            "tenant_id": 2,
            "owner": "Riley",
        },
    ]

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").label("Title").required(),
                Select.make("status")
                .label("Status")
                .options({"Active": "Active", "Draft": "Draft"}),
                TextInput.make("owner").label("Owner"),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.heading("Projects")
            .description(
                "Use the tenant switcher in the topbar. "
                "This list is scoped to the current team — Acme Corp or Beta Labs."
            )
            .columns(
                [
                    TextColumn.make("title").searchable(),
                    TextColumn.make("status").label("Status"),
                    TextColumn.make("owner").label("Owner"),
                ]
            )
        )
