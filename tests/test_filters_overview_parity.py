"""Filament-parity coverage for table filters overview."""

from __future__ import annotations

from almasix.orbit.panels.conduit.hosts import ListRecordsHost
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.tables import (
    Filter,
    FilterGroup,
    SelectFilter,
    Table,
    TernaryFilter,
    TextColumn,
    TrashedFilter,
    flatten_filters,
)


def test_boolean_filter_checkbox_and_toggle_chrome() -> None:
    rows = [
        {"id": 1, "title": "A", "featured": True},
        {"id": 2, "title": "B", "featured": False},
    ]
    checkbox = (
        Filter.make("featured")
        .label("Featured")
        .query(lambda q, value: [r for r in q if r.get("featured")])
    )
    assert checkbox.is_boolean_filter()
    assert [r["id"] for r in checkbox.apply(rows, True)] == [1]
    assert checkbox.apply(rows, False) == rows

    table = (
        Table.make()
        .columns([TextColumn.make("title")])
        .filters([checkbox.toggle()])
        .filter_state({"featured": True})
        .records(rows)
    )
    html = table.render()
    assert 'class="or-toggle or-filter-check"' in html
    assert "or-table-filter-boolean" in html
    assert "Featured" in html
    assert "or-filter-chip" in html
    assert "Yes" in html


def test_select_filter_multiple_and_placeholder() -> None:
    rows = [
        {"id": 1, "status": "draft"},
        {"id": 2, "status": "published"},
        {"id": 3, "status": "review"},
    ]
    filt = (
        SelectFilter.make("status")
        .multiple()
        .selectable_placeholder(False)
        .options({"draft": "Draft", "published": "Published", "review": "Review"})
    )
    assert filt.is_multiple()
    assert not filt.has_selectable_placeholder()
    assert [r["id"] for r in filt.apply(rows, ["draft", "review"])] == [1, 3]

    html = (
        Table.make()
        .columns([TextColumn.make("status")])
        .filters([filt])
        .filter_state({"status": ["draft", "review"]})
        .records(rows)
        .render()
    )
    assert " multiple" in html
    assert '<option value="">All</option>' not in html
    assert "Draft, Review" in html or ("Draft" in html and "Review" in html)


def test_ternary_labels_nullable_and_queries() -> None:
    rows = [
        {"id": 1, "featured": True},
        {"id": 2, "featured": False},
        {"id": 3, "featured": None},
    ]
    filt = (
        TernaryFilter.make("featured")
        .true_label("Only featured")
        .false_label("Not featured")
        .placeholder("Any")
        .nullable()
    )
    opts = filt.get_options()
    assert opts[""] == "Any"
    assert opts["1"] == "Only featured"
    assert opts["0"] == "Not featured"
    assert [r["id"] for r in filt.apply(rows, "1")] == [1]
    assert [r["id"] for r in filt.apply(rows, "0")] == [2, 3]

    custom = TernaryFilter.make("featured").queries(
        true=lambda q, value: [r for r in q if r["id"] == 1],
        false=lambda q, value: [r for r in q if r["id"] == 2],
        blank=lambda q, value: list(q),
    )
    assert [r["id"] for r in custom.apply(rows, "1")] == [1]
    assert [r["id"] for r in custom.apply(rows, "0")] == [2]
    assert len(custom.apply(rows, "")) == 3


def test_filter_group_flattens_for_apply_and_renders_section() -> None:
    group = FilterGroup.make("visibility").label("Visibility").filters(
        [
            SelectFilter.make("status").options({"draft": "Draft", "published": "Published"}),
            TernaryFilter.make("featured"),
        ]
    )
    flat = flatten_filters([group])
    assert [f.get_name() for f in flat] == ["status", "featured"]

    table = (
        Table.make()
        .columns([TextColumn.make("title")])
        .filters([group])
        .filter_state({"status": "published", "featured": "1"})
        .records(
            [
                {"title": "A", "status": "published", "featured": True},
                {"title": "B", "status": "draft", "featured": True},
                {"title": "C", "status": "published", "featured": False},
            ]
        )
    )
    assert [r["title"] for r in table.get_all_filtered_records()] == ["A"]
    html = table.render()
    assert "or-filter-group" in html
    assert "Visibility" in html
    assert 'data-filter="status"' in html
    assert 'data-filter="featured"' in html


def test_indicate_using_and_hidden_indicators() -> None:
    filt = (
        SelectFilter.make("status")
        .options({"draft": "Draft", "published": "Published"})
        .indicate_using(lambda state, **_: f"is {state}" if state else None)
    )
    table = (
        Table.make()
        .columns([TextColumn.make("title")])
        .filters([filt])
        .filter_state({"status": "draft"})
        .records([{"title": "A", "status": "draft"}])
    )
    html = table.render()
    assert "is draft" in html

    hidden = table.hidden_filter_indicators()
    assert "or-filter-chip" not in hidden.render()

    silent = SelectFilter.make("status").options({"draft": "Draft"}).indicate(False)
    assert silent.resolve_indicator("draft") is None


def test_default_filter_state_and_host_reset() -> None:
    class _Posts(Resource):
        model = type("Post", (), {})
        navigation_label = "Posts"
        slug = "posts"
        records = [
            {"id": 1, "title": "A", "status": "draft"},
            {"id": 2, "title": "B", "status": "published"},
        ]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")]).filters(
                [
                    SelectFilter.make("status")
                    .options({"draft": "Draft", "published": "Published"})
                    .default("published")
                ]
            )

    panel = Panel.make("admin").path("admin").resources([_Posts]).login(False)
    host_cls = ListRecordsHost.bind(panel=panel, resource=_Posts)
    host = host_cls()
    host.mount()
    titles = [
        r["title"] for r in host._filtered_table().get_all_filtered_records()
    ]
    assert titles == ["B"]
    assert host.table_filters.get("status") == "published"

    host.setTableFilter("status", "draft")
    host.resetTableFilters()
    assert host.table_filters == {"status": "published"}


