#!/usr/bin/env python3
"""Build a static HTML gallery from Orbit render() output for screenshot capture.

Shot IDs use ``{section}/{name}`` and become files under
``docs/public/examples/{light|dark}/{section}/{name}.png``.
"""

from __future__ import annotations

from pathlib import Path

from almasix.orbit.actions.action import CreateAction, EditAction
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

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT.parent / "packages/panels/src/almasix/orbit/resources/css/orbit.css").read_text(
    encoding="utf-8"
)
OUT = ROOT / "public" / "examples" / "gallery.html"

# Canonical shot registry — keep capture scripts & docs in sync with these IDs.
SHOTS: list[tuple[str, str]] = [
    ("forms/overview", "Forms overview"),
    ("forms/text-input", "Text input"),
    ("forms/select", "Select"),
    ("tables/overview", "Tables overview"),
    ("schemas/callout", "Callout"),
    ("schemas/empty-state", "Empty state"),
    ("schemas/primes-text", "Text prime"),
    ("panels/shell", "Panel shell"),
    ("users/login", "Login"),
]


class DemoResource(Resource):
    model = type("Post", (), {"id": 1, "title": "Hello"})
    navigation_label = "Posts"
    navigation_group = "Content"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title").required()])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([TextColumn.make("title").searchable()])


def shot(shot_id: str, label: str, html: str) -> str:
    """One capturable frame. Title is outside the shot so PNGs stay clean."""
    return (
        f'<section class="gallery-section" data-section="{shot_id.split("/", 1)[0]}">'
        f'<p class="gallery-label">{label} <code>{shot_id}</code></p>'
        f'<div class="or-shot" data-shot="{shot_id}">{html}</div>'
        f"</section>"
    )


def shell_fragment(panel: Panel, content: str, *, active_path: str | None = None) -> str:
    """Panel chrome without full HTML document, scripts, or action modal host.

    Nesting a full ``render_shell()`` document inside the gallery loads Alpine from
    CDN while ``orbit.js`` 404s — the confirm modal then paints open over every shot.
    """
    ctx = panel.menu_layout_context(active_path=active_path)
    sidebar = panel._render_sidebar(ctx, panel._sidebar_collapsible)
    topbar = panel._render_topbar(ctx)
    app_class = "or-app"
    if ctx.layout == "sidebar_topbar":
        app_class += " or-app-split"
    if ctx.layout == "top":
        app_class += " or-app-top"
    return (
        f'<div class="{app_class} or-shot-shell" x-data="{{ sidebarOpen: true }}">'
        f"{sidebar}"
        f'<div class="or-main">{topbar}<main class="or-content">{content}</main></div>'
        f"</div>"
    )


