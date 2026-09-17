"""Interactive Orbit UI demo — browse forms, tables, shell, and login live.

Run from repo root::

    .venv/bin/python -m demo

Then open http://127.0.0.1:8765/
"""

from __future__ import annotations

from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.routing import Route

from almasix.orbit.actions.action import CreateAction, DeleteAction, EditAction
from almasix.orbit.forms.components import (
    Block,
    Builder,
    Checkbox,
    FileUpload,
    Repeater,
    RichEditor,
    Select,
    TextInput,
    Textarea,
    Toggle,
)
from almasix.orbit.forms.form import Form
from almasix.orbit.panels.auth import Login
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.schemas.layouts import Callout, EmptyState, Flex, Section
from almasix.orbit.schemas.primes import Text
from almasix.orbit.tables.columns import TextColumn
from almasix.orbit.tables.table import Table

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
CSS = REPO / "packages/panels/src/almasix/orbit/resources/css/orbit.css"
JS = REPO / "packages/panels/src/almasix/orbit/resources/js/orbit.js"

NAV = [
    ("/", "Dashboard"),
    ("/forms", "Forms"),
    ("/tables", "Tables"),
    ("/schemas", "Schemas"),
    ("/login", "Login"),
]


class PostResource(Resource):
    model = type("Post", (), {"id": 1, "title": "Hello"})
    navigation_label = "Posts"
    navigation_group = "Content"
    navigation_icon = "heroicon-o-pencil-square"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title").required()])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title").searchable()])


class AuthorResource(Resource):
    model = type("Author", (), {"id": 1, "name": "Ada"})
    navigation_label = "Authors"
    navigation_group = "Content"
    navigation_icon = "heroicon-o-user-group"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("name").required()])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("name").searchable()])


def make_panel() -> Panel:
    return (
        Panel.make("demo")
        .path("demo")
        .brand_name("Orbit Demo")
        .primary("#f1511b")
        .resources([PostResource, AuthorResource])
        .navigation_layout("sidebar_topbar")
        .sidebar_collapsible()
        .login()
    )


PANEL = make_panel()


def theme_from(request: Request) -> str:
    q = request.query_params.get("theme")
    if q in ("light", "dark"):
        return q
    return request.cookies.get("orbit_demo_theme", "light")


def wrap_shell(request: Request, content: str, *, active_path: str, title: str) -> HTMLResponse:
    theme = theme_from(request)
    shell = PANEL.render_shell(content, active_path=active_path)
    # Inject theme + floating demo chrome without forking render_shell.
    inject = f"""
<script>
(() => {{
  const theme = {theme!r};
  document.documentElement.setAttribute('data-theme', theme);
  document.documentElement.classList.toggle('dark', theme === 'dark');
  document.body.classList.toggle('dark', theme === 'dark');
  document.body.classList.add('or-body');
}})();
</script>
<style>
  .or-demo-bar {{
    position: fixed; z-index: 60; right: 1rem; bottom: 1rem;
    display: flex; gap: 0.5rem; align-items: center;
    padding: 0.55rem 0.75rem; border-radius: 999px;
    background: var(--or-cream); border: 1px solid var(--or-line);
    box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    font: 600 0.8rem var(--or-font);
  }}
  .or-demo-bar a, .or-demo-bar button {{
    appearance: none; border: 0; background: transparent; cursor: pointer;
    color: var(--or-ink); text-decoration: none; padding: 0.25rem 0.45rem;
    border-radius: 999px;
  }}
  .or-demo-bar a:hover, .or-demo-bar button:hover {{ background: var(--or-paper-deep); }}
  .or-demo-bar .is-active {{ background: color-mix(in srgb, var(--or-primary) 16%, transparent); color: var(--or-primary-deep); }}
  html[data-theme="dark"] .or-demo-bar .is-active {{ color: var(--or-primary-soft); }}
</style>
<nav class="or-demo-bar" aria-label="Demo controls">
  {"".join(
      f'<a href="{href}?theme={theme}" class="{"is-active" if request.url.path.rstrip("/") == href.rstrip("/") or (href == "/" and request.url.path == "/") else ""}">{label}</a>'
      for href, label in NAV
  )}
  <button type="button" id="or-demo-theme" data-theme="{theme}">
    {"Dark" if theme == "light" else "Light"} mode
  </button>
</nav>
<script>
document.getElementById('or-demo-theme')?.addEventListener('click', () => {{
  const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.cookie = 'orbit_demo_theme=' + next + ';path=/;max-age=31536000';
  const url = new URL(window.location.href);
  url.searchParams.set('theme', next);
  window.location.href = url.toString();
}});
</script>
"""
    # Put body class + theme early: rewrite opening body tag.
    html = shell.replace("<body class=\"or-body\">", f'<body class="or-body" data-demo-page="{title}">', 1)
    if 'class="or-body"' not in html:
        html = html.replace("<body>", f'<body class="or-body" data-demo-page="{title}">', 1)
    html = html.replace("</body>", inject + "</body>", 1)
    response = HTMLResponse(html)
    response.set_cookie("orbit_demo_theme", theme, max_age=31536000, path="/")
    return response


