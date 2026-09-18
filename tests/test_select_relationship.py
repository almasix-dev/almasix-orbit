"""Select relationship() model querying + composite option labels — full coverage."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest
from almasix.orbit.forms import Select
from almasix.orbit.forms import select_relationship as sr
from almasix.orbit.forms.select_relationship import (
    DEFAULT_OPTIONS_LIMIT,
    format_record_option_label,
    load_relationship_options,
    option_label_placeholders,
    relationship_should_ajax,
    resolve_related_model,
)


class _Artist:
    primary_key = "id"

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)


class _Rel:
    related = _Artist


class _Album:
    def artist(self) -> _Rel:
        return _Rel()


class _NeedsParent:
    def artist(self, parent: Any) -> _Rel:  # noqa: ARG002
        return _Rel()


class _BoomOwner:
    def __init__(self) -> None:
        raise RuntimeError("cannot construct")


class _BadRelOwner:
    def artist(self) -> Any:
        raise RuntimeError("rel failed")


class _FakeQuery:
    def __init__(self, rows: list[Any] | None = None, *, as_collection: bool = False) -> None:
        self._rows = rows if rows is not None else []
        self._as_collection = as_collection
        self._fail_order = False
        self._fail_limit = False

    def where_in(self, *_a: Any, **_k: Any) -> _FakeQuery:
        return self

    def where_like(self, *_a: Any, **_k: Any) -> _FakeQuery:
        return self

    def or_where_like(self, *_a: Any, **_k: Any) -> _FakeQuery:
        return self

    def order_by(self, *_a: Any, **_k: Any) -> _FakeQuery:
        if self._fail_order:
            raise RuntimeError("no order")
        return self

    def limit(self, *_a: Any, **_k: Any) -> _FakeQuery:
        if self._fail_limit:
            raise RuntimeError("no limit")
        return self

    async def get(self) -> Any:
        if self._as_collection:

            class Coll:
                def __init__(self, rows: list[Any]) -> None:
                    self._rows = rows

                def all(self) -> list[Any]:
                    return list(self._rows)

            return Coll(self._rows)
        return list(self._rows)


class _Model:
    primary_key = "id"
    _query: _FakeQuery | None = None

    @classmethod
    def query(cls) -> _FakeQuery:
        if cls._query is None:
            raise RuntimeError("no query")
        return cls._query


def test_option_label_format_placeholders_and_render() -> None:
    assert option_label_placeholders("{name} - {bio}") == ["name", "bio"]
    assert option_label_placeholders("") == []
    row = SimpleNamespace(name="Nova", bio="Producer", id=1)
    assert format_record_option_label(row, "{name} - {bio}") == "Nova - Producer"
    assert format_record_option_label({"name": "A", "bio": None}, "{name} - {bio}") == "A - "


def test_relationship_option_label_api_and_search_columns() -> None:
    sel = (
        Select.make("artist_id")
        .relationship("artist", option_label="{name} - {country}")
        .searchable()
    )
    rel = sel.get_relationship()
    assert rel is not None
    assert rel["option_label"] == "{name} - {country}"
    assert rel["title_attribute"] == "name"
    assert rel["search_columns"] == ["name", "country"]

    chained = Select.make("a").relationship("artist", "name").option_label("{name} / {bio}")
    rel2 = chained.get_relationship()
    assert rel2 is not None
    assert rel2["option_label"] == "{name} / {bio}"
    assert rel2["search_columns"] == ["name", "bio"]

    only_fmt = Select.make("b").option_label("{title} ({year})")
    rel3 = only_fmt.get_relationship()
    assert rel3 is not None
    assert rel3["title_attribute"] == "title"


def test_get_option_label_from_record_using_callback() -> None:
    sel = (
        Select.make("artist_id")
        .relationship(model=_Artist, title_attribute="name")
        .get_option_label_from_record_using(lambda r: f"{r.name} :: {getattr(r, 'bio', '')}")
    )
    rel = sel.get_relationship()
    assert rel is not None
    assert rel["get_option_label"](_Artist(name="X", bio="Y")) == "X :: Y"

    bare = Select.make("x").get_option_label_from_record_using(lambda r: "z")
    assert bare.get_relationship() is not None


def test_relationship_ajax_vs_preload() -> None:
    sel = Select.make("artist_id").relationship("artist", "name").searchable()
    rel = sel.get_relationship()
    assert rel is not None
    assert relationship_should_ajax(rel, searchable=True) is True
    assert relationship_should_ajax({**rel, "preload": True}, searchable=True) is False
    assert sel.effective_options_limit() == DEFAULT_OPTIONS_LIMIT
    html = sel.render()
    assert 'data-ajax-search="true"' in html
    assert f'data-options-limit="{DEFAULT_OPTIONS_LIMIT}"' in html
    pre = Select.make("artist_id").relationship("artist", "name", preload=True).searchable()
    assert 'data-preload="true"' in pre.render()


def test_resolve_related_model_paths() -> None:
    assert (
        resolve_related_model(relationship_name="artist", related_model=_Artist, owner_model=None)
        is _Artist
    )
    assert (
        resolve_related_model(relationship_name="artist", related_model=None, owner_model=_Album)
        is _Artist
    )
    assert (
        resolve_related_model(
            relationship_name="artist", related_model=None, owner_model=_NeedsParent
        )
        is _Artist
    )
    assert (
        resolve_related_model(relationship_name="artist", related_model=None, owner_model=_BoomOwner)
        is None
    )
    assert (
        resolve_related_model(relationship_name="nope", related_model=None, owner_model=_Album)
        is None
    )
    assert (
        resolve_related_model(relationship_name="artist", related_model=None, owner_model=_BadRelOwner)
        is None
    )
    assert resolve_related_model(relationship_name=None, related_model=None, owner_model=_Album) is None

    class _NeedsParentThenBoom:
        def artist(self, *args: Any) -> Any:
            if not args:
                raise TypeError("missing parent")
            raise RuntimeError("boom with parent")

    assert (
        resolve_related_model(
            relationship_name="artist",
            related_model=None,
            owner_model=_NeedsParentThenBoom,
        )
        is None
    )

    class _NonTypeRelated:
        def artist(self) -> Any:
            return SimpleNamespace(related="not-a-type")

    assert (
        resolve_related_model(
            relationship_name="artist",
            related_model=None,
            owner_model=_NonTypeRelated,
        )
        is None
    )


def test_record_key_and_label_helpers() -> None:
    assert sr._record_key(SimpleNamespace(id=7)) == "7"
    assert sr._record_key({"id": 9}) == "9"
    assert sr._record_key(SimpleNamespace()) is None
    assert sr._record_label(SimpleNamespace(name="A", id=1), "name") == "A"
    assert sr._record_label({"name": "B", "id": 2}, "name") == "B"
    assert (
        sr._record_label(
            SimpleNamespace(name="C", bio="D"),
            "name",
            option_label="{name} - {bio}",
        )
        == "C - D"
    )
    assert (
        sr._record_label(
            SimpleNamespace(name="E"),
            "name",
            get_option_label=lambda r: (_ for _ in ()).throw(RuntimeError("x")),
        )
        == "E"
    )
    assert sr._record_label(SimpleNamespace(id=3), "missing") == "3"
    assert sr._record_label({}, "missing") == ""


def test_accepts_search_and_run_coro() -> None:
    assert sr._accepts_search(lambda q: q) is False
    assert sr._accepts_search(lambda q, s: q) is True
    assert sr._accepts_search(object()) is False  # type: ignore[arg-type]

    async def _one() -> int:
        return 1

    assert sr._run_coro(_one()) == 1

    async def _nested() -> int:
        return sr._run_coro(_one())

    assert asyncio.run(_nested()) == 1


@pytest.mark.asyncio
async def test_fetch_rows_branches() -> None:
    rows = [_Artist(id=1, name="Nova", bio="x"), _Artist(id=2, name="Cedar", bio="y")]
    _Model._query = _FakeQuery(rows)

    got = await sr._fetch_rows(
        _Model,
        title_attribute="name",
        search=None,
        search_columns=None,
        limit=50,
        modify_query=None,
    )
    assert len(got) == 2

    # modify_query one-arg + search multi-column
    def mod(q: _FakeQuery) -> _FakeQuery:
        return q

    def mod2(q: _FakeQuery, search: str | None) -> _FakeQuery:  # noqa: ARG001
        return q

    await sr._fetch_rows(
        _Model,
        title_attribute="name",
        search="No",
        search_columns=["name", "bio"],
        limit=10,
        modify_query=mod2,
    )
    await sr._fetch_rows(
        _Model,
        title_attribute="name",
        search=None,
        search_columns=None,
        limit=10,
        modify_query=mod,
    )

    # empty keys
    empty = await sr._fetch_rows(
        _Model,
        title_attribute="name",
        search=None,
        search_columns=None,
        limit=10,
        modify_query=None,
        keys=["", None],
    )
    assert empty == []

    # keys path
    await sr._fetch_rows(
        _Model,
        title_attribute="name",
        search=None,
        search_columns=None,
        limit=10,
        modify_query=None,
        keys=[1],
    )

    # order/limit failures + collection + None get
    q = _FakeQuery(rows, as_collection=True)
    q._fail_order = True
    q._fail_limit = True
    _Model._query = q
    coll = await sr._fetch_rows(
        _Model,
        title_attribute="name",
        search=None,
        search_columns=None,
        limit=5,
        modify_query=lambda qq: None,  # ignored when returns None
    )
    assert len(coll) == 2

    class NoneGet(_FakeQuery):
        async def get(self) -> None:
            return None

    _Model._query = NoneGet([])
    assert (
        await sr._fetch_rows(
            _Model,
            title_attribute="name",
            search=None,
            search_columns=None,
            limit=5,
            modify_query=None,
        )
        == []
    )


def test_load_relationship_options_success_and_failure() -> None:
    rows = [_Artist(id=1, name="Nova", bio="Beat"), {"id": 2, "name": "Cedar", "bio": "Folk"}]
    _Model._query = _FakeQuery(rows)
    opts = load_relationship_options(
        model=_Model,
        title_attribute="name",
        option_label="{name} - {bio}",
        limit=50,
    )
    assert opts["1"] == "Nova - Beat"
    assert opts["2"] == "Cedar - Folk"

    class Boom:
        @classmethod
        def query(cls) -> Any:
            raise RuntimeError("db down")

    assert load_relationship_options(model=Boom, title_attribute="name") == {}

    # skip records without id
    _Model._query = _FakeQuery([SimpleNamespace(name="no-id")])
    assert load_relationship_options(model=_Model, title_attribute="name") == {}


def test_select_resolve_options_ajax_and_preload(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def fake_load(**kwargs: Any) -> dict[str, str]:
        calls.append(kwargs)
        return {"1": "Nova - KE"}

    import almasix.orbit.forms.select_relationship as mod

    monkeypatch.setattr(mod, "load_relationship_options", fake_load)

    sel = (
        Select.make("artist_id")
        .relationship("artist", option_label="{name} - {country}", model=_Artist)
        .searchable()
    )

    assert sel.resolve_relationship_options(None, model=_Album) == {}
    assert sel.resolve_relationship_options("1", model=_Album) == {"1": "Nova - KE"}
    assert calls[-1].get("keys") == ["1"]
    assert calls[-1].get("option_label") == "{name} - {country}"

    sel.resolve_relationship_options(None, search="No", model=_Album)
    assert calls[-1].get("search") == "No"

    # static options win
    with_static = Select.make("x").options({"a": "A"}).relationship("artist", "name", model=_Artist)
    assert with_static._relationship_options_for_render(None, model=_Album) == {}

    # preload searchable uses search path (no keys)
    pre = (
        Select.make("artist_id")
        .relationship("artist", "name", model=_Artist, preload=True)
        .searchable()
    )
    pre.resolve_relationship_options(None, model=_Album)
    assert calls[-1].get("keys") is None


def test_select_owner_model_from_resource() -> None:
    class Res:
        model = _Album

        @classmethod
        def get_model(cls) -> type:
            return _Album

    class BadRes:
        @classmethod
        def get_model(cls) -> type:
            raise RuntimeError("x")

        model = _Album

    sel = Select.make("artist_id")
    assert sel._owner_model(resource=Res) is _Album
    assert sel._owner_model(resource=BadRes) is _Album
    assert sel._owner_model(model=_Album) is _Album
    assert sel._owner_model() is None


def test_select_render_with_select_search_ctx(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sr,
        "load_relationship_options",
        lambda **k: {"1": "Hit"},
    )
    import almasix.orbit.forms.select_relationship as mod

    monkeypatch.setattr(mod, "load_relationship_options", lambda **k: {"1": "Hit"})

    sel = (
        Select.make("artist_id")
        .relationship("artist", "name", model=_Artist, preload=True)
        .searchable()
        .options_limit(10)
    )
    html = sel.render(
        None,
        model=_Album,
        select_search={"artist_id": "Hit"},
    )
    assert "Hit" in html or "data-options-limit=\"10\"" in html
    assert sel.effective_options_limit() == 10
