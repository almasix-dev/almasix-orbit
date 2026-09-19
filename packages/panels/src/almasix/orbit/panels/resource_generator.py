"""Generate Orbit resource form/table stubs from a model's database columns.

Mirrors Filament's ``make:filament-resource --generate``: reflect the live
table via :class:`~almasix.orm.schema.Schema`, map SQL / cast types onto Orbit
fields and columns, and emit Python source fragments for the stub.
"""

from __future__ import annotations

import asyncio
import importlib
import re
from dataclasses import dataclass
from typing import Any

# Columns Filament typically omits from generated forms.
_SKIP_FORM = frozenset(
    {
        "id",
        "uuid",
        "ulid",
        "created_at",
        "updated_at",
        "deleted_at",
        "remember_token",
    }
)

# Secrets / tokens stay off the list table.
_SKIP_TABLE = frozenset({"password", "remember_token"})

_VARCHAR_LEN = re.compile(r"(?:VARCHAR|CHAR|STRING|NVARCHAR)\s*\(\s*(\d+)\s*\)", re.I)
_TEXT_HINT = re.compile(r"(TEXT|CLOB|BLOB)", re.I)


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    type: str
    nullable: bool = True
    default: Any = None
    cast: Any = None


@dataclass(frozen=True)
class GeneratedSchemas:
    """Python source fragments for ``form()`` / ``table()`` plus import names."""

    form_fields: list[str]
    table_columns: list[str]
    form_imports: tuple[str, ...]
    table_imports: tuple[str, ...]
    column_count: int
    warning: str | None = None


def resolve_model(name: str | None) -> type[Any] | None:
    """Locate an Almasix ORM model by bare name or dotted path."""
    if not name or not str(name).strip():
        return None
    raw = str(name).strip()
    found = _locate(raw)
    if found is None:
        return None
    try:
        from almasix.orm.model import Model
    except ImportError:
        return found if isinstance(found, type) else None
    if isinstance(found, type) and issubclass(found, Model):
        return found
    return None


def _locate(name: str) -> Any:
    if "." in name:
        module_name, _, attribute = name.rpartition(".")
        try:
            return getattr(importlib.import_module(module_name), attribute, None)
        except ImportError:
            return None
    try:
        from almasix.console.repl import discover_app_classes
    except ImportError:
        return None
    return discover_app_classes().get(name)


def model_import_path(model: type[Any]) -> str:
    return f"{model.__module__}.{model.__name__}"


def model_import_statement(model: type[Any]) -> str:
    return f"from {model.__module__} import {model.__name__}"


def load_columns(model: type[Any], *, connection: str | None = None) -> tuple[list[ColumnSpec], str | None]:
    """Reflect ``Schema.columns`` for ``model``; return ``(cols, error_or_None)``."""
    try:
        from almasix.orm.schema import Schema
    except ImportError as exc:
        return [], f"ORM schema unavailable: {exc}"

    table = model.get_table()
    conn = connection or getattr(model, "connection", None)
    try:
        raw = asyncio.run(Schema.columns(table, connection=conn))
    except Exception as exc:  # noqa: BLE001 — surface DB errors to the CLI
        return [], f"Could not read columns for table [{table}]: {exc}"
    if not raw:
        return [], f"Table [{table}] does not exist yet (or has no columns)."

    casts = {}
    if hasattr(model, "class_casts"):
        try:
            casts = dict(model.class_casts() or {})
        except Exception:  # noqa: BLE001
            casts = {}

    specs = [
        ColumnSpec(
            name=str(col["name"]),
            type=str(col.get("type") or ""),
            nullable=bool(col.get("nullable", True)),
            default=col.get("default"),
            cast=casts.get(str(col["name"])),
        )
        for col in raw
    ]
    return specs, None


def generate_schemas(
    columns: list[ColumnSpec],
    *,
    model: type[Any] | None = None,
) -> GeneratedSchemas:
    """Map reflected columns onto Orbit form field / table column source lines."""
    pk = getattr(model, "primary_key", "id") if model else "id"
    form_fields: list[str] = []
    table_columns: list[str] = []
    form_imports: set[str] = set()
    table_imports: set[str] = set()

    for col in columns:
        if col.name == pk or col.name in _SKIP_FORM:
            pass
        elif _is_timestamp(col, model) and col.name in (
            getattr(model, "created_at", "created_at") if model else "created_at",
            getattr(model, "updated_at", "updated_at") if model else "updated_at",
        ):
            pass
        else:
            field_line, field_imps = _form_field(col)
            if field_line:
                form_fields.append(field_line)
                form_imports.update(field_imps)

        if col.name in _SKIP_TABLE:
            continue
        if col.name in (getattr(model, "hidden", ()) if model else ()):
            if col.name in ("password", "remember_token"):
                continue
        col_line, col_imps = _table_column(col, model=model)
        if col_line:
            table_columns.append(col_line)
            table_imports.update(col_imps)

    if not form_fields and not columns:
        form_fields = ['TextInput.make("title").required().max_length(200)']
        form_imports.add("TextInput")
    if not table_columns and not columns:
        table_columns = ['TextColumn.make("title").searchable().sortable()']
        table_imports.add("TextColumn")

    return GeneratedSchemas(
        form_fields=form_fields,
        table_columns=table_columns,
        form_imports=tuple(sorted(form_imports)),
        table_imports=tuple(sorted(table_imports)),
        column_count=len(columns),
    )


def default_title_schemas() -> GeneratedSchemas:
    return GeneratedSchemas(
        form_fields=['TextInput.make("title").required().max_length(200)'],
        table_columns=['TextColumn.make("title").searchable().sortable()'],
        form_imports=("TextInput",),
        table_imports=("TextColumn",),
        column_count=0,
    )