def forms_html() -> str:
    form = (
        Form.make()
        .schema(
            [
                Callout.make().info().label("Tip").description("Edit these fields — Alpine + Orbit CSS are live."),
                Section.make("basics")
                .heading("Basics")
                .schema(
                    [
                        Flex.make()
                        .from_breakpoint("md")
                        .schema(
                            [
                                TextInput.make("name").required().label("Name").prefix("Dr."),
                                Select.make("role")
                                .options({"a": "Admin", "e": "Editor", "v": "Viewer"})
                                .label("Role")
                                .searchable(),
                            ]
                        ),
                        Textarea.make("bio").label("Bio").rows(3),
                        Toggle.make("active").label("Active"),
                        Checkbox.make("terms").label("Accept terms"),
                    ]
                ),
                FileUpload.make("avatar").image().label("Avatar"),
                RichEditor.make("body").label("Body"),
                Repeater.make("links")
                .schema([TextInput.make("url").label("URL")])
                .default_items(1)
                .label("Links"),
                Builder.make("blocks")
                .blocks(
                    [
                        Block.make("hero")
                        .label("Hero")
                        .schema([TextInput.make("heading").label("Heading")])
                    ]
                )
                .label("Blocks"),
            ]
        )
        .fill(
            {
                "name": "Ada",
                "role": "a",
                "bio": "Editor at Orbit.",
                "active": True,
                "body": "<p>Hello from Orbit.</p>",
                "links": [{"url": "https://orbit.almasix.com"}],
                "blocks": [{"type": "hero", "heading": "Welcome"}],
            }
        )
    )
    return f'<h1 class="or-page-title">Forms</h1>{form.render()}'


def tables_html() -> str:
    table = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").label("Title").sortable().searchable(),
                TextColumn.make("amount").label("Amount").money("USD"),
                TextColumn.make("status").label("Status").badge(),
            ]
        )
        .records(
            [
                {"title": "Ada", "amount": 12, "status": "Published"},
                {"title": "Bob", "amount": 8, "status": "Draft"},
                {"title": "Chi", "amount": 24, "status": "Archived"},
            ]
        )
        .striped()
        .actions(
            [
                EditAction.make().url(lambda record, **_: f"/forms?edit={record['title']}"),
                DeleteAction.make().requires_confirmation(),
            ]
        )
        .header_actions([CreateAction.make().url("/forms")])
    )
    return f'<h1 class="or-page-title">Tables</h1>{table.render()}'


def schemas_html() -> str:
    bits = [
        Callout.make().info().label("Tip").description("Schema layouts and primes.").render(),
        Callout.make().warning().label("Watch").description("Confirmation modals use Alpine.").render(),
        EmptyState.make().heading("No drafts").description("Create one when you are ready.").render(),
        Text.make().content("Published").badge().color("success").render(),
        Text.make().content("Draft").badge().color("warning").render(),
    ]
    return f'<h1 class="or-page-title">Schemas</h1><div class="or-schema or-schema-cols-1">{"".join(bits)}</div>'


