"""Coverage for ORM-backed resource hosts and JSON-safe record dicts."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from types import SimpleNamespace
from typing import Any, ClassVar

import pytest
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.panels.conduit import hosts as hosts_mod
from almasix.orbit.panels.conduit.hosts import (
    CreateRecordHost,
    EditRecordHost,
    FormHost,
    ListRecordsHost,
    ViewRecordHost,
    _as_record_dict,
    _await_maybe,
    _find_record,
    _is_orm_model,
    _jsonable_value,
    _mount_action_args,
    _next_record_id,
    _orm_create,
    _orm_delete_ids,
    _orm_fetch_all,
    _orm_find,
    _orm_update,
    _orm_write_payload,
    _resource_model,
    _resource_mutable,
    _resource_records,
    _save_resource_records,
)
from almasix.orbit.panels.pages import resource_pages as rp
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.routing import _embed_async
from almasix.orbit.tables import Table, TextColumn
from almasix.orm import Model


class _Color(Enum):
    RED = "red"


class _BrokenIso:
    def isoformat(self) -> str:
        raise RuntimeError("nope")


class _OrmRow:
    def __init__(self, **attrs: Any) -> None:
        self.__dict__.update(attrs)

    def get_attributes(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    async def save(self) -> bool:
        return True

    async def delete(self) -> bool:
        store = getattr(type(self), "_store", None)
        if isinstance(store, list):
            store[:] = [r for r in store if getattr(r, "id", None) != self.id]
        return True


class _OrmModel:
    """Stand-in Model used via monkeypatch of ``_resource_model``."""

    fillable = ("title", "status", "amount")
    _store: ClassVar[list[_OrmRow]] = []
    _next_id: ClassVar[int] = 1

    @classmethod
    def reset(cls) -> None:
        cls._store = []
        cls._next_id = 1
        _OrmRow._store = cls._store  # type: ignore[attr-defined]

    @classmethod
    async def all(cls) -> list[_OrmRow]:
        return list(cls._store)

    @classmethod
    async def find(cls, key: Any) -> _OrmRow | None:
        rid = str(key)
        for row in cls._store:
            if str(row.id) == rid:
                return row
        return None

    @classmethod
    async def create(cls, attributes: dict[str, Any] | None = None, **kwargs: Any) -> _OrmRow:
        data = dict(attributes or {})
        data.update(kwargs)
        row = _OrmRow(id=cls._next_id, created_at=datetime(2026, 1, 2, 3, 4, 5), **data)
        cls._next_id += 1
        cls._store.append(row)
        _OrmRow._store = cls._store  # type: ignore[attr-defined]
        return row


class _SyncOrmModel(_OrmModel):
    """Sync ORM API (no coroutines) to exercise ``_await_maybe`` sync branch."""

    @classmethod
    def all(cls):  # type: ignore[override]
        return list(cls._store)

    @classmethod
    def find(cls, key: Any):  # type: ignore[override]
        rid = str(key)
        for row in cls._store:
            if str(row.id) == rid:
                return row
        return None

    @classmethod
    def create(cls, attributes=None, **kwargs):  # type: ignore[override]
        data = dict(attributes or {})
        data.update(kwargs)
        row = _OrmRow(id=cls._next_id, **data)
        cls._next_id += 1
        cls._store.append(row)
        _OrmRow._store = cls._store  # type: ignore[attr-defined]
        return row


class _RealOrmPost(Model):
    fillable = ("title",)


class _OrmResource(Resource):
    model = type("FakePost", (), {})
    slug = "orm-posts"
    records_mutable = None

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title"), TextInput.make("status")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title"), TextColumn.make("status")])


class _SeedResource(Resource):
    model = type("Seed", (), {})
    slug = "seeds"
    records_mutable = False
    records: ClassVar[list[dict[str, Any]]] = [{"id": 1, "name": "Locked"}]

    @classmethod
    def get_records(cls):
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("name")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("name")])


def _panel() -> Panel:
    return Panel.make("orm-demo").path("/")


def test_jsonable_value_covers_nested_and_edge_types() -> None:
    assert _jsonable_value(None) is None
    assert _jsonable_value({"a": datetime(2026, 9, 18, 1, 2, 3)}) == {
        "a": "2026-09-18T01:02:03"
    }
    assert _jsonable_value((date(2026, 9, 18), Decimal("3"))) == ["2026-09-18", 3]
    assert _jsonable_value(Decimal("1.5")) == 1.5
    assert _jsonable_value(_Color.RED) == "red"
    assert _jsonable_value(b"hi") == "hi"
    assert isinstance(_jsonable_value(_BrokenIso()), str)
    assert _jsonable_value(object())  # falls through to str()


def test_as_record_dict_and_write_payload() -> None:
    assert _as_record_dict(None) == {}
    assert _as_record_dict({"id": 1, "created_at": datetime(2026, 1, 1)})["created_at"].startswith(
        "2026"
    )

    class BoomAttrs:
        def get_attributes(self):
            raise RuntimeError("boom")

        def __init__(self) -> None:
            self.id = 9
            self.title = "T"

    assert _as_record_dict(BoomAttrs())["title"] == "T"

    class NonDictAttrs:
        def get_attributes(self):
            return "nope"

        def __init__(self) -> None:
            self.id = 2
            self.title = "X"

    assert _as_record_dict(NonDictAttrs())["title"] == "X"

    payload = _orm_write_payload(
        {"id": 1, "title": "A", "status": "draft", "created_at": "x", "extra": 1},
        _OrmModel,
    )
    assert payload == {"title": "A", "status": "draft"}
    assert _mount_action_args("delete", None, {"recordId": 7, "data": {"x": 1}})[1] == "7"
    assert _mount_action_args("delete", recordId="9")[1] == "9"


def test_resource_records_helpers_and_orm_detection() -> None:
    class WithRecords(Resource):
        model = type("W", (), {})
        records = [{"id": "a"}]

    assert _resource_records(WithRecords) == [{"id": "a"}]
    _save_resource_records(WithRecords, [{"id": "b"}])
    assert WithRecords.records == [{"id": "b"}]
    assert _find_record([{"id": 1}], "") is None
    assert _find_record([SimpleNamespace(id=2)], "2") is not None
    assert _next_record_id([{"id": "x"}, {"id": 3}]) == 4

    assert _is_orm_model(None) is False
    assert _is_orm_model(type("Post", (), {})) is False
    assert _is_orm_model(_RealOrmPost) is True
    assert _is_orm_model(Model) is False
    assert _resource_model(SimpleNamespace(model=_RealOrmPost)) is _RealOrmPost
    assert _resource_model(SimpleNamespace(model=type("X", (), {}))) is None

    class NoFn:
        records_mutable = True

    assert _resource_mutable(NoFn) is True

    class Locked:
        records_mutable = False

    assert _resource_mutable(Locked) is False

    class Auto:
        records_mutable = None
        model = _RealOrmPost

    assert _resource_mutable(Auto) is True


@pytest.mark.asyncio
async def test_orm_helper_coroutines() -> None:
    _OrmModel.reset()
    await _OrmModel.create({"title": "A", "status": "draft"})
    rows = await _orm_fetch_all(_OrmModel)
    assert rows and rows[0]["title"] == "A"
    assert await _orm_find(_OrmModel, "999") is None
    found = await _orm_find(_OrmModel, "1")
    assert found is not None
    # digit retry path when string miss then int hit
    _OrmModel._store[0].id = 42
    assert await _orm_find(_OrmModel, "42") is not None

    created = await _orm_create(_OrmModel, {"title": "B", "status": "x", "id": 9})
    assert created["title"] == "B"
    updated = await _orm_update(_OrmModel, str(created["id"]), {"title": "B2"})
    assert updated["title"] == "B2"
    missing = await _orm_update(_OrmModel, "9999", {"title": "New"})
    assert missing["title"] == "New"
    await _orm_delete_ids(_OrmModel, {"", str(created["id"]), "nope"})
    assert await _await_maybe(5) == 5

    _SyncOrmModel.reset()
    row = _SyncOrmModel.create({"title": "S"})
    assert row.title == "S"
    assert await _orm_fetch_all(_SyncOrmModel)


@pytest.mark.asyncio
async def test_orm_list_create_edit_delete_hosts(monkeypatch: pytest.MonkeyPatch) -> None:
    _OrmModel.reset()
    await _OrmModel.create({"title": "One", "status": "draft", "amount": 10})
    monkeypatch.setattr(hosts_mod, "_resource_model", lambda resource: _OrmModel)
    monkeypatch.setattr(hosts_mod, "_resource_mutable", lambda resource: True)

    panel = _panel()
    listing = ListRecordsHost.bind(panel=panel, resource=_OrmResource)()
    await listing.mount()
    assert len(listing.records) == 1
    assert isinstance(listing.records[0]["created_at"], str)

    await listing.mountAction("delete", "1", {"data": {}})
    assert listing.records == []
    assert await _OrmModel.find(1) is None

    await listing.mountAction("create", None, {"data": {"title": "Two", "status": "published"}})
    assert len(listing.records) == 1
    rid = str(listing.records[0]["id"])

    await listing.mountAction(
        "edit", rid, {"data": {"title": "Two!", "status": "published"}}
    )
    assert listing.records[0]["title"] == "Two!"

    # edit missing id appends
    await listing.mountAction("edit", "999", {"data": {"title": "Ghost", "status": "draft"}})
    assert any(r.get("title") == "Ghost" for r in listing.records)

    listing.selected = [rid]
    await listing.mountAction("delete_bulk", None, {"data": {}})
    assert all(str(r.get("id")) != rid for r in listing.records)

    # custom action fallthrough
    await listing._mount_action_orm(_OrmModel, "custom", "", {})


@pytest.mark.asyncio
async def test_orm_create_edit_view_hosts(monkeypatch: pytest.MonkeyPatch) -> None:
    _OrmModel.reset()
    row = await _OrmModel.create({"title": "Ada", "status": "draft"})
    monkeypatch.setattr(hosts_mod, "_resource_model", lambda resource: _OrmModel)
    monkeypatch.setattr(hosts_mod, "_resource_mutable", lambda resource: True)

    panel = _panel()
    create = CreateRecordHost.bind(panel=panel, resource=_OrmResource)()
    create.mount(data={"title": "pre"})
    create.set_property("data.title", "Grace")
    create.set_property("data.status", "published")
    await create.create()
    assert create.created_id
    assert create.take_redirect()["url"].endswith(f"/orm-posts/{create.created_id}")
    create.mountAction("ping", "1", {"data": {}})

    edit = EditRecordHost.bind(panel=panel, resource=_OrmResource)()
    edit.record_id = str(row.id)
    await edit.mount()
    assert edit.data["title"] == "Ada"
    edit.set_property("data.title", "Ada Lovelace")
    await edit.save()
    assert (await _OrmModel.find(row.id)).title == "Ada Lovelace"
    assert edit.take_redirect()["url"].endswith(f"/orm-posts/{row.id}")

    # mount with explicit record kwargs
    edit2 = EditRecordHost.bind(panel=panel, resource=_OrmResource)()
    edit2.mount(record={"id": 7, "title": "R"})
    assert edit2.record_id == "7"

    view = ViewRecordHost.bind(panel=panel, resource=_OrmResource)()
    view.record_id = str(row.id)
    await view.mount()
    assert view.record["title"] == "Ada Lovelace"
    await view.mountAction("delete", str(row.id), {"data": {}})
    assert await _OrmModel.find(row.id) is None
    assert view.take_redirect()["url"].endswith("/orm-posts")

    created = await _OrmModel.create({"title": "Keep", "status": "draft"})
    edit3 = EditRecordHost.bind(panel=panel, resource=_OrmResource)()
    edit3.record_id = str(created.id)
    await edit3.mount()
    await edit3.mountAction("delete", None, {"data": {}})
    assert await _OrmModel.find(created.id) is None

    view2 = ViewRecordHost.bind(panel=panel, resource=_OrmResource)()
    view2.mount(record={"id": 8, "title": "V"})
    assert view2.record_id == "8"
    view2.mountAction("custom", "8", {})


def test_immutable_host_guards() -> None:
    panel = Panel.make("seed").path("/")
    listing = ListRecordsHost.bind(panel=panel, resource=_SeedResource)()
    listing.mount()
    listing.mountAction("delete", "1", {"data": {}})
    assert _SeedResource.records[0]["id"] == 1

    create = CreateRecordHost.bind(panel=panel, resource=_SeedResource)()
    create.create()
    assert create.created_id is None
    html = create.render()
    assert "cannot be changed" in html

    edit = EditRecordHost.bind(panel=panel, resource=_SeedResource)()
    edit.record_id = "1"
    edit.mount()
    edit.save()
    assert _SeedResource.records[0]["name"] == "Locked"
    ehtml = edit.render()
    assert "cannot be changed" in ehtml
    edit.mountAction("delete", "1", {"data": {}})
    assert _SeedResource.records[0]["id"] == 1

    view = ViewRecordHost.bind(panel=panel, resource=_SeedResource)()
    view.record_id = "1"
    view.mount()
    view.mountAction("delete", "1", {"data": {}})
    assert _SeedResource.records[0]["id"] == 1


def test_resource_mutability_helpers() -> None:
    class Seed(Resource):
        model = type("Seed", (), {})

    assert Seed.records_are_mutable() is False
    assert Seed._uses_orm_model() is False

    class Flagged(Resource):
        model = type("X", (), {})
        records_mutable = True

    assert Flagged.records_are_mutable() is True

    class Locked(Resource):
        model = type("Y", (), {})
        records_mutable = False

    assert Locked.records_are_mutable() is False

    class Real(Resource):
        model = _RealOrmPost
        records_mutable = None

    assert Real._uses_orm_model() is True
    assert Real.records_are_mutable() is True

    class NoModel(Resource):
        model = None

    assert NoModel._uses_orm_model() is False

    table = Seed.get_table()
    names = [a.get_name() for a in table._actions]
    assert "edit" not in names
    assert table._header_actions == []


def test_resource_pages_header_and_mutable_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rp, "_auth_user", lambda: None)
    record = {"id": 1, "name": "Ada"}

    class Mutable(Resource):
        model = type("M", (), {})
        slug = "ms"
        records_mutable = True

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("name")])

    html = rp._page_header_actions(Mutable, "view", record)
    assert "edit" in html
    html2 = rp._page_header_actions(Mutable, "edit", record)
    assert "view" in html2
    assert rp._resource_is_mutable(_SeedResource) is False

    class GateUser:
        def can(self, *a, **k):
            return False

    monkeypatch.setattr(rp, "_auth_user", lambda: GateUser())
    assert "edit" in rp._page_header_actions(Mutable, "view", record)


@pytest.mark.asyncio
async def test_embed_async_awaits_async_mount() -> None:
    host = ListRecordsHost.bind(panel=_panel(), resource=_SeedResource)()

    async def _async_mount(**kwargs):
        host.records = [{"id": 1, "name": "Async"}]
        host._mount_list_page(_SeedResource)

    host.mount = _async_mount  # type: ignore[method-assign]
    html = await _embed_async(host)
    assert "Async" in html or "or-page" in html or "conduit" in html or "wire" in html


def test_form_host_mount_action() -> None:
    host = FormHost()
    host.mount(data={"a": 1})
    assert host.data["a"] == 1
    host.mountAction("x", "1", {"data": {}})
    host.save()


def test_form_data_mutations_nested_paths() -> None:
    panel = _panel()

    class Mutable(Resource):
        model = type("M", (), {})
        slug = "mut"
        records_mutable = True
        records: ClassVar[list[dict[str, Any]]] = []

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("title")])

    host = CreateRecordHost.bind(panel=panel, resource=Mutable)()
    host.mount()
    host.set_property("data", {"title": "T", "links": []})
    assert host.data["title"] == "T"
    host.set_property("data.title", "T2")
    assert host.data["title"] == "T2"
    host.addRepeaterItem("links")
    host.addRepeaterItem("links")
    host.set_property("data.links.0.label", "A")
    host.moveRepeaterItem("links", 0, 1)
    host.cloneRepeaterItem("links", 0)
    host.removeRepeaterItem("links", 0)
    host.addBuilderBlock("blocks", "hero")
    host.addKeyValueRow("meta")
    host.addKeyValueRow("meta")
    # edge cases
    host.moveRepeaterItem("links", "bad", 1)
    host.removeRepeaterItem("missing", 0)
    host.cloneRepeaterItem("links", 99)
    host._form_path_set("", "x")
    host.data = None  # type: ignore[assignment]
    host._form_path_set("z.y", 1)
    assert isinstance(host.data, dict)


def test_edit_save_memory_object_records_and_append() -> None:
    class Obj:
        def __init__(self, id, name):  # noqa: A002
            self.id = id
            self.name = name

        def __setattr__(self, key, value):
            if key == "name" and value == "boom":
                raise RuntimeError("nope")
            super().__setattr__(key, value)

    class Mem(Resource):
        model = type("Mem", (), {})
        slug = "mems"
        records_mutable = True
        records: ClassVar[list[Any]] = [Obj(1, "Ada"), {"id": 2, "name": "Grace"}]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("name")])

    panel = Panel.make("mem").path("/")
    edit = EditRecordHost.bind(panel=panel, resource=Mem)()
    edit.record_id = "1"
    edit.mount()
    edit.set_property("data.name", "Ada2")
    edit.save()
    assert Mem.records[0].name == "Ada2"

    edit.set_property("data.name", "boom")
    edit.save()  # setattr failure swallowed

    # append when id not found
    edit2 = EditRecordHost.bind(panel=panel, resource=Mem)()
    edit2.record_id = "99"
    edit2.data = {"name": "New"}
    edit2.save()
    assert any(_record_keyish(r) == "99" or (isinstance(r, dict) and r.get("name") == "New") for r in Mem.records)

    # create-style save with empty record_id
    edit3 = EditRecordHost.bind(panel=panel, resource=Mem)()
    edit3.record_id = ""
    edit3.data = {"name": "Fresh"}
    edit3.save()
    assert any(isinstance(r, dict) and r.get("name") == "Fresh" for r in Mem.records)

    # memory delete from edit/view
    before = len(Mem.records)
    edit4 = EditRecordHost.bind(panel=panel, resource=Mem)()
    edit4.record_id = "2"
    edit4.mountAction("delete", "2", {"data": {}})
    assert len(Mem.records) == before - 1


def _record_keyish(record: Any) -> str:
    if isinstance(record, dict):
        return str(record.get("id", ""))
    return str(getattr(record, "id", "") or "")


@pytest.mark.asyncio
async def test_orm_update_setattr_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class LockedRow(_OrmRow):
        def __setattr__(self, key, value):
            if key == "title":
                raise RuntimeError("locked")
            super().__setattr__(key, value)

    class LockedModel(_OrmModel):
        @classmethod
        async def find(cls, key: Any):
            row = await super().find(key)
            if row is None:
                return None
            locked = LockedRow(**row.get_attributes())
            LockedRow._store = cls._store  # type: ignore[attr-defined]
            # replace in store
            for i, r in enumerate(cls._store):
                if str(r.id) == str(locked.id):
                    cls._store[i] = locked
                    break
            return locked

    LockedModel.reset()
    await LockedModel.create({"title": "A", "status": "d"})
    out = await _orm_update(LockedModel, "1", {"title": "B", "status": "p"})
    assert "id" in out


def test_list_edit_object_records_via_mount_action() -> None:
    class Obj:
        def __init__(self, id, title):  # noqa: A002
            self.id = id
            self.title = title

    class Mem(Resource):
        model = type("M", (), {})
        slug = "objs"
        records_mutable = True
        records: ClassVar[list[Any]] = [Obj(1, "A")]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

    panel = Panel.make("objs").path("/")
    host = ListRecordsHost.bind(panel=panel, resource=Mem)()
    host.mount()
    host.mountAction("edit", "1", {"data": {"title": "B"}})
    assert Mem.records[0].title == "B"
    host.mountAction("ping", "1", {})


def test_resource_orm_name_guards_and_issubclass_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class Named:
        pass

    Named.__name__ = "object"
    Named.__module__ = "app.models"

    class Res(Resource):
        model = Named  # type: ignore[misc]

    assert Res._uses_orm_model() is False

    Named2 = type("Named2", (), {})
    Named2.__name__ = "type"
    Named2.__module__ = "app.models"

    class Res2(Resource):
        model = Named2

    assert Res2._uses_orm_model() is False

    real = issubclass

    def boom(a, b):
        raise TypeError("nope")

    monkeypatch.setattr("builtins.issubclass", boom)
    class Res3(Resource):
        model = _RealOrmPost

    assert Res3._uses_orm_model() is False
    monkeypatch.setattr("builtins.issubclass", real)


def test_resource_pages_hydrate_and_width() -> None:
    class R(Resource):
        model = type("R", (), {})
        slug = "rs"
        records_mutable = True
        form_content_max_width = "screen-md"
        content_max_width = "full"

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("name"), TextInput.make("email")])

    form = R.get_form()
    data = rp._hydrate_form_state(form, SimpleNamespace(name="Ada", email="a@t", extra=1))
    assert data["name"] == "Ada"
    assert rp._resource_width_style(R, operation="edit")
    assert rp._resource_width_style(R, operation="list")
    assert rp._record_id({"id": 3}) == "3"
    assert rp._record_id(SimpleNamespace(id=4)) == "4"
    assert rp._record_id(None) == ""

    # badge / tab render
    tab = rp.Tab("x").label("X").badge(lambda: 2).badge_color("success")
    assert "2" in tab.render(active=True)


def test_nested_list_form_paths() -> None:
    panel = _panel()

    class Mutable(Resource):
        model = type("M", (), {})
        slug = "nest"
        records_mutable = True

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("title")])

    host = CreateRecordHost.bind(panel=panel, resource=Mutable)()
    host.data = {"grid": [[]]}
    host.set_property("data.grid.0.0", "cell")
    assert host.data["grid"][0][0] == "cell"
    host.data = {"grid": ["x"]}
    host.set_property("data.grid.0.nested", "y")
    # coerce index slot to dict
    assert isinstance(host.data["grid"][0], dict)


def test_list_edit_setattr_failure_and_view_memory_delete() -> None:
    class Obj:
        def __init__(self, id, title):  # noqa: A002
            self.id = id
            self.title = title

        def __setattr__(self, key, value):
            if key == "title" and value == "fail":
                raise RuntimeError("x")
            super().__setattr__(key, value)

    class Mem(Resource):
        model = type("M", (), {})
        slug = "failobjs"
        records_mutable = True
        records: ClassVar[list[Any]] = [Obj(1, "A"), {"id": 2, "title": "B"}]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("title")])

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

    panel = Panel.make("fo").path("/")
    host = ListRecordsHost.bind(panel=panel, resource=Mem)()
    host.mount()
    host.mountAction("edit", "1", {"data": {"title": "fail"}})
    assert Mem.records[0].title == "A"

    view = ViewRecordHost.bind(panel=panel, resource=Mem)()
    view.record_id = "2"
    view.mount()
    view.mountAction("delete", "2", {"data": {}})
    assert all(_record_keyish(r) != "2" for r in Mem.records)


def test_is_orm_model_edges(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _is_orm_model(123) is False
    assert _is_orm_model(object) is False

    class Named:
        pass

    Named.__name__ = "object"
    Named.__module__ = "app.m"
    assert _is_orm_model(Named) is False

    def boom(a, b):
        raise TypeError("x")

    monkeypatch.setattr("builtins.issubclass", boom)
    assert _is_orm_model(_RealOrmPost) is False


def test_form_host_render_with_factory() -> None:
    class Bound(FormHost):
        pass

    Bound._form_factory = staticmethod(lambda: Form.make("f").schema([TextInput.make("n")]))
    Bound._title = "Demo"
    host = Bound()
    host.data = {"n": "x"}
    html = host.render()
    assert "Demo" in html
    assert "or-form" in html

    empty = FormHost()
    assert "No form" in empty.render()


def test_page_header_permission_denial(monkeypatch: pytest.MonkeyPatch) -> None:
    class User:
        def has_permission(self, *a, **k):
            return False

        def can(self, *a, **k):
            return False

    class R(Resource):
        model = type("R", (), {})
        slug = "perm"
        records_mutable = True

        @classmethod
        def can_update(cls, user, record=None):
            return False

        @classmethod
        def can_delete(cls, user, record=None):
            return False

        @classmethod
        def can_view(cls, user, record=None):
            return False

    monkeypatch.setattr(rp, "_auth_user", lambda: User())
    assert rp._page_header_actions(R, "view", {"id": 1}) == ""
    assert rp._page_header_actions(R, "edit", {"id": 1}) == ""


def test_as_record_dict_without_id_attr() -> None:
    class NoId:
        def __init__(self) -> None:
            self.title = "t"

    assert _as_record_dict(NoId()) == {"title": "t"}


def test_list_render_with_tabs_and_snake_slug() -> None:
    class Tabbed(Resource):
        model = type("T", (), {})
        slug = None
        records_mutable = True
        records: ClassVar[list[dict[str, Any]]] = [{"id": 1, "title": "A"}]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def get_tabs(cls):
            return [rp.Tab("all").label("All")]

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")])

    # Force slug from class name with internal capitals
    class MyHTTPItemResource(Resource):
        model = type("X", (), {})

    assert "_" in MyHTTPItemResource.get_slug()

    panel = Panel.make("tabs").path("/")
    host = ListRecordsHost.bind(panel=panel, resource=Tabbed)()
    host.mount()
    html = host.render()
    assert "All" in html or "or-list-tab" in html


@pytest.mark.asyncio
async def test_embed_async_lazy_and_sync_mount() -> None:
    host = ListRecordsHost.bind(panel=_panel(), resource=_SeedResource)()
    host.lazy = True  # type: ignore[attr-defined]
    html = await _embed_async(host)
    assert isinstance(html, str)

    host2 = ListRecordsHost.bind(panel=_panel(), resource=_SeedResource)()
    host2.mount = lambda **k: None  # type: ignore[method-assign]
    host2.booted = lambda: None  # type: ignore[method-assign]
    html2 = await _embed_async(host2)
    assert isinstance(html2, str)


def test_auth_user_and_allowed_typeerror(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "almasix.orbit.panels.routing._current_user",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")),
    )
    assert rp._auth_user() is None

    class User:
        pass

    class R(Resource):
        model = type("R", (), {})
        slug = "te"
        records_mutable = True

        @classmethod
        def can_update(cls, user):  # only user — triggers TypeError then retry
            return True

        @classmethod
        def can_view(cls, user):
            return True

        @classmethod
        def can_delete(cls, user):
            return False

    monkeypatch.setattr(rp, "_auth_user", lambda: User())
    html = rp._page_header_actions(R, "view", {"id": 1})
    assert "edit" in html

    class Legacy:
        records_mutable = True

        @classmethod
        def can_update(cls, user, record=None):
            return True

        @classmethod
        def can_delete(cls, user, record=None):
            return True

        @classmethod
        def can_view(cls, user, record=None):
            return True

        @classmethod
        def page_url(cls, page, record=None):
            return f"/{page}"

    assert "edit" in rp._page_header_actions(Legacy, "view", {"id": 1})


def test_infolist_skips_nameless_fields() -> None:
    from almasix.orbit.infolists.infolist import Infolist

    class R(Resource):
        model = type("R", (), {})

        @classmethod
        def form(cls, form: Form) -> Form:
            blank = TextInput.make("")
            blank._name = ""  # type: ignore[attr-defined]
            return form.schema([blank, TextInput.make("title")])

        @classmethod
        def infolist(cls, infolist: Infolist) -> Infolist:
            return infolist

    info = R.get_infolist()
    names = [c.get_name() for c in info.get_components()]
    assert "title" in names


def test_tiny_coverage_edges() -> None:
    assert _resource_records(type("NoRec", (), {})) == []
    _save_resource_records(type("NoRec", (), {}), [{"id": 1}])
    assert rp._resource_is_mutable(SimpleNamespace(records_mutable=True)) is True
    assert rp._hydrate_form_state(Form.make("f"), None) == {}

    blank = TextInput.make("")
    blank._name = ""  # type: ignore[attr-defined]
    blank._state_path = ""  # type: ignore[attr-defined]
    form2 = Form.make("f2").schema([blank, TextInput.make("name")])
    hydrated = rp._hydrate_form_state(form2, {"name": "Ada", "extra": 1})
    assert hydrated["name"] == "Ada"
    assert hydrated["extra"] == 1

    panel = _panel()

    class Mutable(Resource):
        model = type("M", (), {})
        slug = "tiny"
        records_mutable = True

        @classmethod
        def form(cls, form: Form) -> Form:
            return form.schema([TextInput.make("title")])

    host = CreateRecordHost.bind(panel=panel, resource=Mutable)()
    host.data = {"links": [{"a": 1}]}
    host.moveRepeaterItem("links", 0, 9)  # out of range
    host.addRepeaterItem("")
    host.set_property("data.links.0", {"a": 2})
    # list-index path: ensure digit parent coerces
    host.data = {"rows": []}
    host.set_property("data.rows.0.name", "x")
    assert host.data["rows"][0]["name"] == "x"

    # Exercise Decimal / Enum import failure branches in _jsonable_value.
    import sys
    import types

    real_dec = sys.modules.get("decimal")
    real_enum = sys.modules.get("enum")
    sys.modules["decimal"] = types.ModuleType("decimal")
    sys.modules["enum"] = types.ModuleType("enum")
    try:
        assert isinstance(_jsonable_value(object()), str)
    finally:
        if real_dec is not None:
            sys.modules["decimal"] = real_dec
        else:
            sys.modules.pop("decimal", None)
        if real_enum is not None:
            sys.modules["enum"] = real_enum
        else:
            sys.modules.pop("enum", None)