def empty_schemas(*, comment: str | None = None) -> GeneratedSchemas:
    """Empty form/table bodies (Filament fallback when generation yields nothing)."""
    tip = f"  # {comment}\n" if comment else ""
    return GeneratedSchemas(
        form_fields=[],
        table_columns=[],
        form_imports=(),
        table_imports=(),
        column_count=0,
        warning=comment,
    )


def _is_timestamp(col: ColumnSpec, model: type[Any] | None) -> bool:
    if model is None:
        return col.name in ("created_at", "updated_at", "deleted_at")
    names = set()
    if getattr(model, "timestamps", True):
        names.add(getattr(model, "created_at", "created_at"))
        names.add(getattr(model, "updated_at", "updated_at"))
    if getattr(model, "_soft_deletes", False):
        names.add(getattr(model, "deleted_at", "deleted_at"))
    return col.name in names


def _cast_name(cast: Any) -> str:
    if cast is None:
        return ""
    if isinstance(cast, str):
        return cast.lower()
    if isinstance(cast, type):
        return cast.__name__.lower()
    return str(cast).lower()


def _kind(col: ColumnSpec) -> str:
    cast = _cast_name(col.cast)
    type_u = (col.type or "").upper()
    name = col.name.lower()

    if cast in ("bool", "boolean") or "BOOL" in type_u or type_u in ("BOOLEAN", "BIT"):
        return "boolean"
    if cast in ("date",) or type_u == "DATE" or type_u.startswith("DATE("):
        return "date"
    if cast in ("datetime", "timestamp") or any(
        t in type_u for t in ("DATETIME", "TIMESTAMP", "TIMESTAMPTZ")
    ):
        return "datetime"
    if cast in ("time",) or type_u.startswith("TIME"):
        return "time"
    if cast in ("json", "array", "object", "asjson", "asarray") or "JSON" in type_u:
        return "json"
    if cast in ("float", "decimal", "double") or any(
        t in type_u for t in ("FLOAT", "DOUBLE", "DECIMAL", "NUMERIC", "REAL")
    ):
        return "numeric"
    if cast in ("int", "integer") or any(
        t in type_u for t in ("INT", "BIGINT", "SMALLINT", "TINYINT", "SERIAL")
    ):
        return "integer"
    if _TEXT_HINT.search(type_u) and "VARCHAR" not in type_u:
        return "text"
    if name in ("email", "e_mail"):
        return "email"
    if name == "password":
        return "password"
    if name.endswith("_id"):
        return "foreign_id"
    if "ENUM" in type_u:
        return "enum"
    return "string"


def _varchar_max(col: ColumnSpec) -> int | None:
    match = _VARCHAR_LEN.search(col.type or "")
    if match:
        return int(match.group(1))
    return None


def _form_field(col: ColumnSpec) -> tuple[str | None, set[str]]:
    kind = _kind(col)
    name = col.name
    req = "" if col.nullable else ".required()"

    if kind == "boolean":
        return f'Toggle.make("{name}")', {"Toggle"}
    if kind == "date":
        return f'DatePicker.make("{name}"){req}', {"DatePicker"}
    if kind == "datetime":
        return f'DateTimePicker.make("{name}"){req}', {"DateTimePicker"}
    if kind == "time":
        return f'TimePicker.make("{name}"){req}', {"TimePicker"}
    if kind == "text":
        return f'Textarea.make("{name}"){req}.column_span("full")', {"Textarea"}
    if kind == "json":
        return f'Textarea.make("{name}"){req}.column_span("full")', {"Textarea"}
    if kind == "email":
        return f'TextInput.make("{name}").email(){req}', {"TextInput"}
    if kind == "password":
        return f'TextInput.make("{name}").password(){req}', {"TextInput"}
    if kind == "integer":
        return f'TextInput.make("{name}").integer(){req}', {"TextInput"}
    if kind == "numeric":
        return f'TextInput.make("{name}").numeric(){req}', {"TextInput"}
    if kind == "foreign_id":
        return f'TextInput.make("{name}").integer(){req}', {"TextInput"}
    if kind == "enum":
        return f'Select.make("{name}"){req}', {"Select"}

    max_len = _varchar_max(col)
    max_bit = f".max_length({max_len})" if max_len else ""
    return f'TextInput.make("{name}"){req}{max_bit}', {"TextInput"}


def _table_column(col: ColumnSpec, *, model: type[Any] | None) -> tuple[str | None, set[str]]:
    kind = _kind(col)
    name = col.name

    if kind == "boolean":
        return f'BooleanColumn.make("{name}")', {"BooleanColumn"}

    if _is_timestamp(col, model) or kind in ("datetime", "date", "time"):
        if kind == "date":
            body = f'TextColumn.make("{name}").date().sortable()'
        elif kind == "time":
            body = f'TextColumn.make("{name}").sortable()'
        else:
            body = f'TextColumn.make("{name}").date_time().sortable()'
        if _is_timestamp(col, model):
            body += ".toggleable(is_toggled_hidden_by_default=True)"
        return body, {"TextColumn"}

    if kind == "text" or kind == "json":
        return f'TextColumn.make("{name}").limit(50)', {"TextColumn"}

    if kind in ("integer", "numeric", "foreign_id"):
        return f'TextColumn.make("{name}").sortable()', {"TextColumn"}

    # Default string-like — searchable + sortable like Filament's TextColumn
    return f'TextColumn.make("{name}").searchable().sortable()', {"TextColumn"}


def format_list(lines: list[str], *, indent: str = "                ") -> str:
    """Format a Python list body for embedding in a stub."""
    if not lines:
        return f"{indent}# add fields / columns here\n"
    return "".join(f"{indent}{line},\n" for line in lines)
