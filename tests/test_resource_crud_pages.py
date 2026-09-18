"""Resource create/edit/view persistence, page actions, and form width."""

from __future__ import annotations

from typing import Any

from almasix.orbit.forms import Form, TextInput
from almasix.orbit.panels.conduit.hosts import CreateRecordHost, EditRecordHost, ViewRecordHost
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.tables import Table, TextColumn


class _DemoResource(Resource):
    model = type("Demo", (), {})
    slug = "demos"
    records_mutable = True
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
    assert "max-width: 64rem" in html

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


class _ImmutableResource(Resource):
    model = type("Seed", (), {})
    slug = "seeds"
    records_mutable = False
    records: list[dict[str, Any]] = [
        {"id": 1, "name": "Locked", "email": "locked@test"},
    ]

    @classmethod
    def get_records(cls):
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("name"), TextInput.make("email")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("name"), TextColumn.make("email")])


def test_immutable_seed_resource_hides_edit_create_and_save() -> None:
    assert _ImmutableResource.records_are_mutable() is False
    table = _ImmutableResource.get_table()
    html = table.records(list(_ImmutableResource.records)).render()
    assert 'data-action="view"' in html
    assert 'data-action="edit"' not in html
    assert 'data-action="delete"' not in html
    header = "".join(a.render() for a in table._header_actions)
    assert "/seeds/create" not in header

    panel = Panel.make("seed-demo").path("/")
    view = ViewRecordHost.bind(panel=panel, resource=_ImmutableResource)()
    view.record_id = "1"
    view.mount()
    vhtml = view.render()
    assert "/seeds/1/edit" not in vhtml
    assert 'data-action="edit"' not in vhtml

    edit = EditRecordHost.bind(panel=panel, resource=_ImmutableResource)()
    edit.record_id = "1"
    edit.mount()
    ehtml = edit.render()
    assert "cannot be changed" in ehtml
    assert ">Save<" not in ehtml
    edit.set_property("data.name", "Hacked")
    edit.save()
    assert _ImmutableResource.records[0]["name"] == "Locked"


def test_as_record_dict_json_serializes_datetimes() -> None:
    import json
    from datetime import date, datetime
    from decimal import Decimal

    from almasix.orbit.panels.conduit.hosts import _as_record_dict

    class _Row:
        def get_attributes(self):
            return {
                "id": 1,
                "title": "Hi",
                "created_at": datetime(2026, 9, 18, 11, 46, 12),
                "published_on": date(2026, 9, 18),
                "amount": Decimal("12.50"),
            }

    row = _as_record_dict(_Row())
    assert row["created_at"] == "2026-09-18T11:46:12"
    assert row["published_on"] == "2026-09-18"
    assert row["amount"] == 12.5
    json.dumps(row)  # must not raise


def test_mount_action_accepts_js_positional_payload() -> None:
    """Confirm modal calls mountAction(name, recordId, {data}) positionally."""
    from almasix.orbit.panels.conduit.hosts import ListRecordsHost

    _DemoResource.records = [
        {"id": 1, "name": "Ada", "email": "a@t"},
        {"id": 2, "name": "Grace", "email": "g@t"},
    ]
    panel = _panel()
    host = ListRecordsHost.bind(panel=panel, resource=_DemoResource)()
    host.mount()
    host.mountAction("delete", "1", {"data": {}})
    assert [r["id"] for r in host.records] == [2]
    assert [r["id"] for r in _DemoResource.records] == [2]