def build() -> str:
    form_overview = (
        Form.make()
        .schema(
            [
                Callout.make().info().label("Tip").description("Fill these fields"),
                Section.make("basics")
                .heading("Basics")
                .schema(
                    [
                        Flex.make()
                        .from_breakpoint("md")
                        .schema(
                            [
                                TextInput.make("name")
                                .required()
                                .label("Name")
                                .default("Ada")
                                .prefix("Dr."),
                                Select.make("role")
                                .options({"a": "Admin", "e": "Editor"})
                                .label("Role")
                                .default("a"),
                            ]
                        ),
                        Textarea.make("bio").label("Bio").rows(3),
                        Toggle.make("active").label("Active").default(True),
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
    )
    form_state = {
        "name": "Ada",
        "role": "a",
        "bio": "Editor at Orbit.",
        "active": True,
        "body": "<p>Hello from Orbit.</p>",
        "links": [{"url": "https://orbit.almasix.com"}],
        "blocks": [{"type": "hero", "heading": "Welcome"}],
    }
    form_overview.fill(form_state)

    text_input = (
        TextInput.make("email")
        .email()
        .label("Email")
        .placeholder("you@acme.test")
        .helper_text("We never share this.")
        .required()
        .render("ada@orbit.test")
    )
    select = (
        Select.make("status")
        .label("Status")
        .options({"draft": "Draft", "published": "Published", "archived": "Archived"})
        .searchable()
        .render("published")
    )

    table = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").label("Title").sortable(),
                TextColumn.make("amount").label("Amount").money("USD"),
            ]
        )
        .records([{"title": "Ada", "amount": 12}, {"title": "Bob", "amount": 8}])
        .striped()
        # URL actions only — no confirm modal chrome in docs shots.
        .actions([EditAction.make().url(lambda record, **_: f"/edit/{record['title']}")])
        .header_actions([CreateAction.make().url("/create")])
    )

    panel = (
        Panel.make("admin")
        .brand_name("Orbit")
        .resources([DemoResource])
        .navigation_layout("sidebar_topbar")
        .sidebar_collapsible()
    )
    shell = shell_fragment(
        panel,
        table.render()
        + EmptyState.make().heading("No drafts").description("Create one when you are ready.").render(),
        active_path="/post",
    )

    parts = [
        shot("forms/overview", "Forms overview", form_overview.render()),
        shot("forms/text-input", "Text input", text_input),
        shot("forms/select", "Select", select),
        shot("tables/overview", "Tables overview", table.render()),
        shot(
            "schemas/callout",
            "Callout",
            Callout.make().info().label("Tip").description("Fill these fields").render(),
        ),
        shot(
            "schemas/empty-state",
            "Empty state",
            EmptyState.make().heading("No drafts").description("Create one when you are ready.").render(),
        ),
        shot(
            "schemas/primes-text",
            "Text prime",
            Text.make().content("Published").badge().color("success").render(),
        ),
        shot("panels/shell", "Panel shell", shell),
        shot("users/login", "Login", Login.render()),
    ]

    shot_list = "\n".join(f"  - {sid}" for sid, _ in SHOTS)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8" />
<title>Orbit examples gallery</title>
<style>
{CSS}
/* Gallery chrome — not part of product CSS */
[x-cloak] {{ display: none !important; }}
.or-action-modal-host,
.or-modal-backdrop,
.or-modal {{ display: none !important; }} /* never capture confirm overlays */
html, body {{
  margin: 0;
  font-family: var(--or-font);
  background: #ebe6df;
  color: var(--or-ink);
}}
body.dark {{
  background: #0f0e0d;
  color: #f3efe9;
}}
.gallery-header {{
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem 0.5rem;
}}
.gallery-header h1 {{ margin: 0 0 0.35rem; font-size: 1.5rem; }}
.gallery-header p {{ margin: 0; color: var(--or-muted); font-size: 0.95rem; }}
.gallery-header code {{ font-size: 0.85em; }}
.gallery-section {{
  max-width: 960px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem 2rem;
}}
.gallery-label {{
  margin: 0 0 0.65rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--or-muted);
  letter-spacing: 0.02em;
}}
.gallery-label code {{
  font-weight: 500;
  opacity: 0.85;
}}
.or-shot {{
  background: var(--or-cream, #fffaf6);
  border: 1px solid var(--or-line, #e5e2dc);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 10px 30px rgba(28, 20, 17, 0.06);
  overflow: hidden;
}}
body.dark .or-shot {{
  background: #1a1715;
  border-color: #2e2926;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}}
.or-shot-shell {{
  min-height: 420px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--or-line);
}}
.or-shot .or-app {{ min-height: 420px; }}
</style>
</head>
<body>
<header class="gallery-header">
  <h1>Orbit screenshot gallery</h1>
  <p>Shots use ids <code>section/name</code> → <code>examples/{{light|dark}}/section/name.png</code></p>
  <p><code>{shot_list}</code></p>
</header>
{"".join(parts)}
</body>
</html>
"""


def list_shot_ids() -> list[str]:
    return [sid for sid, _ in SHOTS]


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = build()
    # Sanity: never ship a gallery that still embeds confirm modal chrome visibly
    if "or-action-modal-host" in html and "display: none !important" not in html:
        raise SystemExit("Gallery must hide action modal host")
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT}")
    print("Shots:")
    for sid in list_shot_ids():
        print(f"  {sid}")
