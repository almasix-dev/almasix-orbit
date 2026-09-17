#!/usr/bin/env python3
"""Build a static HTML gallery from Orbit render() output for screenshot capture."""

from __future__ import annotations

from pathlib import Path

from almasix.orbit.actions.action import CreateAction, DeleteAction
from almasix.orbit.actions.presets import ActionGroup, ReplicateAction
from almasix.orbit.forms.components import (
    Builder,
    Block,
    FileUpload,
    Repeater,
    RichEditor,
    Select,
    TextInput,
)
from almasix.orbit.forms.form import Form
from almasix.orbit.panels.auth import Login
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.resource import Resource
from almasix.orbit.schemas.layouts import Callout, EmptyState, Flex
from almasix.orbit.schemas.primes import Text
from almasix.orbit.tables.columns import TextColumn
from almasix.orbit.tables.summaries import Sum
from almasix.orbit.tables.table import Table

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT.parent / "packages/panels/src/almasix/orbit/resources/css/orbit.css").read_text(
    encoding="utf-8"
)
OUT = ROOT / "public" / "examples" / "gallery.html"


class DemoResource(Resource):
    model = type("Post", (), {"id": 1, "title": "Hello"})
    navigation_label = "Posts"
    navigation_group = "Content"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([TextInput.make("title").required()])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [TextColumn.make("title").searchable().summarize(Sum.make())]
        )


def section(title: str, html: str) -> str:
    return f'<section class="gallery-section" id="{title}"><h2>{title}</h2><div class="gallery-card">{html}</div></section>'


def build() -> str:
    form = (
        Form.make()
        .schema(
            [
                Callout.make().info().label("Tip").description("Fill these fields"),
                Flex.make().from_breakpoint("md").schema(
                    [
                        TextInput.make("name").required().label("Name"),
                        Select.make("role")
                        .searchable()
                        .options({"a": "Admin", "e": "Editor"})
                        .label("Role"),
                    ]
                ),
                FileUpload.make("avatar").accepted_file_types(["image/png"]).label("Avatar"),
                RichEditor.make("body").label("Body"),
                Repeater.make("links")
                .schema([TextInput.make("url")])
                .label("Links"),
                Builder.make("blocks")
                .blocks([Block.make("hero").label("Hero").schema([TextInput.make("heading")])])
                .label("Blocks"),
            ]
        )
    )
    table = (
        Table.make()
        .columns(
            [
                TextColumn.make("title").money("USD") if False else TextColumn.make("title").sortable(),
                TextColumn.make("amount").money("USD").summarize(Sum.make().attribute("amount")),
            ]
        )
        .records([{"title": "Ada", "amount": 12}, {"title": "Bob", "amount": 8}])
        .striped()
        .actions([CreateAction.make().url("/create"), DeleteAction.make()])
        .header_actions([ActionGroup.make([ReplicateAction.make(), CreateAction.make()])])
    )
    panel = (
        Panel.make("admin")
        .brand_name("Orbit")
        .resources([DemoResource])
        .navigation_layout("sidebar_topbar")
        .sidebar_collapsible()
    )
    shell = panel.render_shell(
        table.render() + EmptyState.make().heading("No drafts").description("Create one.").render(),
        active_path="/post",
    )
    parts = [
        section("form", form.render({"name": "Ada", "role": "a", "body": "<p>Hello</p>"})),
        section("table", table.render()),
        section("primes", Text.make().content("Published").badge().color("success").render()),
        section("login", Login.render()),
        section("shell", shell),
    ]
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8" />
<title>Orbit examples gallery</title>
<style>
{CSS}
body {{ font-family: Outfit, ui-sans-serif, system-ui, sans-serif; margin: 0; background: #f6f4f1; color: #1a1a1a; }}
body.dark {{ background: #121212; color: #f3f3f3; }}
.gallery-section {{ padding: 2rem; max-width: 1100px; margin: 0 auto; }}
.gallery-card {{ background: #fff; border: 1px solid #e5e2dc; border-radius: 12px; padding: 1.25rem; }}
body.dark .gallery-card {{ background: #1c1c1c; border-color: #333; }}
h2 {{ margin-top: 0; }}
</style>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
</head>
<body>
{"".join(parts)}
</body>
</html>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"Wrote {OUT}")
