"""Coverage for store-backed resources and form deep-links."""

from __future__ import annotations

import asyncio
from typing import Any, ClassVar

from almasix.orbit.forms import Form, TextInput
from almasix.orbit.panels.conduit.hosts import CreateRecordHost, ListRecordsHost, OrbitPageHost
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.routing import make_panel_page_action
from almasix.orbit.tables import Table, TextColumn
from almasix.orbit.panels.users import OrbitUser


class _Stored(Resource):
    slug = "stored"
    records_mutable = True
    refresh_records_on_mount = True
    records: ClassVar[list[dict[str, Any]]] = [{"id": "old", "title": "Old"}]
    deleted: ClassVar[list[str]] = []

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return [{"id": "fresh", "title": "Fresh"}]

    @classmethod
    def delete_record(cls, record_id: str) -> None:
        cls.deleted.append(str(record_id))

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])


class _Hooked(_Stored):
    slug = "hooked"

    @classmethod
    def mutate_form_data_before_create(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {**data, "id": "given"}


class _HookPassthrough(_Stored):
    slug = "hook-pass"

    @classmethod
    def mutate_form_data_before_create(cls, data: dict[str, Any]) -> Any:
        return None


class _FormPage(OrbitPageHost):
    form_id: str = ""

    @classmethod
    def _public_property_names(cls) -> set[str]:
        return {"form_id"}

    def render(self) -> str:
        return f'<p data-form="{self.form_id}">builder</p>'


def test_list_refreshes_and_deletes_through_store() -> None:
    panel = Panel.make("app").path("/app")
    host = ListRecordsHost.bind(panel=panel, resource=_Stored)()
    host.records = [{"id": "stale", "title": "Stale"}]
    host.mount()
    assert host.records[0]["id"] == "fresh"

    _Stored.deleted = []
    host.selected = ["fresh"]
    host.mountAction("delete", "fresh")
    assert _Stored.deleted == ["fresh"]
    assert host.records[0]["id"] == "fresh"


def test_create_uses_mutate_hook_or_keeps_payload() -> None:
    panel = Panel.make("app").path("/app")
    created = CreateRecordHost.bind(panel=panel, resource=_Hooked)()
    created.data = {"title": "Lead"}
    created.create()
    assert created.created_id == "given"

    passthrough = CreateRecordHost.bind(panel=panel, resource=_HookPassthrough)()
    passthrough.data = {"title": "Plain"}
    passthrough.create()
    assert passthrough.data["title"] == "Plain"
    assert passthrough.created_id


def test_page_action_loads_form_query() -> None:
    panel = Panel.make("app").path("/app").user(OrbitUser.default())
    host_cls = _FormPage.bind(panel=panel)

    class _Req:
        def __init__(self) -> None:
            self.path = "/app/form-builder"
            self.url = type("U", (), {"path": self.path})()
            self.query_params = {"form": "abc"}

    action = make_panel_page_action(panel, host_cls)
    result = asyncio.run(action(_Req()))
    body = getattr(result, "body", None) or getattr(result, "content", None) or str(result)
    text = body.decode() if isinstance(body, (bytes, bytearray)) else str(body)
    assert 'data-form="abc"' in text
