"""Tests for resource pages, clusters, auth, tenancy, hooks, global search."""

from __future__ import annotations

from almasix.orbit.forms.components import TextInput
from almasix.orbit.forms.form import Form
from almasix.orbit.panels.auth import AppAuthentication, Login, Profile, Register
from almasix.orbit.panels.cluster import Cluster
from almasix.orbit.panels.global_search import (
    build_result,
    render_global_search_input,
    render_global_search_results,
    search_records,
)
from almasix.orbit.panels.hooks import Plugin, clear_render_hooks, register_render_hook, render_hook
from almasix.orbit.panels.pages import CreateRecord, EditRecord, ListRecords, Tab, ViewRecord
from almasix.orbit.panels.resource import Resource
from almasix.orbit.panels.tenancy import Tenancy, Tenant
from almasix.orbit.tables.columns import TextColumn
from almasix.orbit.tables.table import Table


class Post:
    id = 1
    title = "Hello"


class PostResource(Resource):
    model = Post
    navigation_label = "Posts"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title").required()])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title")])


class PostList(ListRecords):
    resource = PostResource

    @classmethod
    def get_tabs(cls) -> list[Tab]:
        return [
            Tab("all").label("All"),
            Tab("published").label("Published").badge(2).badge_color("success").modify_query_using(
                lambda rows: [r for r in rows if r.get("published")]
            ),
        ]


class PostCreate(CreateRecord):
    resource = PostResource


class PostEdit(EditRecord):
    resource = PostResource


class PostView(ViewRecord):
    resource = PostResource


def test_list_create_edit_view_pages() -> None:
    records = [
        {"id": 1, "title": "AlphaPub", "published": True},
        {"id": 2, "title": "BetaDraft", "published": False},
    ]
    html = PostList.render(records=records, active_tab="published")
    assert "or-page-list" in html and "or-list-tabs" in html
    assert "AlphaPub" in html
    assert "BetaDraft" not in html
    assert "or-page-create" in PostCreate.render()
    assert 'wire:submit="create"' in PostCreate.render({"title": "X"})
    assert 'data-record="1"' in PostEdit.render(record={"id": 1, "title": "Hi"})
    assert "or-page-view" in PostView.render(record=Post())
    try:
        ListRecords.render()
        raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass


def test_cluster_auth_tenancy_hooks_search() -> None:
    class SettingsCluster(Cluster):
        navigation_label = "Settings"

    c = SettingsCluster.make().resources([PostResource]).breadcrumb("Settings crumb")
    assert c.get_slug() == "settings"
    assert c.path_prefix() == "/settings"
    assert c.get_breadcrumb() == "Settings crumb"

    assert "or-page-login" in Login.render()
    assert "password" in Register.render()
    assert "or-page-profile" in Profile.render()
    mfa = AppAuthentication(brand_name="Orbit")
    assert mfa.get_id() == "app"
    assert not mfa.is_enabled(object())
    assert "code" in mfa.get_challenge_form().render()

    tenancy = (
        Tenancy()
        .tenants([Tenant(1, "Acme"), Tenant(2, "Beta")])
        .current(Tenant(1, "Acme"))
        .scope_using(lambda q, t: [r for r in q if r.get("tenant_id") == t.id])
        .registration()
        .profile()
    )
    assert "or-tenant-switcher" in tenancy.render_switcher()
    assert tenancy.scope_query([{"tenant_id": 1}, {"tenant_id": 2}]) == [{"tenant_id": 1}]

    clear_render_hooks()
    register_render_hook("panels::topbar.end", lambda **_: "<!--hook-->")
    assert "<!--hook-->" in render_hook("panels::topbar.end")
    assert Plugin("x").get_id() == "x"
    Plugin("x").register(None)
    Plugin("x").boot(None)

    found = search_records([{"title": "Ada"}, {"title": "Bob"}], "ad", attributes=["title"])
    assert found == [{"title": "Ada"}]
    assert "or-global-search-input" in render_global_search_input()
    assert "Ada" in render_global_search_results(
        [build_result(title="Ada", url="/p/1", details={"Author": "X"})]
    )
    assert "No results" in render_global_search_results([])
