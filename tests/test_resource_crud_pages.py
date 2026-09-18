"""Resource create/edit/view persistence, page actions, and form width."""

from __future__ import annotations

from typing import Any

from almasix.orbit.forms import Form, TextInput
from almasix.orbit.panels.conduit.hosts import CreateRecordHost, EditRecordHost, ViewRecordHost
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.tables import TextColumn, Table


class _DemoResource(Resource):
    model = type("Demo", (), {})
    slug = "demos"
    records: list[dict[str, Any]] = []

    @classmethod
    def get_records(cls):
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("name"), TextInput.make("email")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("name"), TextColumn.make("email")])


def _panel() -> Panel:
    return Panel.make("crud-demo").path("/")


def test_edit_and_view_load_record_by_id() -> None:
    _DemoResource.records = [{"id": 1, "name": "Ada", "email": "ada@test"}]
    panel = _panel()
    edit = EditRecordHost.bind(panel=panel, resource=_DemoResource)()
    edit.record_id = "1"
    edit.mount()
    assert edit.data["name"] == "Ada"
    html = edit.render()
    assert 'value="Ada"' in html
    assert 'model="data.name"' in html
    assert "or-page-actions" in html
    assert 'data-action="view"' in html
    assert 'data-action="delete"' in html
    assert "max-width: 48rem" in html

    view = ViewRecordHost.bind(panel=panel, resource=_DemoResource)()
    view.record_id = "1"
    view.mount()
    assert view.record["name"] == "Ada"
    vhtml = view.render()
    assert "Ada" in vhtml
    assert "or-page-actions" in vhtml
    assert "/demos/1/edit" in vhtml


def test_create_and_save_persist_to_resource_records() -> None:
    _DemoResource.records = [{"id": 1, "name": "Ada", "email": "ada@test"}]
    panel = _panel()
    create = CreateRecordHost.bind(panel=panel, resource=_DemoResource)()
    create.mount()
    create.set_property("data.name", "Grace")
    create.set_property("data.email", "grace@test")
    create.create()
    assert create.created_id == "2"
    assert _DemoResource.records[-1]["name"] == "Grace"
    redirect = create.take_redirect()
    assert redirect and redirect["url"].endswith("/demos/2")

    edit = EditRecordHost.bind(panel=panel, resource=_DemoResource)()
    edit.record_id = "2"
    edit.mount()
    edit.set_property("data.name", "Grace Hopper")
    edit.save()
    assert _DemoResource.records[-1]["name"] == "Grace Hopper"
    assert edit.take_redirect()["url"].endswith("/demos/2")


def test_view_delete_action_removes_record() -> None:
    _DemoResource.records = [
        {"id": 1, "name": "Ada", "email": "a@t"},
        {"id": 2, "name": "Grace", "email": "g@t"},
    ]
    panel = _panel()
    view = ViewRecordHost.bind(panel=panel, resource=_DemoResource)()
    view.record_id = "1"
    view.mount()
    view.mountAction("delete", record_id="1")
    assert [r["id"] for r in _DemoResource.records] == [2]
    assert view.take_redirect()["url"].endswith("/demos")
