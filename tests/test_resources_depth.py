"""Resource depth: record titles, relation managers, global search, soft deletes."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, ClassVar

from almasix.orbit.forms import Form, TextInput
from almasix.orbit.panels.conduit.hosts import (
    EditRecordHost,
    ListRecordsHost,
    ViewRecordHost,
    _load_relation_records,
    _orm_restore_id,
    _parse_relation_action,
    _relation_manager_for,
    _resource_relation_managers,
    _restore_seed_records,
)
from almasix.orbit.panels.global_search import (
    collect_global_search_results,
    render_global_search_groups,
    render_global_search_input,
)
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.relation_manager import RelationManager, _singular
from almasix.orbit.panels.resource import Resource, _singularize
from almasix.orbit.tables import Table, TextColumn
from almasix.orm import Model


class CommentsRelation(RelationManager):
    relationship = "comments"
    title = "Comments"
    description = "Replies on this post."

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("author"), TextColumn.make("body")])


class EditOnlyRelation(RelationManager):
    relationship = "revisions"
    render_on = "edit"
    is_mutable = False

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("label")])


class ArticleResource(Resource):
    model = type("Article", (), {})
    slug = "articles"
    records_mutable = True
    record_title_attribute = "title"
    global_search_attributes = ("title", "body")
    global_search_result_details = ("status", "missing")
    records: ClassVar[list[dict[str, Any]]] = []

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title")])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])

    @classmethod
    def get_relations(cls) -> list[type[Any]]:
        return [CommentsRelation, EditOnlyRelation]


def _article(**over: Any) -> dict[str, Any]:
    record = {
        "id": 1,
        "title": "Launch Orbit",
        "body": "Ship the panel",
        "status": "published",
        "comments": [{"id": 7, "author": "Ada", "body": "Nice"}],
        "revisions": [{"id": 3, "label": "v1"}],
    }
    record.update(over)
    return record


def _panel() -> Panel:
    return Panel.make("depth").path("/admin").resources([ArticleResource])


# --- labels and record titles ------------------------------------------------


def test_model_labels_default_from_slug() -> None:
    assert ArticleResource.get_model_label() == "Article"
    assert ArticleResource.get_plural_model_label() == "Articles"


def test_explicit_model_labels_win() -> None:
    class Labelled(ArticleResource):
        model_label = "Blog post"
        plural_model_label = "Blog posts"

    assert Labelled.get_model_label() == "Blog post"
    assert Labelled.get_plural_model_label() == "Blog posts"


def test_record_title_uses_attribute_then_falls_back() -> None:
    assert ArticleResource.get_record_title(_article()) == "Launch Orbit"
    assert ArticleResource.get_record_title({"id": 4, "title": ""}) == "Article #4"
    assert ArticleResource.get_record_title({}) == "Article"
    assert ArticleResource.get_record_title(None) == "Article"
    assert ArticleResource.get_record_title_attribute() == "title"


def test_record_title_reads_object_attributes() -> None:
    class Row:
        id = 9
        title = "From object"

    assert ArticleResource.get_record_title(Row()) == "From object"


def test_singularize_handles_common_endings() -> None:
    assert _singularize("stories") == "story"
    assert _singularize("boxes") == "box"
    assert _singularize("posts") == "post"
    assert _singularize("press") == "press"
    assert _singularize("media") == "media"
    assert _singular("comments") == "comment"


def test_record_title_helper_falls_back() -> None:
    from almasix.orbit.panels.pages.resource_pages import _record_title

    assert _record_title(type("Plain", (), {}), {"id": 1}, fallback="Records") == "Records"

    class Broken:
        @staticmethod
        def get_record_title(_record: Any) -> str:
            raise RuntimeError("boom")

    assert _record_title(Broken, {"id": 1}, fallback="Records") == "Records"

    class Blank:
        @staticmethod
        def get_record_title(_record: Any) -> str:
            return ""

    assert _record_title(Blank, {"id": 1}, fallback="Records") == "Records"


def test_view_and_edit_headings_use_record_title() -> None:
    panel = _panel()
    ArticleResource.records = [_article()]
    view = ViewRecordHost.bind(panel=panel, resource=ArticleResource)()
    view.record_id = "1"
    view.mount()
    html = view.render()
    assert "<h1 class=\"or-page-title\">Launch Orbit</h1>" in html

    edit = EditRecordHost.bind(panel=panel, resource=ArticleResource)()
    edit.record_id = "1"
    edit.mount()
    assert "Edit Launch Orbit" in edit.render()


def test_create_page_heading_uses_singular_label() -> None:
    from almasix.orbit.panels.pages.resource_pages import CreateRecord, _create_heading

    class Bound(CreateRecord):
        resource = ArticleResource

    assert "Create Article" in Bound.render()
    assert _create_heading(type("Plain", (), {"get_navigation_label": lambda: "Things"})) == "Things"


def test_breadcrumbs_show_record_title() -> None:
    panel = _panel()
    crumbs = panel.breadcrumbs("/admin/articles/1", record_title="Launch Orbit")
    assert crumbs[-1]["label"] == "Launch Orbit"
    edit_crumbs = panel.breadcrumbs("/admin/articles/1/edit", record_title="Launch Orbit")
    assert [c["label"] for c in edit_crumbs][-2:] == ["Launch Orbit", "Edit"]
    assert edit_crumbs[-2]["url"] == "/admin/articles/1"
    assert panel.breadcrumbs("/admin/articles/1")[-1]["label"] == "View"


def test_record_view_url_guards_short_paths() -> None:
    panel = _panel()
    assert panel._record_view_url(ArticleResource, ["articles"]) is None

    class Broken:
        @staticmethod
        def page_url(*_a: Any, **_k: Any) -> str:
            raise RuntimeError("no url")

    assert panel._record_view_url(Broken, ["articles", "1"]) is None


def test_render_shell_passes_record_title_into_breadcrumbs() -> None:
    panel = _panel()
    html = panel.render_shell(
        "<p>body</p>", active_path="/admin/articles/1", record_title="Launch Orbit"
    )
    assert "Launch Orbit" in html


# --- relation managers -------------------------------------------------------


def test_relation_manager_defaults() -> None:
    assert CommentsRelation.get_title() == "Comments"
    assert EditOnlyRelation.get_title() == "Revisions"
    assert CommentsRelation.get_description() == "Replies on this post."
    assert EditOnlyRelation.get_description() is None
    assert CommentsRelation.get_record_label() == "comment"
    assert CommentsRelation.action_name("delete") == "relation.comments.delete"
    assert CommentsRelation.get_foreign_key(ArticleResource) == "article_id"
    assert CommentsRelation.get_foreign_key() == "owner_id"
    assert CommentsRelation.get_form().get_name() == "comments_form"
    assert CommentsRelation.can_view_for_record(object(), _article()) is True
    assert CommentsRelation.can_view_for_record(None, _article()) is False


def test_relation_manager_explicit_foreign_key() -> None:
    class Keyed(CommentsRelation):
        foreign_key = "post_uuid"

    assert Keyed.get_foreign_key(ArticleResource) == "post_uuid"


def test_relation_manager_records_from_owner() -> None:
    assert CommentsRelation.get_records(None) == []
    assert CommentsRelation.get_records({"comments": None}) == []
    assert CommentsRelation.get_records({"comments": {"id": 1}}) == [{"id": 1}]

    class Owner:
        comments = [{"id": 2}]

    assert CommentsRelation.get_records(Owner()) == [{"id": 2}]


def test_relation_manager_render_includes_table_and_actions() -> None:
    html = CommentsRelation.render(_article())
    assert 'data-relation="comments"' in html
    assert "Comments" in html
    assert "Replies on this post." in html
    assert "Ada" in html
    assert "relation.comments.create" in html

    immutable = EditOnlyRelation.render({"revisions": [{"id": 3, "label": "v1"}]})
    assert "relation.revisions.create" not in immutable


def test_relation_manager_render_accepts_explicit_records() -> None:
    html = CommentsRelation.render({}, records=[{"id": 5, "author": "Grace"}])
    assert "Grace" in html


def test_view_page_renders_relations_and_edit_only_managers() -> None:
    panel = _panel()
    ArticleResource.records = [_article()]
    view = ViewRecordHost.bind(panel=panel, resource=ArticleResource)()
    view.record_id = "1"
    view.mount()
    html = view.render()
    assert 'data-relation="comments"' in html
    assert 'data-relation="revisions"' not in html
    assert view.relations["comments"][0]["author"] == "Ada"

    edit = EditRecordHost.bind(panel=panel, resource=ArticleResource)()
    edit.record_id = "1"
    edit.mount()
    edit_html = edit.render()
    assert 'data-relation="comments"' in edit_html
    assert 'data-relation="revisions"' in edit_html


def test_relation_sections_skipped_without_relations_or_record() -> None:
    from almasix.orbit.panels.pages.resource_pages import _relation_managers

    class Bare(Resource):
        slug = "bares"

    assert _relation_managers(Bare, {"id": 1}, "view") == ""
    assert _relation_managers(ArticleResource, None, "view") == ""
    assert _relation_managers(type("NoRelations", (), {}), {"id": 1}, "view") == ""


def test_relation_managers_render_without_preloaded_rows() -> None:
    from almasix.orbit.panels.pages.resource_pages import _relation_managers

    html = _relation_managers(ArticleResource, _article(), "view")
    assert 'data-relation="comments"' in html


def test_relation_manager_keeps_custom_table_actions() -> None:
    from almasix.orbit.actions import Action

    class Custom(CommentsRelation):
        relationship = "notes"

        @classmethod
        def table(cls, table: Table) -> Table:
            return (
                table.columns([TextColumn.make("body")])
                .actions([Action.make("ping")])
                .header_actions([Action.make("pong")])
            )

    table = Custom.get_table()
    assert [a.get_name() for a in table._actions] == ["ping"]
    assert [a.get_name() for a in table._header_actions] == ["pong"]


def test_relation_manager_hidden_when_authorization_denies() -> None:
    from almasix.orbit.panels.pages import resource_pages

    class Denied(CommentsRelation):
        @classmethod
        def can_view_for_record(cls, user: Any, owner: Any) -> bool:
            return False

    class Hidden(ArticleResource):
        @classmethod
        def get_relations(cls) -> list[type[Any]]:
            return [Denied]

    original = resource_pages._auth_user
    resource_pages._auth_user = lambda: object()  # type: ignore[assignment]
    try:
        assert resource_pages._relation_managers(Hidden, _article(), "view") == ""
    finally:
        resource_pages._auth_user = original  # type: ignore[assignment]


def test_relation_delete_action_removes_row() -> None:
    panel = _panel()
    ArticleResource.records = [_article()]
    view = ViewRecordHost.bind(panel=panel, resource=ArticleResource)()
    view.record_id = "1"
    view.mount()
    assert view.relations["comments"]
    view.mountAction("relation.comments.delete", "7")
    assert view.relations["comments"] == []

    edit = EditRecordHost.bind(panel=panel, resource=ArticleResource)()
    edit.record_id = "1"
    edit.mount()
    edit.mountAction("relation.comments.delete", "7")
    assert edit.relations["comments"] == []


def test_relation_create_action_is_consumed_without_error() -> None:
    panel = _panel()
    ArticleResource.records = [_article()]
    view = ViewRecordHost.bind(panel=panel, resource=ArticleResource)()
    view.record_id = "1"
    view.mount()
    assert view.mountAction("relation.comments.create") is None
    assert view.mountAction("relation.unknown.delete", "1") is None


def test_relation_helpers() -> None:
    assert _parse_relation_action("relation.comments.delete") == ("comments", "delete")
    assert _parse_relation_action("delete") is None
    assert _relation_manager_for(ArticleResource, "comments") is CommentsRelation
    assert _relation_manager_for(ArticleResource, "nope") is None

    class Broken:
        @staticmethod
        def get_relations() -> list[Any]:
            raise RuntimeError("boom")

    assert _resource_relation_managers(Broken) == []
    assert _resource_relation_managers(type("NoHook", (), {})) == []
    assert _singular("posts") == "post"


def test_relations_not_loaded_without_owner() -> None:
    panel = _panel()
    view = ViewRecordHost.bind(panel=panel, resource=ArticleResource)()
    assert view.load_relations({}) is None
    assert view.relations == {}


async def test_load_relation_records_skips_blank_relationships() -> None:
    class Blank(RelationManager):
        relationship = ""

    class WithBlank(ArticleResource):
        @classmethod
        def get_relations(cls) -> list[type[Any]]:
            return [Blank, CommentsRelation]

    loaded = await _load_relation_records(WithBlank, _article())
    assert list(loaded) == ["comments"]


# --- global search -----------------------------------------------------------


def test_global_search_requires_declared_attributes() -> None:
    class Quiet(Resource):
        slug = "quiets"

    assert Quiet.is_globally_searchable() is False
    assert Quiet.get_global_search_results("a", []) == []
    assert ArticleResource.is_globally_searchable() is True
    assert ArticleResource.get_globally_searchable_attributes() == ["title", "body"]


def test_global_search_results_build_rows() -> None:
    ArticleResource._panel_path = "/admin"
    rows = ArticleResource.get_global_search_results("launch", [_article()])
    assert rows[0]["title"] == "Launch Orbit"
    assert rows[0]["url"] == "/admin/articles/1"
    assert rows[0]["details"] == {"Status": "published"}
    assert ArticleResource.get_global_search_results("   ", [_article()]) == []
    assert ArticleResource.get_global_search_results("launch", [_article()], limit=0) == []


def test_collect_global_search_results_groups_and_authorizes() -> None:
    panel = _panel()
    ArticleResource.records = [_article()]
    groups = collect_global_search_results(panel, "launch")
    assert groups[0]["label"] == "Articles"
    assert groups[0]["results"][0]["title"] == "Launch Orbit"
    assert collect_global_search_results(panel, "") == []

    class Denier:
        def can(self, *_a: Any, **_k: Any) -> bool:
            return False

    assert collect_global_search_results(panel, "launch", user=Denier()) == []


def test_collect_global_search_results_skips_non_searchable_and_uses_supplied_rows() -> None:
    class Quiet(Resource):
        slug = "quiets"

    class Empty(ArticleResource):
        slug = "empties"
        records: ClassVar[list[dict[str, Any]]] = []

    panel = Panel.make("gs").path("/admin").resources([Quiet, Empty, ArticleResource])
    groups = collect_global_search_results(
        panel, "launch", records_by_resource={ArticleResource: [_article()]}
    )
    assert [g["label"] for g in groups] == ["Articles"]


def test_global_search_group_rendering() -> None:
    html = render_global_search_groups(
        [
            {"label": "Empty", "results": []},
            {"label": "Articles", "results": [{"title": "A", "url": "/a", "details": {"S": "x"}}]},
        ]
    )
    assert "or-gs-group-label" in html
    assert "No results" not in html
    assert "No results" in render_global_search_groups([])


def test_global_search_input_variants() -> None:
    bound = render_global_search_input()
    assert 'wire:model.live.debounce.300ms="globalSearch"' in bound
    fetched = render_global_search_input(endpoint="/admin/global-search", debounce_ms=150)
    assert "/admin/global-search?search=" in fetched
    assert "150" in fetched


def test_panel_global_search_configuration() -> None:
    panel = _panel()
    assert panel.has_global_search() is True
    assert panel.global_search_url() == "/admin/global-search"
    assert "or-global-search-input" in panel.render_shell("<p>x</p>")

    panel.global_search(False)
    assert panel.has_global_search() is False
    assert "or-global-search-slot" in panel.render_shell("<p>x</p>")

    panel.global_search(True, debounce=500, placeholder="Find…", limit=3)
    assert panel._global_search_debounce_ms == 500
    assert panel._global_search_placeholder == "Find…"
    assert panel._global_search_limit == 3
    panel.global_search_debounce(200).global_search_placeholder("Go").global_search_limit(7)
    assert (panel._global_search_debounce_ms, panel._global_search_limit) == (200, 7)
    assert panel._global_search_placeholder == "Go"


def test_root_panel_global_search_url() -> None:
    panel = Panel.make("root").path("/").resources([ArticleResource])
    assert panel.global_search_url() == "/global-search"


def test_global_search_route_renders_matches() -> None:
    from almasix.orbit.panels.routing import mount_panel

    class Router:
        def __init__(self) -> None:
            self.routes: list[tuple[Any, dict[str, Any]]] = []

        def add(self, *args: Any, **kwargs: Any) -> None:
            self.routes.append((args, kwargs))

    ArticleResource.records = [_article()]
    panel = _panel().login(False)
    router = Router()
    mount_panel(router, panel)
    route = next(
        args for args, kwargs in router.routes
        if kwargs.get("name") == "depth" or "/global-search" in str(args[1])
    )
    action = route[2]
    request = SimpleNamespace(
        url=SimpleNamespace(path="/admin/global-search"),
        query_params={"search": "launch"},
    )
    body = asyncio.run(action(request))
    assert "Launch Orbit" in str(getattr(body, "body", body))


def test_global_search_route_absent_without_searchable_resources() -> None:
    from almasix.orbit.panels.routing import mount_panel

    class Quiet(Resource):
        slug = "quiets"

    class Router:
        def __init__(self) -> None:
            self.routes: list[str] = []

        def add(self, *args: Any, **kwargs: Any) -> None:
            self.routes.append(str(kwargs.get("name")))

    router = Router()
    mount_panel(router, Panel.make("quiet").path("/admin").resources([Quiet]).login(False))
    assert "orbit.quiet.global-search" not in router.routes


async def test_global_search_groups_read_orm_and_seed_records() -> None:
    from almasix.orbit.panels.routing import _global_search_groups

    _reset_orm()

    class SearchableOrm(OrmPostResource):
        slug = "orm-search"
        global_search_attributes = ("title",)

    class Quiet(Resource):
        slug = "quiet-rows"

    panel = (
        Panel.make("orm-gs")
        .path("/admin")
        .resources([Quiet, SearchableOrm, ArticleResource])
    )
    ArticleResource.records = [_article()]
    panel.global_search_limit(1)
    groups = await _global_search_groups(panel, "launch", None)
    assert sum(len(g["results"]) for g in groups) == 1


def test_query_param_reads_supported_request_shapes() -> None:
    from almasix.orbit.panels.routing import _query_param

    assert _query_param(None, "search") == ""
    assert _query_param(SimpleNamespace(), "search") == ""
    assert _query_param(SimpleNamespace(query_params=object()), "search") == ""
    assert _query_param(SimpleNamespace(query={"search": "x"}), "search") == "x"
    assert _query_param(SimpleNamespace(query_params={"search": "y"}), "search") == "y"


def test_host_record_title_reads_mounted_hosts() -> None:
    from almasix.orbit.panels.routing import _host_record_title

    panel = _panel()
    ArticleResource.records = [_article()]
    view = ViewRecordHost.bind(panel=panel, resource=ArticleResource)()
    view.record_id = "1"
    view.mount()
    assert _host_record_title(view) == "Launch Orbit"

    edit = EditRecordHost.bind(panel=panel, resource=ArticleResource)()
    edit.record_id = "1"
    edit.mount()
    assert _host_record_title(edit) == "Launch Orbit"

    assert _host_record_title(SimpleNamespace(record={}, data={})) is None
    assert _host_record_title(SimpleNamespace(record={"id": 1})) is None

    class Boom:
        record = {"id": 1}

        @staticmethod
        def get_resource() -> Any:
            raise RuntimeError("no resource")

    assert _host_record_title(Boom()) is None

    class Blank:
        record = {"id": 1}

        @staticmethod
        def get_resource() -> Any:
            return type("R", (), {"get_record_title": staticmethod(lambda _r: "")})

    assert _host_record_title(Blank()) is None


# --- soft deletes ------------------------------------------------------------


class TrashResource(Resource):
    model = type("Trash", (), {})
    slug = "trashables"
    records_mutable = True
    soft_deletes = True
    records: ClassVar[list[dict[str, Any]]] = []

    @classmethod
    def get_records(cls) -> list[dict[str, Any]]:
        return list(cls.records)

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("name")])


def test_is_trashed_public_helper() -> None:
    from almasix.orbit.tables.filters import is_trashed

    assert is_trashed({"deleted_at": "2026-01-01"}) is True
    assert is_trashed({"id": 1}) is False


def test_soft_delete_table_adds_filter_and_actions() -> None:
    table = TrashResource.get_table()
    assert [f.get_name() for f in table.flat_filters()] == ["trashed"]
    names = [a.get_name() for a in table._actions]
    assert "restore" in names and "force_delete" in names

    plain = ArticleResource.get_table()
    assert "restore" not in [a.get_name() for a in plain._actions]


def test_restore_seed_records_clears_trashed_markers() -> None:
    class Row:
        def __init__(self) -> None:
            self.id = 2
            self.deleted_at = "2026-01-01"
            self.trashed = True

    row = Row()
    restored = _restore_seed_records(
        [{"id": 1, "deleted_at": "2026-01-01", "trashed": True}, row, {"id": 3}], "1"
    )
    assert restored[0]["deleted_at"] is None and restored[0]["trashed"] is False
    assert restored[1] is row and row.deleted_at == "2026-01-01"

    restored_obj = _restore_seed_records([row], "2")
    assert restored_obj[0].deleted_at is None
    assert restored_obj[0].trashed is False


def test_list_host_restore_action_on_seed_records() -> None:
    TrashResource.records = [{"id": 1, "name": "Ada", "deleted_at": "2026-01-01"}]
    panel = Panel.make("trash").path("/admin").resources([TrashResource])
    host = ListRecordsHost.bind(panel=panel, resource=TrashResource)()
    host.mount()
    host.mountAction("restore", "1")
    assert host.records[0]["deleted_at"] is None


def test_view_host_restore_action_on_seed_records() -> None:
    TrashResource.records = [{"id": 1, "name": "Ada", "deleted_at": "2026-01-01"}]
    panel = Panel.make("trash-view").path("/admin").resources([TrashResource])
    host = ViewRecordHost.bind(panel=panel, resource=TrashResource)()
    host.record_id = "1"
    host.mount()
    host.mountAction("restore", "1")
    assert TrashResource.records[0]["deleted_at"] is None


def test_restore_blocked_on_immutable_resource() -> None:
    class Frozen(TrashResource):
        slug = "frozen"
        records_mutable = False

    panel = Panel.make("frozen").path("/admin").resources([Frozen])
    host = ViewRecordHost.bind(panel=panel, resource=Frozen)()
    host.record_id = "1"
    assert host.mountAction("restore", "1") is None


class _Row:
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


class _Query:
    def __init__(self, rows: list[_Row]) -> None:
        self._rows = rows

    async def get(self) -> list[_Row]:
        return list(self._rows)


class OrmComment(Model):
    """Real Model subclass with the query surface stubbed for tests."""

    fillable = ("body",)
    _store: ClassVar[list[_Row]] = []

    @classmethod
    def where(cls, key: str, value: Any) -> _Query:
        return _Query([r for r in cls._store if str(getattr(r, key, "")) == str(value)])

    @classmethod
    async def find(cls, key: Any) -> _Row | None:
        return next((r for r in cls._store if str(r.id) == str(key)), None)


class OrmPost(Model):
    fillable = ("title",)
    _store: ClassVar[list[_Row]] = []

    @classmethod
    async def all(cls) -> list[_Row]:
        return list(cls._store)

    @classmethod
    async def find(cls, key: Any) -> _Row | None:
        return next((r for r in cls._store if str(r.id) == str(key)), None)


class OrmCommentsRelation(RelationManager):
    relationship = "comments"
    related_model = OrmComment
    foreign_key = "post_id"

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("body")])


class OrmPostResource(Resource):
    model = OrmPost
    slug = "orm-articles"
    soft_deletes = True
    record_title_attribute = "title"

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])

    @classmethod
    def get_relations(cls) -> list[type[Any]]:
        return [OrmCommentsRelation]


def _reset_orm() -> None:
    OrmPost._store = [_Row(id=1, title="Launch", deleted_at="2026-01-01")]
    OrmComment._store = [_Row(id=5, post_id=1, body="Nice")]
    _Row._store = OrmComment._store  # type: ignore[attr-defined]


async def test_orm_relation_records_load_and_delete() -> None:
    _reset_orm()
    panel = Panel.make("orm-depth").path("/admin").resources([OrmPostResource])
    view = ViewRecordHost.bind(panel=panel, resource=OrmPostResource)()
    view.record_id = "1"
    await view.mount()
    assert view.relations["comments"][0]["body"] == "Nice"
    assert 'data-relation="comments"' in view.render()

    await view.mountAction("relation.comments.delete", "5")
    assert view.relations["comments"] == []


async def test_orm_relation_records_load_on_edit_host() -> None:
    _reset_orm()
    panel = Panel.make("orm-depth-edit").path("/admin").resources([OrmPostResource])
    edit = EditRecordHost.bind(panel=panel, resource=OrmPostResource)()
    edit.record_id = "1"
    await edit.mount()
    assert edit.relations["comments"][0]["body"] == "Nice"


async def test_orm_restore_from_list_and_view_hosts() -> None:
    _reset_orm()
    panel = Panel.make("orm-restore").path("/admin").resources([OrmPostResource])
    listing = ListRecordsHost.bind(panel=panel, resource=OrmPostResource)()
    await listing.mount()
    await listing.mountAction("restore", "1")
    assert listing.records[0]["deleted_at"] is None

    _reset_orm()
    view = ViewRecordHost.bind(panel=panel, resource=OrmPostResource)()
    view.record_id = "1"
    await view.mount()
    await view.mountAction("restore", "1")
    assert view.record["deleted_at"] is None


async def test_orm_restore_from_list_host_ignores_missing_rows() -> None:
    _reset_orm()
    panel = Panel.make("orm-restore-missing").path("/admin").resources([OrmPostResource])
    listing = ListRecordsHost.bind(panel=panel, resource=OrmPostResource)()
    await listing.mount()
    await listing.mountAction("restore", "404")
    assert listing.records[0]["title"] == "Launch"


def test_restore_seed_records_tolerates_readonly_attributes() -> None:
    class Locked:
        id = 1

        @property
        def deleted_at(self) -> str:
            return "2026-01-01"

    row = Locked()
    assert _restore_seed_records([row], "1") == [row]


async def test_orm_restore_helper_prefers_restore_method() -> None:
    calls: list[str] = []

    class Instance:
        deleted_at = "2026-01-01"

        def restore(self) -> None:
            calls.append("restore")

    class Model:
        @staticmethod
        def find(_id: Any) -> Any:
            return Instance()

    await _orm_restore_id(Model, "1")
    assert calls == ["restore"]


async def test_orm_restore_helper_falls_back_to_save() -> None:
    saved: list[str] = []

    class Instance:
        deleted_at = "2026-01-01"

        def save(self) -> None:
            saved.append("save")

    class Model:
        @staticmethod
        def find(_id: Any) -> Any:
            return Instance()

    await _orm_restore_id(Model, "1")
    assert saved == ["save"]


async def test_orm_restore_helper_handles_missing_and_readonly_records() -> None:
    class Missing:
        @staticmethod
        def find(_id: Any) -> Any:
            return None

    await _orm_restore_id(Missing, "1")

    class Frozen:
        __slots__ = ()

    class Model:
        @staticmethod
        def find(_id: Any) -> Any:
            return Frozen()

    await _orm_restore_id(Model, "1")
