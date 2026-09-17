"""Tests for UNIQUE / IntegrityError → user-facing message mapping."""

from __future__ import annotations

import asyncio

from almasix.orbit.panels.conduit.hosts import RegisterHost
from almasix.orbit.panels.db_errors import (
    friendly_unique_message,
    is_unique_violation,
    map_db_error,
    unique_violation_column,
)
from almasix.orbit.panels.panel import Panel


class _SqliteUnique(Exception):
    pass


def test_detects_sqlite_unique() -> None:
    exc = _SqliteUnique("UNIQUE constraint failed: users.email")
    # Pretend it's an IntegrityError by name via a dynamic type
    exc.__class__ = type("IntegrityError", (Exception,), {})
    err = exc.__class__("UNIQUE constraint failed: users.email")
    assert is_unique_violation(err)
    assert unique_violation_column(err) == "email"
    assert "email already exists" in friendly_unique_message(err).lower()


def test_detects_postgres_and_mysql_messages() -> None:
    pg = Exception(
        'duplicate key value violates unique constraint "users_email_key"\n'
        "DETAIL:  Key (email)=(a@b.c) already exists."
    )
    assert is_unique_violation(pg)
    assert unique_violation_column(pg) == "email"

    mysql = Exception("Duplicate entry 'a@b.c' for key 'users.email'")
    assert is_unique_violation(mysql)
    assert unique_violation_column(mysql) == "email"


def test_wrapped_sqlalchemy_style_chain() -> None:
    class IntegrityError(Exception):
        pass

    orig = IntegrityError("UNIQUE constraint failed: users.email")
    wrapper = Exception(
        "(sqlite3.IntegrityError) UNIQUE constraint failed: users.email "
        "[SQL: INSERT INTO users ...] [parameters: (...)]"
    )
    wrapper.__cause__ = orig
    assert is_unique_violation(wrapper)
    assert "already exists" in map_db_error(wrapper).lower()
    assert "[SQL:" not in map_db_error(wrapper)


def test_non_unique_falls_through_safely() -> None:
    err = RuntimeError("connection refused")
    assert not is_unique_violation(err)
    assert map_db_error(err) == "connection refused"


def test_unique_violation_named_types_and_slug() -> None:
    class UniqueViolation(Exception):
        pass

    err = UniqueViolation("boom")
    assert is_unique_violation(err)
    assert friendly_unique_message(err) == "That value is already taken."

    slug = Exception("UNIQUE constraint failed: posts.slug")
    assert unique_violation_column(slug) == "slug"
    assert friendly_unique_message(slug) == "This slug is already taken."
    assert friendly_unique_message(slug, field_labels={"slug": "URL slug"}) == "This URL slug is already taken."


def test_map_db_error_sanitizes_sql_dumps() -> None:
    err = Exception("weird IntegrityError failure [SQL: SELECT 1]")
    msg = map_db_error(err)
    assert "[SQL:" not in msg
    assert "Could not save" in msg
    assert map_db_error(Exception("")) == "Could not save."
    assert friendly_unique_message(RuntimeError("x")) == "x"


def test_register_host_maps_unique_integrity_error(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    panel = Panel.make("admin").path("admin")

    class BoomModel:
        @staticmethod
        def create(data):  # type: ignore[no-untyped-def]
            raise Exception(
                "(sqlite3.IntegrityError) UNIQUE constraint failed: users.email "
                "[SQL: INSERT INTO users (name, email, password) VALUES (?, ?, ?)]"
            )

    host_cls = type(
        "RH",
        (RegisterHost,),
        {"panel_id": "admin", "_panel": panel},
    )
    host = host_cls(
        name="Sam",
        email="maosa.sam@gmail.com",
        password="secret",
        password_confirmation="secret",
    )
    monkeypatch.setattr(host, "_user_model", lambda: BoomModel)
    monkeypatch.setattr(host, "_email_taken", lambda model, email: False)
    monkeypatch.setattr("almasix.hashing.Hash.make", lambda p: f"hash:{p}")
    asyncio.run(host.register())
    assert host.error == "An account with this email already exists."
    assert "IntegrityError" not in host.error
    assert "[SQL:" not in host.error


def test_register_host_precheck_email_taken() -> None:
    panel = Panel.make("admin").path("admin")

    class Existing:
        records = [{"email": "taken@example.com"}]

        @staticmethod
        def create(data):  # type: ignore[no-untyped-def]
            raise AssertionError("create should not run when email is taken")

    host_cls = type(
        "RH",
        (RegisterHost,),
        {"panel_id": "admin", "_panel": panel},
    )
    host = host_cls(
        name="Sam",
        email="taken@example.com",
        password="secret",
        password_confirmation="secret",
    )
    host._user_model = lambda: Existing  # type: ignore[method-assign]
    asyncio.run(host.register())
    assert host.error == "An account with this email already exists."
