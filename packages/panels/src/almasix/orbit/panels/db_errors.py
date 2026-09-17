"""Map database integrity / UNIQUE failures to user-facing messages."""

from __future__ import annotations

import re

# SQLite: UNIQUE constraint failed: users.email
_SQLITE_UNIQUE = re.compile(
    r"unique constraint failed:\s*(?:(?P<table>[\w\"`]+)\.)?(?P<column>[\w\"`]+)",
    re.IGNORECASE,
)
# PostgreSQL: Key (email)=(x) already exists. / constraint "users_email_key"
_PG_KEY = re.compile(r"Key\s*\((?P<column>[^)]+)\)=", re.IGNORECASE)
_PG_CONSTRAINT = re.compile(
    r'unique constraint ["`]?(?P<table>\w+)_(?P<column>\w+)(?:_key|_unique)?["`]?',
    re.IGNORECASE,
)
# MySQL: Duplicate entry 'x' for key 'users.email' / 'email'
_MYSQL_DUP = re.compile(
    r"duplicate entry .+ for key ['`](?:[\w]+\.)?(?P<column>[\w]+)['`]",
    re.IGNORECASE,
)

_DEFAULT_FIELD_LABELS: dict[str, str] = {
    "email": "email",
    "username": "username",
    "slug": "slug",
    "name": "name",
}


def iter_exception_chain(exc: BaseException) -> list[BaseException]:
    """Walk ``__cause__`` / ``orig`` / ``__context__`` without cycles."""
    out: list[BaseException] = []
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        out.append(current)
        seen.add(id(current))
        nxt = getattr(current, "__cause__", None)
        if nxt is None:
            nxt = getattr(current, "orig", None)
        if nxt is None:
            nxt = getattr(current, "__context__", None)
        current = nxt if isinstance(nxt, BaseException) else None
    return out


def is_unique_violation(exc: BaseException) -> bool:
    """True when ``exc`` (or a wrapped cause) is a UNIQUE / duplicate-key failure."""
    for err in iter_exception_chain(exc):
        name = type(err).__name__
        msg = str(err).lower()
        if name in {"UniqueViolation", "UniqueViolationError", "DuplicateKeyError"}:
            return True
        if "unique constraint" in msg or "duplicate key" in msg or "duplicate entry" in msg:
            return True
        if name == "IntegrityError" and ("unique" in msg or "duplicate" in msg):
            return True
    return False


def unique_violation_column(exc: BaseException) -> str | None:
    """Best-effort column name from common SQLite / Postgres / MySQL messages."""
    for err in iter_exception_chain(exc):
        text = str(err)
        for pattern in (_SQLITE_UNIQUE, _PG_KEY, _PG_CONSTRAINT, _MYSQL_DUP):
            match = pattern.search(text)
            if match:
                col = match.group("column")
                return str(col).strip("`\"' ").split(",")[0].strip()
    return None


def friendly_unique_message(
    exc: BaseException,
    *,
    field_labels: dict[str, str] | None = None,
    default: str = "That value is already taken.",
) -> str:
    """Human-readable message for a UNIQUE violation (falls back to ``default``)."""
    if not is_unique_violation(exc):
        return str(exc) or default
    column = unique_violation_column(exc)
    labels = {**_DEFAULT_FIELD_LABELS, **(field_labels or {})}
    if column:
        key = column.lower()
        label = labels.get(key, key.replace("_", " "))
        if key == "email":
            return "An account with this email already exists."
        return f"This {label} is already taken."
    return default


def map_db_error(exc: BaseException, *, field_labels: dict[str, str] | None = None) -> str:
    """Map a persistence exception to a safe UI/CLI string."""
    if is_unique_violation(exc):
        return friendly_unique_message(exc, field_labels=field_labels)
    text = str(exc).strip()
    # Avoid dumping SQL / parameter dumps in the auth UI.
    if "UNIQUE constraint" in text or "IntegrityError" in text or "[SQL:" in text:
        return "Could not save — please check your input and try again."
    return text or "Could not save."