def test_trashed_and_persist_attr() -> None:
    rows = [
        {"id": 1, "title": "Live", "deleted_at": None},
        {"id": 2, "title": "Gone", "deleted_at": "2024-01-01"},
    ]
    filt = TrashedFilter.make()
    assert [r["id"] for r in filt.apply(rows, "")] == [1]
    assert [r["id"] for r in filt.apply(rows, "only")] == [2]
    assert len(filt.apply(rows, "with")) == 2

    html = (
        Table.make("posts")
        .columns([TextColumn.make("title")])
        .filters([filt])
        .persist_filters_in_session()
        .deselect_all_records_when_filtered(False)
        .records(rows)
        .render()
    )
    assert 'data-filters-session="posts"' in html
    assert Table.make().deselect_all_records_when_filtered(False).should_deselect_all_records_when_filtered() is False


def test_filter_edge_branches() -> None:
    filt = Filter.make("x").toggle(False)
    assert filt.is_toggle() is False
    assert filt._ui is None or filt._ui != "toggle"

    # Callable options → not treated as boolean chrome
    callable_opts = Filter.make("y").options(lambda **_: {"a": "A"})
    assert callable_opts.is_boolean_filter() is False

    # SelectFilter / Ternary short-circuit when _ui cleared
    select = SelectFilter.make("s")
    select._ui = None
    assert select.is_boolean_filter() is False
    ternary = TernaryFilter.make("t")
    ternary._ui = None
    assert ternary.is_boolean_filter() is False

    assert (
        SelectFilter.make("s")
        .indicate_using(lambda **_: None)
        .resolve_indicator("x")
        is None
    )

    bare = Filter.make("bare")
    assert bare.apply([{"a": 1}], True) == [{"a": 1}]  # no query
    assert Filter.make("q").query(lambda q, v: q).apply([1], "") == [1]
    assert Filter.make("opts").options({"a": "A"}).apply([1], "a") == [1]

    multi = SelectFilter.make("tags").multiple().attribute("tags")
    rows = [
        {"id": 1, "tags": ["a", "b"]},
        {"id": 2, "tags": ["c"]},
        {"id": 3, "tags": "a"},
    ]
    assert [r["id"] for r in multi.apply(rows, ["a"])] == [1, 3]
    assert multi.apply(rows, [None, ""]) == rows  # empty wanted set

    obj = type("R", (), {"status": "draft"})()
    assert SelectFilter.make("status").apply([obj], "draft") == [obj]

    assert TernaryFilter.make("f").apply(rows, "maybe") == rows

    assert Filter.make("z").to_dict()["boolean"] is True
    assert SelectFilter.make("s").to_dict()["multiple"] is False

    # SelectFilter with custom query + empty attribute name
    custom = SelectFilter.make("s").query(lambda q, v: [r for r in q if r.get("ok")])
    assert custom.apply([{"ok": True}, {"ok": False}], "x") == [{"ok": True}]
    no_attr = SelectFilter.make(None)
    no_attr._attribute = None
    assert no_attr.apply(rows, "a") == rows

    # Ternary with custom Filter.query, blank path, missing attribute, object records
    tq = TernaryFilter.make("f").query(lambda q, v: q[:1])
    assert tq.apply(rows, "1") == rows[:1]
    assert TernaryFilter.make("f").apply(rows, "") == rows
    nameless = TernaryFilter.make(None)
    assert nameless.apply(rows, "1") == rows
    obj_f = type("R", (), {"featured": True})()
    assert [r for r in TernaryFilter.make("featured").apply([obj_f], "1")] == [obj_f]

    # TrashedFilter custom query + object records
    trashed = TrashedFilter.make().query(lambda q, v: list(q))
    assert trashed.apply(rows, "only") == rows
    gone = type("R", (), {"deleted_at": "x", "trashed": False})()
    live = type("R", (), {"deleted_at": None, "trashed": False})()
    assert TrashedFilter.make().apply([gone, live], "only") == [gone]

    from almasix.orbit.tables import QueryBuilderFilter

    class _B:
        def apply(self, query):
            return query[:1]

        def render(self, state=None, **ctx):
            return "<div class='qb'>qb</div>"

        def rules(self, value):
            self._rules = value

    qb = QueryBuilderFilter.make().builder(_B())
    assert qb.is_boolean_filter() is False
    assert qb.get_builder() is not None
    assert qb.apply(rows, ["rule"]) == rows[:1]
    assert "qb" in qb.render()
    assert QueryBuilderFilter.make().apply(rows, None) == rows
    assert QueryBuilderFilter.make().render() == ""
    assert QueryBuilderFilter.make().query(lambda q, v: q).apply(rows, 1) == rows


def test_deselect_clears_selection_when_enabled() -> None:
    class _Posts(Resource):
        model = type("Post", (), {})
        navigation_label = "Posts"
        slug = "posts"
        records = [{"id": 1, "title": "A", "status": "draft"}]

        @classmethod
        def get_records(cls):
            return list(cls.records)

        @classmethod
        def table(cls, table: Table) -> Table:
            return table.columns([TextColumn.make("title")]).filters(
                [SelectFilter.make("status").options({"draft": "Draft"})]
            )

    panel = Panel.make("admin").path("admin").resources([_Posts]).login(False)
    host_cls = ListRecordsHost.bind(panel=panel, resource=_Posts)
    host = host_cls(selected=["1"], select_all=True)
    host.mount()
    host.setTableFilter("status", "draft")
    assert host.selected == []
    assert host.select_all is False
