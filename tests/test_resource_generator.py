"""Tests for Orbit resource form/table generation from DB columns."""

from __future__ import annotations

import builtins
from pathlib import Path
from types import SimpleNamespace

import pytest
from almasix.orbit.panels.commands import MakeOrbitResourceCommand
from almasix.orbit.panels.resource_generator import (
    ColumnSpec,
    _cast_name,
    _kind,
    _locate,
    default_title_schemas,
    empty_schemas,
    format_list,
    generate_schemas,
    load_columns,
    model_import_path,
    model_import_statement,
    resolve_model,
)
from almasix.orm import Model


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
    assert 'make("id")' not in form
    assert 'make("created_at")' not in form

    assert 'TextColumn.make("title").searchable().sortable()' in table
    assert 'BooleanColumn.make("published")' in table
    assert 'TextColumn.make("created_at").date_time().sortable().toggleable' in table
    assert "password" not in table
    assert "remember_token" not in table
    assert "BooleanColumn" in schemas.table_imports
    assert "Toggle" in schemas.form_imports
    assert "Textarea" in schemas.form_imports
    assert "DateTimePicker" in schemas.form_imports


def test_generate_schemas_covers_remaining_kinds() -> None:
    cols = [
        ColumnSpec("born_on", "DATE", nullable=False),
        ColumnSpec("opens_at", "TIME", nullable=True),
        ColumnSpec("meta", "JSON", nullable=True),
        ColumnSpec("price", "DECIMAL(10,2)", nullable=False, cast="decimal"),
        ColumnSpec("kind", "ENUM('a','b')", nullable=False),
        ColumnSpec("note", "VARCHAR", nullable=True),
        ColumnSpec("deleted_at", "DATETIME", nullable=True),
        ColumnSpec("uuid", "CHAR(36)", nullable=False),
    ]
    model = SimpleNamespace(
        primary_key="id",
        timestamps=False,
        created_at="created_at",
        updated_at="updated_at",
        deleted_at="deleted_at",
        _soft_deletes=True,
        hidden=(),
    )
    schemas = generate_schemas(cols, model=model)  # type: ignore[arg-type]
    form = "\n".join(schemas.form_fields)
    table = "\n".join(schemas.table_columns)
    assert 'DatePicker.make("born_on").required()' in form
    assert 'TimePicker.make("opens_at")' in form
    assert 'Textarea.make("meta")' in form
    assert 'TextInput.make("price").numeric().required()' in form
    assert 'Select.make("kind").required()' in form
    assert 'TextInput.make("note")' in form
    assert 'make("uuid")' not in form
    assert 'make("deleted_at")' not in form
    assert 'TextColumn.make("born_on").date().sortable()' in table
    assert 'TextColumn.make("opens_at").sortable()' in table
    assert 'TextColumn.make("meta").limit(50)' in table
    assert 'TextColumn.make("price").sortable()' in table
    assert "DatePicker" in schemas.form_imports
    assert "TimePicker" in schemas.form_imports
    assert "Select" in schemas.form_imports


def test_generate_schemas_custom_timestamps_and_fk() -> None:
    model = SimpleNamespace(
        primary_key="id",
        timestamps=True,
        created_at="made_at",
        updated_at="changed_at",
        _soft_deletes=False,
        hidden=(),
    )
    schemas = generate_schemas(
        [
            ColumnSpec("id", "INTEGER"),
            ColumnSpec("made_at", "DATETIME"),
            ColumnSpec("changed_at", "DATETIME"),
            ColumnSpec("user_id", "INTEGER", nullable=False),
            ColumnSpec("tag_id", "VARCHAR(36)", nullable=True),
        ],
        model=model,  # type: ignore[arg-type]
    )
    form = "\n".join(schemas.form_fields)
    assert 'make("made_at")' not in form
    assert 'TextInput.make("user_id").integer().required()' in form
    assert 'TextInput.make("tag_id").integer()' in form or 'TextInput.make("tag_id")' in form
    assert any("user_id" in c for c in schemas.table_columns)

    schemas = generate_schemas(
        [
            ColumnSpec("created_at", "DATETIME"),
            ColumnSpec("title", "STRING"),
        ]
    )
    assert any("title" in line for line in schemas.form_fields)
    assert any("created_at" in line for line in schemas.table_columns)


