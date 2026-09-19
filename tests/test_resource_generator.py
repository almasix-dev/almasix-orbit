"""Tests for Orbit resource form/table generation from DB columns."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from almasix.orbit.panels.commands import MakeOrbitResourceCommand
from almasix.orbit.panels.resource_generator import (
    ColumnSpec,
    default_title_schemas,
    format_list,
    generate_schemas,
    resolve_model,
)


def test_generate_schemas_maps_common_types() -> None:
    cols = [
        ColumnSpec("id", "INTEGER", nullable=False),
        ColumnSpec("title", "VARCHAR(200)", nullable=False),
        ColumnSpec("body", "TEXT", nullable=True),
        ColumnSpec("published", "BOOLEAN", nullable=False, cast="bool"),
        ColumnSpec("views", "INTEGER", nullable=True),
        ColumnSpec("published_at", "DATETIME", nullable=True),
        ColumnSpec("created_at", "DATETIME", nullable=True),
        ColumnSpec("updated_at", "DATETIME", nullable=True),
        ColumnSpec("password", "VARCHAR(255)", nullable=True),
        ColumnSpec("remember_token", "VARCHAR(100)", nullable=True),
        ColumnSpec("author_id", "INTEGER", nullable=True),
        ColumnSpec("email", "VARCHAR(255)", nullable=False),
    ]
    model = SimpleNamespace(
        primary_key="id",
        timestamps=True,
        created_at="created_at",
        updated_at="updated_at",
        _soft_deletes=False,
        hidden=("password", "remember_token"),
    )
    schemas = generate_schemas(cols, model=model)  # type: ignore[arg-type]
    form = "\n".join(schemas.form_fields)
    table = "\n".join(schemas.table_columns)

    assert 'TextInput.make("title").required().max_length(200)' in form
    assert 'Textarea.make("body")' in form
    assert 'Toggle.make("published")' in form
    assert 'TextInput.make("views").integer()' in form
    assert 'DateTimePicker.make("published_at")' in form
    assert 'TextInput.make("email").email().required()' in form
    assert 'TextInput.make("password").password()' in form
    assert 'TextInput.make("author_id").integer()' in form
    assert "created_at" not in form
    assert "id" not in form or 'make("id")' not in form

    assert 'TextColumn.make("title").searchable().sortable()' in table
    assert 'BooleanColumn.make("published")' in table
    assert 'TextColumn.make("created_at").date_time().sortable().toggleable' in table
    assert "password" not in table
    assert "remember_token" not in table
    assert "BooleanColumn" in schemas.table_imports
    assert "Toggle" in schemas.form_imports
    assert "Textarea" in schemas.form_imports
    assert "DateTimePicker" in schemas.form_imports


def test_generate_schemas_empty_falls_back_to_title() -> None:
    schemas = generate_schemas([])
    assert schemas == default_title_schemas() or schemas.form_fields == default_title_schemas().form_fields


def test_format_list_empty_comment() -> None:
    assert "add fields" in format_list([])


def test_resolve_model_missing() -> None:
    assert resolve_model("") is None
    assert resolve_model("DefinitelyMissingModelXYZ") is None


def test_make_orbit_resource_generate_from_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app_root = tmp_path
    (app_root / "app" / "orbit" / "admin").mkdir(parents=True)
    (app_root / "app" / "orbit" / "admin" / "panel.py").write_text(
        "from almasix.orbit import Panel\n\npanel = Panel.make('admin')\n",
        encoding="utf-8",
    )
    (app_root / "app" / "models").mkdir(parents=True)
    (app_root / "app" / "models" / "__init__.py").write_text("", encoding="utf-8")
    (app_root / "app" / "models" / "article.py").write_text(
        '''from almasix.orm import Model

class Article(Model):
    fillable = ("title", "body", "published")
''',
        encoding="utf-8",
    )

    class FakeApp:
        def path(self, *parts: str) -> str:
            return str(app_root.joinpath(*parts))

    cols = [
        ColumnSpec("id", "INTEGER", nullable=False),
        ColumnSpec("title", "VARCHAR(120)", nullable=False),
        ColumnSpec("body", "TEXT", nullable=True),
        ColumnSpec("published", "BOOLEAN", nullable=False),
        ColumnSpec("created_at", "DATETIME", nullable=True),
        ColumnSpec("updated_at", "DATETIME", nullable=True),
    ]

    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.load_columns",
        lambda model, connection=None: (cols, None),
    )
    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.resolve_model",
        lambda name: type(
            "Article",
            (),
            {
                "__module__": "app.models.article",
                "__name__": "Article",
                "get_table": classmethod(lambda cls: "articles"),
                "primary_key": "id",
                "timestamps": True,
                "created_at": "created_at",
                "updated_at": "updated_at",
                "_soft_deletes": False,
                "hidden": (),
                "class_casts": classmethod(lambda cls: {}),
            },
        ),
    )

    cmd = MakeOrbitResourceCommand(FakeApp())
    cmd._arguments = {"name": "Article"}
    cmd._options = {"panel": "admin", "force": True, "generate": True, "model": "Article"}
    assert cmd.handle() == 0
    out = app_root / "app" / "orbit" / "admin" / "resources" / "article_resource.py"
    text = out.read_text(encoding="utf-8")
    assert "model = Article" in text
    assert "from app.models.article import Article" in text
    assert 'TextInput.make("title").required().max_length(120)' in text
    assert 'Textarea.make("body")' in text
    assert 'Toggle.make("published")' in text
    assert 'BooleanColumn.make("published")' in text
    assert 'navigation_label = "Articles"' in text
    assert "navigation_group" not in text


def test_make_orbit_resource_without_generate_keeps_title_stub(tmp_path: Path) -> None:
    app_root = tmp_path
    (app_root / "app" / "orbit" / "admin").mkdir(parents=True)
    (app_root / "app" / "orbit" / "admin" / "panel.py").write_text("x=1\n", encoding="utf-8")

    class FakeApp:
        def path(self, *parts: str) -> str:
            return str(app_root.joinpath(*parts))

    cmd = MakeOrbitResourceCommand(FakeApp())
    cmd._arguments = {"name": "Widget"}
    cmd._options = {"panel": "admin", "force": True}
    assert cmd.handle() == 0
    text = (app_root / "app" / "orbit" / "admin" / "resources" / "widget_resource.py").read_text(
        encoding="utf-8"
    )
    assert "# model = Widget" in text
    assert 'TextInput.make("title")' in text
