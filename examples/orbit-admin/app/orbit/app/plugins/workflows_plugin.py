"""A published contract workflow on the admin panel.

Sign in as Ada (the first seeded user) to see the open draft in the inbox.
"""

from __future__ import annotations

from typing import Any

from almasix_orbit_workflows import (
    CanvasPage,
    CasePage,
    Directory,
    InboxPage,
    Person,
    WorkflowEngine,
    WorkflowPlugin,
    contract_workflow,
    current_engine,
    install,
)


def contract_engine() -> WorkflowEngine:
    """Legal and finance share one published contract. Ada has already started it."""
    engine = WorkflowEngine(
        directory=Directory(
            [
                {"id": "1", "name": "Ada Lovelace", "roles": ["sales"]},
                {"id": "2", "name": "Alan Turing", "roles": ["legal"]},
                {"id": "3", "name": "Grace Hopper", "roles": ["finance"]},
            ]
        )
    )
    document = contract_workflow().document()
    engine.save(document)
    engine.publish("contract")
    engine.start("contract", Person.of("1", "Ada Lovelace"))
    return engine


class ContractDesigner(CanvasPage):
    """The contract document, when the page is opened without a key."""

    @classmethod
    def render(cls, **ctx: Any) -> str:
        if not ctx.get("key") and not isinstance(ctx.get("document"), dict):
            ctx = {**ctx, "key": "contract"}
        return super().render(**ctx)


class OpenCase(CasePage):
    """The case Ada started, when the page is opened without an id."""

    @classmethod
    def render(cls, **ctx: Any) -> str:
        if not ctx.get("case_id"):
            cases = list(current_engine().store.cases.values())
            if cases:
                ctx = {**ctx, "case_id": cases[-1]["id"]}
        return super().render(**ctx)


class DemoWorkflows(WorkflowPlugin):
    """Inbox, case, and designer, added beside the panel's existing pages."""

    def register(self, panel: Any) -> None:
        install(self.engine)
        panel.pages([*panel.get_pages(), InboxPage, OpenCase, ContractDesigner])