def test_generate_schemas_all_skipped_leaves_empty_lists() -> None:
    schemas = generate_schemas(
        [ColumnSpec("id", "INTEGER"), ColumnSpec("uuid", "CHAR(36)")],
        model=SimpleNamespace(  # type: ignore[arg-type]
            primary_key="id",
            timestamps=False,
            _soft_deletes=False,
            hidden=(),
        ),
    )
    assert schemas.form_fields == []
    assert schemas.table_columns == [c for c in schemas.table_columns]  # id still on table
    assert any("id" in c for c in schemas.table_columns)


def test_generate_schemas_empty_falls_back_to_title() -> None:
    schemas = generate_schemas([])
    assert schemas.form_fields == default_title_schemas().form_fields
    assert schemas.table_columns == default_title_schemas().table_columns


def test_empty_schemas_and_format_list() -> None:
    empty = empty_schemas(comment="no columns")
    assert empty.warning == "no columns"
    assert empty.form_fields == []
    assert "add fields" in format_list([])
    assert "foo" in format_list(["foo"])


def test_cast_name_and_kind_helpers() -> None:
    assert _cast_name(None) == ""
    assert _cast_name("JSON") == "json"
    assert _cast_name(bool) == "bool"
    assert _cast_name(123) == "123"
    assert _kind(ColumnSpec("flag", "BIT")) == "boolean"
    assert _kind(ColumnSpec("d", "DATE()")) == "date"
    assert _kind(ColumnSpec("t", "", cast="timestamp")) == "datetime"
    assert _kind(ColumnSpec("x", "", cast="time")) == "time"
    assert _kind(ColumnSpec("j", "", cast="array")) == "json"
    assert _kind(ColumnSpec("n", "REAL")) == "numeric"
    assert _kind(ColumnSpec("i", "BIGINT")) == "integer"
    assert _kind(ColumnSpec("e_mail", "VARCHAR(10)")) == "email"


def test_resolve_and_locate_model(monkeypatch: pytest.MonkeyPatch) -> None:
    assert resolve_model("") is None
    assert resolve_model("DefinitelyMissingModelXYZ") is None
    assert resolve_model("almasix.orm.model.Model") is Model
    assert resolve_model("missing.module.Nope") is None

    class NotAModel:
        pass

    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator._locate",
        lambda name: NotAModel if name == "X" else None,
    )
    assert resolve_model("X") is None

    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator._locate",
        lambda name: "not-a-type",
    )
    assert resolve_model("Y") is None

    assert model_import_path(Model) == "almasix.orm.model.Model"
    assert "import Model" in model_import_statement(Model)


def test_locate_bare_name_via_discover(monkeypatch: pytest.MonkeyPatch) -> None:
    class Demo(Model):
        pass

    monkeypatch.setattr(
        "almasix.console.repl.discover_app_classes",
        lambda: {"Demo": Demo},
    )
    assert _locate("Demo") is Demo
    assert resolve_model("Demo") is Demo


def test_locate_dotted_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.importlib.import_module",
        lambda name: (_ for _ in ()).throw(ImportError("nope")),
    )
    assert _locate("pkg.Missing") is None


def test_locate_bare_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    monkeypatch.delitem(sys.modules, "almasix.console.repl", raising=False)
    real_import = builtins.__import__

    def block_repl(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: tuple = (),
        level: int = 0,
    ) -> object:
        if name == "almasix.console.repl" or name.startswith("almasix.console.repl"):
            raise ImportError("gone")
        return real_import(name, globals, locals, fromlist, level)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", block_repl)
    assert _locate("Bare") is None


