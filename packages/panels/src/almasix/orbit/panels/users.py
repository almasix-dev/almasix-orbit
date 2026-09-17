"""Orbit panel user + menu helpers (fluent, host-agnostic)."""

from __future__ import annotations

from typing import Any, Self


class _FluentStr:
    """Instance attribute that is both a string (for duck-typing) and a setter."""

    def __init__(self, private: str, default: str = "") -> None:
        self.private = private
        self.default = default

    def __set_name__(self, owner: type, name: str) -> None:
        self.public = name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        current = getattr(obj, self.private)

        class _Value(str):
            __slots__ = ()

            def __new__(cls, text: str) -> _Value:
                return str.__new__(cls, text)

            def __call__(inner_self, value: str) -> Any:
                setattr(obj, self.private, value)
                return obj

        return _Value(current)

    def __set__(self, obj: Any, value: str) -> None:
        setattr(obj, self.private, value)


class _FluentBool:
    """Boolean attribute with optional fluent ``.admin(True)``-style setting via method."""

    def __init__(self, private: str, default: bool = False) -> None:
        self.private = private
        self.default = default

    def __get__(self, obj: Any, objtype: type | None = None) -> bool:
        if obj is None:
            return self  # type: ignore[return-value]
        return bool(getattr(obj, self.private))

    def __set__(self, obj: Any, value: bool) -> None:
        setattr(obj, self.private, bool(value))


class OrbitUser:
    """Lightweight panel principal for shell chrome and local demos.

    Prefer Almasix ``auth().user()`` in production. Configure a panel default with::

        Panel.make("admin").default_user()
        # or:
        Panel.make("admin").user(
            OrbitUser.make().name("Ada").email("ada@orbit.test").admin()
        )

    ``name`` / ``email`` are fluent setters and string-valued reads (duck-typed like Auth users).
    """

    name = _FluentStr("_name", "Admin")  # noqa: A003
    email = _FluentStr("_email", "admin@orbit.test")
    is_admin = _FluentBool("_is_admin", True)

    def __init__(self) -> None:
        self._name = "Admin"
        self._email = "admin@orbit.test"
        self._is_admin = True
        self._permissions: set[str] = set()

    @classmethod
    def make(cls) -> Self:
        return cls()

    @classmethod
    def default(cls) -> Self:
        """Sensible local-admin default."""
        return cls.make().name("Admin").email("admin@orbit.test").admin()

    def admin(self, condition: bool = True) -> Self:
        self._is_admin = condition
        return self

    def permissions(self, *abilities: str) -> Self:
        self._permissions |= set(abilities)
        return self

    def can(self, ability: str, record: Any = None) -> bool:  # noqa: ARG002
        if self._is_admin or "*" in self._permissions:
            return True
        return ability in self._permissions

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "email": self._email,
            "is_admin": self._is_admin,
            "permissions": sorted(self._permissions),
        }


class UserMenuItem:
    """Fluent topbar user-menu link."""

    def __init__(self, name: str | None = None) -> None:
        self._name = name
        self._label: str = (name or "Item").replace("_", " ").title()
        self._url: str = "#"

    @classmethod
    def make(cls, name: str | None = None) -> Self:
        return cls(name)

    def label(self, value: str) -> Self:
        self._label = value
        return self

    def url(self, value: str) -> Self:
        self._url = value
        return self

    def to_dict(self) -> dict[str, str]:
        return {"label": self._label, "url": self._url}


class PanelNotification:
    """Fluent notification seed for demos / shell chrome."""

    def __init__(self) -> None:
        self._title: str = "Notification"
        self._body: str = ""

    @classmethod
    def make(cls, title: str | None = None) -> Self:
        inst = cls()
        if title:
            inst._title = title
        return inst

    def title(self, value: str) -> Self:
        self._title = value
        return self

    def body(self, value: str) -> Self:
        self._body = value
        return self

    def to_dict(self) -> dict[str, str]:
        return {"title": self._title, "body": self._body}