def dashboard_html() -> str:
    return (
        '<h1 class="or-page-title">Dashboard</h1>'
        '<p style="color:var(--or-muted);max-width:36rem;margin:0 0 1.25rem">'
        "Live Orbit chrome for UI review. Use the bottom bar to switch pages and theme. "
        "Tell me what feels off — spacing, contrast, white vs cream, controls — and we iterate.</p>"
        + Callout.make()
        .success()
        .label("Ready")
        .description("Light theme uses a white canvas. Toggle dark from the demo bar.")
        .render()
        + tables_html().replace('<h1 class="or-page-title">Tables</h1>', '<h2 class="or-section-title" style="margin:1.5rem 0 0.75rem">Recent posts</h2>', 1)
    )


async def page_dashboard(request: Request) -> HTMLResponse:
    return wrap_shell(request, dashboard_html(), active_path="/demo/posts", title="Dashboard")


async def page_forms(request: Request) -> HTMLResponse:
    return wrap_shell(request, forms_html(), active_path="/demo/posts", title="Forms")


async def page_tables(request: Request) -> HTMLResponse:
    return wrap_shell(request, tables_html(), active_path="/demo/posts", title="Tables")


async def page_schemas(request: Request) -> HTMLResponse:
    return wrap_shell(request, schemas_html(), active_path="/demo/authors", title="Schemas")


async def page_login(request: Request) -> HTMLResponse:
    theme = theme_from(request)
    # Login as a focused auth page (still with assets + theme).
    body = Login.render()
    html = f"""<!DOCTYPE html>
<html lang="en" data-theme="{theme}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sign in — Orbit Demo</title>
  <link rel="stylesheet" href="/vendor/orbit/orbit.css" />
  <style>:root {{ --or-font: 'Outfit', ui-sans-serif, system-ui, sans-serif; --or-primary: #f1511b; }}</style>
</head>
<body class="or-body{" dark" if theme == "dark" else ""}">
  <main style="min-height:100vh;display:grid;place-items:center;padding:2rem">
    <div style="width:min(24rem,100%)">{body}</div>
  </main>
  <nav class="or-demo-bar" aria-label="Demo controls" style="position:fixed;z-index:60;right:1rem;bottom:1rem;display:flex;gap:.5rem;padding:.55rem .75rem;border-radius:999px;background:var(--or-cream);border:1px solid var(--or-line);box-shadow:0 10px 30px rgba(0,0,0,.12);font:600 .8rem var(--or-font)">
    <a href="/?theme={theme}" style="color:var(--or-ink);text-decoration:none">← Demo</a>
    <a href="/login?theme={"dark" if theme == "light" else "light"}" style="color:var(--or-ink);text-decoration:none">{"Dark" if theme == "light" else "Light"} mode</a>
  </nav>
  <script src="/vendor/orbit/orbit.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</body>
</html>"""
    response = HTMLResponse(html)
    response.set_cookie("orbit_demo_theme", theme, max_age=31536000, path="/")
    return response


async def asset_css(_: Request) -> Response:
    return Response(CSS.read_text(encoding="utf-8"), media_type="text/css")


async def asset_js(_: Request) -> Response:
    return Response(JS.read_text(encoding="utf-8"), media_type="application/javascript")


app = Starlette(
    routes=[
        Route("/", page_dashboard),
        Route("/forms", page_forms),
        Route("/tables", page_tables),
        Route("/schemas", page_schemas),
        Route("/login", page_login),
        Route("/vendor/orbit/orbit.css", asset_css),
        Route("/vendor/orbit/orbit.js", asset_js),
    ]
)


def main() -> None:
    import os

    import uvicorn

    reload = os.environ.get("ORBIT_DEMO_RELOAD", "").lower() in {"1", "true", "yes"}
    print("Orbit demo → http://127.0.0.1:8765/")
    print("Toggle light/dark from the floating bar. Feedback welcome.")
    if reload:
        print("Reload enabled (ORBIT_DEMO_RELOAD=1).")
    uvicorn.run(
        "demo.app:app",
        host="127.0.0.1",
        port=8765,
        reload=reload,
        reload_dirs=(
            [
                str(ROOT),
                str(REPO / "packages/panels/src/almasix/orbit/resources"),
                str(REPO / "packages/forms/src"),
                str(REPO / "packages/tables/src"),
                str(REPO / "packages/schemas/src"),
                str(REPO / "packages/panels/src/almasix/orbit/panels"),
            ]
            if reload
            else None
        ),
    )


if __name__ == "__main__":
    main()