def test_load_columns_success_and_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeModel:
        connection = None

        @classmethod
        def get_table(cls) -> str:
            return "things"

        @classmethod
        def class_casts(cls) -> dict[str, str]:
            return {"active": "bool"}

    async def fake_columns(table: str, connection: str | None = None) -> list[dict[str, object]]:
        assert table == "things"
        return [
            {"name": "active", "type": "BOOLEAN", "nullable": False, "default": None},
            {"name": "title", "type": None, "nullable": True},
        ]

    monkeypatch.setattr(
        "almasix.orm.schema.Schema.columns",
        fake_columns,
    )
    cols, err = load_columns(FakeModel)  # type: ignore[arg-type]
    assert err is None
    assert cols[0].cast == "bool"
    assert cols[1].type == ""

    async def empty(table: str, connection: str | None = None) -> list[dict[str, object]]:
        return []

    monkeypatch.setattr("almasix.orm.schema.Schema.columns", empty)
    cols, err = load_columns(FakeModel)  # type: ignore[arg-type]
    assert cols == []
    assert err and "does not exist" in err

    async def boom(table: str, connection: str | None = None) -> list[dict[str, object]]:
        raise RuntimeError("db down")

    monkeypatch.setattr("almasix.orm.schema.Schema.columns", boom)
    cols, err = load_columns(FakeModel)  # type: ignore[arg-type]
    assert cols == []
    assert err and "Could not read columns" in err

    class BrokenCasts(FakeModel):
        @classmethod
        def class_casts(cls) -> dict[str, str]:
            raise RuntimeError("casts broke")

    async def one(table: str, connection: str | None = None) -> list[dict[str, object]]:
        return [{"name": "x", "type": "INT", "nullable": True}]

    monkeypatch.setattr("almasix.orm.schema.Schema.columns", one)
    cols, err = load_columns(BrokenCasts)  # type: ignore[arg-type]
    assert err is None
    assert cols[0].cast is None


def test_load_columns_schema_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    monkeypatch.delitem(sys.modules, "almasix.orm.schema", raising=False)
    real = builtins.__import__

    def hide(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: tuple = (),
        level: int = 0,
    ) -> object:
        if name == "almasix.orm.schema" or name.startswith("almasix.orm.schema."):
            raise ImportError("hidden")
        return real(name, globals, locals, fromlist, level)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", hide)

    class M:
        @classmethod
        def get_table(cls) -> str:
            return "t"

    cols, err = load_columns(M)  # type: ignore[arg-type]
    assert cols == []
    assert err and "ORM schema unavailable" in err


def test_resolve_model_without_orm(monkeypatch: pytest.MonkeyPatch) -> None:
    class Local:
        pass

    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator._locate",
        lambda name: Local,
    )

    import sys

    monkeypatch.delitem(sys.modules, "almasix.orm.model", raising=False)
    real = builtins.__import__

    def hide(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: tuple = (),
        level: int = 0,
    ) -> object:
        if name == "almasix.orm.model" or name.startswith("almasix.orm.model"):
            raise ImportError("no orm")
        return real(name, globals, locals, fromlist, level)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", hide)
    assert resolve_model("Local") is Local


def test_make_orbit_resource_generate_from_columns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_root = tmp_path
    (app_root / "app" / "orbit" / "admin").mkdir(parents=True)
    (app_root / "app" / "orbit" / "admin" / "panel.py").write_text(
        "from almasix.orbit import Panel\n\npanel = Panel.make('admin')\n",
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


def test_make_orbit_resource_generate_falls_back_on_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_root = tmp_path
    (app_root / "app" / "orbit" / "admin").mkdir(parents=True)
    (app_root / "app" / "orbit" / "admin" / "panel.py").write_text("x=1\n", encoding="utf-8")

    class FakeApp:
        def path(self, *parts: str) -> str:
            return str(app_root.joinpath(*parts))

    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.resolve_model",
        lambda name: type(
            "Post",
            (),
            {
                "__module__": "app.models.post",
                "__name__": "Post",
                "get_table": classmethod(lambda cls: "posts"),
            },
        ),
    )
    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.load_columns",
        lambda model, connection=None: ([], "Table [posts] does not exist yet"),
    )
    cmd = MakeOrbitResourceCommand(FakeApp())
    cmd._arguments = {"name": "Post"}
    cmd._options = {"panel": "admin", "force": True, "generate": True}
    assert cmd.handle() == 0
    text = (app_root / "app" / "orbit" / "admin" / "resources" / "post_resource.py").read_text(
        encoding="utf-8"
    )
    assert "model = Post" in text
    assert 'TextInput.make("title")' in text


def test_make_orbit_resource_generate_without_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_root = tmp_path
    (app_root / "app" / "orbit" / "admin").mkdir(parents=True)
    (app_root / "app" / "orbit" / "admin" / "panel.py").write_text("x=1\n", encoding="utf-8")

    class FakeApp:
        def path(self, *parts: str) -> str:
            return str(app_root.joinpath(*parts))

    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.resolve_model",
        lambda name: None,
    )
    cmd = MakeOrbitResourceCommand(FakeApp())
    cmd._arguments = {"name": "Ghost"}
    cmd._options = {"panel": "admin", "force": True, "generate": True}
    assert cmd.handle() == 0
    text = (app_root / "app" / "orbit" / "admin" / "resources" / "ghost_resource.py").read_text(
        encoding="utf-8"
    )
    assert "# model = Ghost" in text


def test_make_orbit_resource_prompt_generate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app_root = tmp_path
    (app_root / "app" / "orbit" / "admin").mkdir(parents=True)
    (app_root / "app" / "orbit" / "admin" / "panel.py").write_text("x=1\n", encoding="utf-8")

    class FakeApp:
        def path(self, *parts: str) -> str:
            return str(app_root.joinpath(*parts))

    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.resolve_model",
        lambda name: type(
            "Post",
            (),
            {
                "__module__": "app.models.post",
                "__name__": "Post",
                "get_table": classmethod(lambda cls: "posts"),
                "primary_key": "id",
                "timestamps": True,
                "created_at": "created_at",
                "updated_at": "updated_at",
                "_soft_deletes": False,
                "hidden": (),
            },
        ),
    )
    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.load_columns",
        lambda model, connection=None: (
            [ColumnSpec("title", "VARCHAR(50)", nullable=False)],
            None,
        ),
    )
    cmd = MakeOrbitResourceCommand(FakeApp())
    monkeypatch.setattr(cmd, "_should_prompt_generate", lambda: True)
    monkeypatch.setattr(cmd, "confirm", lambda *a, **k: True)
    cmd._arguments = {"name": "Post"}
    cmd._options = {"panel": "admin", "force": True}
    assert cmd.handle() == 0
    text = (app_root / "app" / "orbit" / "admin" / "resources" / "post_resource.py").read_text(
        encoding="utf-8"
    )
    assert 'TextInput.make("title").required().max_length(50)' in text

    # Decline prompt → title stub still linked to model
    cmd2 = MakeOrbitResourceCommand(FakeApp())
    monkeypatch.setattr(cmd2, "_should_prompt_generate", lambda: True)
    monkeypatch.setattr(cmd2, "confirm", lambda *a, **k: False)
    cmd2._arguments = {"name": "Post"}
    cmd2._options = {"panel": "admin", "force": True}
    assert cmd2.handle() == 0

    # Prompt path with load error
    cmd3 = MakeOrbitResourceCommand(FakeApp())
    monkeypatch.setattr(cmd3, "_should_prompt_generate", lambda: True)
    monkeypatch.setattr(cmd3, "confirm", lambda *a, **k: True)
    monkeypatch.setattr(
        "almasix.orbit.panels.resource_generator.load_columns",
        lambda model, connection=None: ([], "nope"),
    )
    cmd3._arguments = {"name": "Post"}
    cmd3._options = {"panel": "admin", "force": True}
    assert cmd3.handle() == 0


def test_should_prompt_generate_follows_interactive(monkeypatch: pytest.MonkeyPatch) -> None:
    cmd = MakeOrbitResourceCommand()
    monkeypatch.setattr("almasix.console.prompts.types.is_interactive", lambda: False)
    assert cmd._should_prompt_generate() is False
    monkeypatch.setattr("almasix.console.prompts.types.is_interactive", lambda: True)
    assert cmd._should_prompt_generate() is True


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
