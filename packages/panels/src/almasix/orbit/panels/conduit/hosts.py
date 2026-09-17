"""Conduit page hosts for Orbit resource CRUD.

Orbit SDUI (Form / Table / Schema) paints HTML; these hosts own Conduit public
state and ``wire:*`` actions — the Filament↔Livewire relationship for Orbit.
"""

from __future__ import annotations

from typing import Any, ClassVar

from almasix.conduit import Component, Conduit
from almasix.orbit.support.conduit_attrs import conduit_attr


class ConduitHost(Component):
    """Conduit host with redirect that works on PyPI Conduit (no ``Component.redirect``)."""

    def redirect(self, url: str, *, navigate: bool = False) -> None:
        """Queue a redirect after the response."""
        try:
            return super().redirect(url, navigate=navigate)  # type: ignore[misc]
        except AttributeError:
            pass
        except TypeError:
            try:
                return super().redirect(url)  # type: ignore[misc]
            except AttributeError:
                pass
        self._orbit_redirect = {"url": str(url), "navigate": bool(navigate)}

    def take_redirect(self) -> dict[str, Any] | None:
        """Pop the queued redirect, if any."""
        try:
            got = super().take_redirect()  # type: ignore[misc]
        except AttributeError:
            got = None
        if got is not None:
            return got
        target = getattr(self, "_orbit_redirect", None)
        self._orbit_redirect = None
        return target


class OrbitPageHost(ConduitHost):
    """Base host: panel + resource binding via ClassVars set by factories."""

    panel_id: ClassVar[str] = "admin"
    resource_slug: ClassVar[str] = ""
    _resource: ClassVar[type[Any] | None] = None
    _panel: ClassVar[Any] = None

    @classmethod
    def bind(cls, *, panel: Any, resource: type[Any] | None = None) -> type[OrbitPageHost]:
        name = f"{cls.__name__}_{getattr(resource, '__name__', 'page')}_{panel.id}"
        host = type(
            name,
            (cls,),
            {
                "panel_id": panel.id,
                "resource_slug": resource.get_slug() if resource is not None else "",
                "_resource": resource,
                "_panel": panel,
            },
        )
        if resource is not None:
            # So Resource.page_url / get_pages include the panel path prefix.
            resource._panel_path = panel.get_path()
        reg = f"orbit.{panel.id}.{getattr(resource, '__name__', 'page')}.{cls.__name__}"
        Conduit.register(reg, host)
        return host

    def get_resource(self) -> type[Any]:
        if type(self)._resource is None:
            raise RuntimeError(f"{type(self).__name__} has no bound resource")
        return type(self)._resource

    def get_panel(self) -> Any:
        return type(self)._panel


class ListRecordsHost(OrbitPageHost):
    """Index page host — table search/sort/tabs live on Conduit state."""

    records: list[dict[str, Any]] = []
    active_tab: str = ""
    table_search: str = ""
    table_sort: str = ""
    table_sort_direction: str = "asc"
    selected: list[str] = []

    def mount(self, **kwargs: Any) -> None:
        resource = self.get_resource()
        if "records" in kwargs and kwargs["records"] is not None:
            self.records = list(kwargs["records"])
        elif not self.records:
            getter = getattr(resource, "get_records", None)
            if callable(getter):
                self.records = list(getter())
            else:
                stored = getattr(resource, "records", None)
                if isinstance(stored, list):
                    self.records = list(stored)
        from almasix.orbit.panels.pages.resource_pages import ListRecords

        page = getattr(resource, "get_pages", lambda: {})()
        list_page = None
        if isinstance(page, dict):
            list_page = page.get("index")
        self._list_page = list_page or ListRecords
        if hasattr(self._list_page, "resource") and getattr(self._list_page, "resource", None) is None:
            self._list_page.resource = resource  # type: ignore[attr-defined]
        tabs = []
        if hasattr(self._list_page, "get_tabs"):
            try:
                bound_resource = resource

                class _Bound(self._list_page):  # type: ignore[misc, valid-type]
                    resource = bound_resource

                tabs = _Bound.get_tabs()
            except Exception:  # pragma: no cover - get_tabs implementations may raise
                tabs = []
        if tabs and not self.active_tab:
            self.active_tab = tabs[0].id

    def setTab(self, tab_id: str) -> None:
        self.active_tab = str(tab_id)

    def mountAction(self, name: str, **kwargs: Any) -> None:
        self.dispatch("orbit-mount-action", name=name, **kwargs)

    def render(self) -> str:
        resource = self.get_resource()

        class _Bound:
            pass

        from almasix.orbit.panels.pages.resource_pages import ListRecords

        class BoundList(ListRecords):
            pass

        BoundList.resource = resource  # type: ignore[misc]
        return BoundList.render(
            records=list(self.records),
            active_tab=self.active_tab or None,
            table_search=self.table_search,
            table_sort=self.table_sort,
            table_sort_direction=self.table_sort_direction,
        )


class CreateRecordHost(OrbitPageHost):
    data: dict[str, Any] = {}
    created_id: str | None = None

    def mount(self, **kwargs: Any) -> None:
        if isinstance(kwargs.get("data"), dict):
            self.data = dict(kwargs["data"])

    def create(self) -> None:
        self.dispatch("orbit-record-created", data=dict(self.data))
        self.created_id = str(self.data.get("id") or "new")

    def mountAction(self, name: str, **kwargs: Any) -> None:
        self.dispatch("orbit-mount-action", name=name, **kwargs)

    def render(self) -> str:
        from almasix.orbit.panels.pages.resource_pages import CreateRecord

        class Bound(CreateRecord):
            pass

        Bound.resource = self.get_resource()  # type: ignore[misc]
        return Bound.render(state=dict(self.data))


class EditRecordHost(OrbitPageHost):
    record_id: str = ""
    data: dict[str, Any] = {}

    def mount(self, **kwargs: Any) -> None:
        if kwargs.get("record_id") is not None:
            self.record_id = str(kwargs["record_id"])
        if isinstance(kwargs.get("data"), dict):
            self.data = dict(kwargs["data"])
        elif isinstance(kwargs.get("record"), dict):
            self.data = dict(kwargs["record"])
            self.record_id = str(self.data.get("id") or self.record_id)

    def save(self) -> None:
        self.dispatch("orbit-record-saved", record_id=self.record_id, data=dict(self.data))

    def mountAction(self, name: str, **kwargs: Any) -> None:
        self.dispatch("orbit-mount-action", name=name, **kwargs)

    def render(self) -> str:
        from almasix.orbit.panels.pages.resource_pages import EditRecord

        class Bound(EditRecord):
            pass

        Bound.resource = self.get_resource()  # type: ignore[misc]
        record = dict(self.data)
        if self.record_id and "id" not in record:
            record["id"] = self.record_id
        return Bound.render(record=record, state=dict(self.data))


class ViewRecordHost(OrbitPageHost):
    record_id: str = ""
    record: dict[str, Any] = {}

    def mount(self, **kwargs: Any) -> None:
        if kwargs.get("record_id") is not None:
            self.record_id = str(kwargs["record_id"])
        if isinstance(kwargs.get("record"), dict):
            self.record = dict(kwargs["record"])
            self.record_id = str(self.record.get("id") or self.record_id)

    def mountAction(self, name: str, **kwargs: Any) -> None:
        self.dispatch("orbit-mount-action", name=name, **kwargs)

    def render(self) -> str:
        from almasix.orbit.panels.pages.resource_pages import ViewRecord

        class Bound(ViewRecord):
            pass

        Bound.resource = self.get_resource()  # type: ignore[misc]
        data = dict(self.record)
        if self.record_id and "id" not in data:
            data["id"] = self.record_id
        return Bound.render(record=data)


class FormHost(ConduitHost):
    """Standalone form host for custom pages."""

    data: dict[str, Any] = {}
    _form_factory: ClassVar[Any] = None
    _title: ClassVar[str] = "Form"

    def mount(self, **kwargs: Any) -> None:
        if isinstance(kwargs.get("data"), dict):
            self.data = dict(kwargs["data"])

    def save(self) -> None:
        self.dispatch("orbit-form-saved", data=dict(self.data))

    def render(self) -> str:
        factory = type(self)._form_factory
        if factory is None:
            return '<div class="or-page"><p class="or-muted">No form configured.</p></div>'
        form = factory()
        form.fill(self.data)
        title = type(self)._title
        return (
            f'<div class="or-page or-page-form"><h1 class="or-page-title">{title}</h1>'
            f'<form class="or-form"{conduit_attr("submit", "save")}>{form.render(self.data)}'
            f'<div class="or-form-actions">'
            f'<button type="submit" class="or-btn or-btn-primary">Save</button>'
            f"</div></form></div>"
        )


class TableHost(ConduitHost):
    """Standalone table host for custom pages."""

    records: list[dict[str, Any]] = []
    table_search: str = ""
    _table_factory: ClassVar[Any] = None
    _title: ClassVar[str] = "Table"

    def mount(self, **kwargs: Any) -> None:
        if kwargs.get("records") is not None:
            self.records = list(kwargs["records"])

    def render(self) -> str:
        factory = type(self)._table_factory
        if factory is None:
            return '<div class="or-page"><p class="or-muted">No table configured.</p></div>'
        table = factory()
        table.records(self.records)
        if self.table_search:
            table.search(self.table_search)
        title = type(self)._title
        return (
            f'<div class="or-page or-page-table"><h1 class="or-page-title">{title}</h1>'
            f"{table.render()}</div>"
        )


class LoginHost(ConduitHost):
    """Auth login Conduit host (guest-accessible route)."""

    email: str = ""
    password: str = ""
    remember: bool = False
    error: str = ""
    panel_id: ClassVar[str] = "admin"
    _panel: ClassVar[Any] = None
    _page_cls: ClassVar[Any] = None

    async def authenticate(self) -> None:
        self.error = ""
        email = str(self.email or "").strip()
        password = str(self.password or "")
        if not email or not password:
            self.error = "Email and password are required."
            return

        remember = bool(self.remember)
        try:
            from almasix.auth import auth

            ok = await auth().attempt(
                {"email": email, "password": password},
                remember=remember,
            )
        except Exception as exc:  # pragma: no cover - provider/config failures
            self.error = str(exc) or "Sign in failed."
            return

        if not ok:
            self.error = "These credentials do not match our records."
            return

        try:
            from almasix.session.store import get_session

            if get_session() is None:
                self.error = (
                    "Signed in, but no session is available. "
                    "Add StartSession to the web middleware group."
                )
                return
        except Exception:
            pass

        panel = type(self)._panel
        home = "/"
        if panel is not None:
            home = panel.url() if hasattr(panel, "url") else str(panel.get_path() or "/")
            if not str(home).startswith("/"):
                home = f"/{home}"
        self.password = ""
        self.redirect(home)

    def render(self) -> str:
        from almasix.orbit.panels.auth import Login

        panel = type(self)._panel
        page_cls = type(self)._page_cls or Login
        brand = "Orbit"
        brand_logo = None
        brand_logo_dark = None
        brand_logo_only = False
        show_signup = False
        signup_url = None
        if panel is not None:
            brand = str(getattr(panel, "_brand", None) or brand)
            getter = getattr(panel, "get_brand_logo_url", None)
            if callable(getter):
                brand_logo = getter(dark=False)
                brand_logo_dark = getter(dark=True)
            else:
                brand_logo = getattr(panel, "_brand_logo", None)
                brand_logo_dark = getattr(panel, "_brand_logo_dark", None) or brand_logo
            brand_logo_only = bool(getattr(panel, "_brand_logo_only", False))
            if callable(getattr(panel, "signup_enabled", None)) and panel.signup_enabled():
                show_signup = True
                signup_url = panel.url("register")
        return page_cls.render(
            email=self.email,
            remember=self.remember,
            brand=brand,
            brand_logo=brand_logo,
            brand_logo_dark=brand_logo_dark,
            brand_logo_only=brand_logo_only,
            error=self._display_error(),
            show_signup=show_signup,
            signup_url=signup_url,
        )

    def _display_error(self) -> str | None:
        if self.error:
            return self.error
        bag = getattr(self, "errors", None) or {}
        for key in ("email", "password", "name", "password_confirmation", "_method"):
            msgs = bag.get(key)
            if msgs:
                return str(msgs[0])
        return None


class RegisterHost(ConduitHost):
    """Auth registration Conduit host (guest-accessible when signup is enabled)."""

    name: str = ""
    email: str = ""
    password: str = ""
    password_confirmation: str = ""
    error: str = ""
    panel_id: ClassVar[str] = "admin"
    _panel: ClassVar[Any] = None
    _page_cls: ClassVar[Any] = None

    async def register(self) -> None:
        self.error = ""
        name = str(self.name or "").strip()
        email = str(self.email or "").strip()
        password = str(self.password or "")
        confirm = str(self.password_confirmation or "")
        if not name or not email or not password:
            self.error = "Name, email, and password are required."
            return
        if password != confirm:
            self.error = "Passwords do not match."
            return

        try:
            user_model = self._user_model()
            from almasix.hashing import Hash

            if await self._email_taken(user_model, email):
                self.error = "An account with this email already exists."
                return

            create = getattr(user_model, "create", None)
            if create is None:
                self.error = "User model cannot create accounts."
                return
            result = create(
                {
                    "name": name,
                    "email": email,
                    "password": Hash.make(password),
                }
            )
            if hasattr(result, "__await__"):
                user = await result
            else:
                user = result
        except Exception as exc:
            from almasix.orbit.panels.db_errors import map_db_error

            self.error = map_db_error(exc)
            return

        try:
            from almasix.auth import auth

            await auth().login(user)
        except Exception as exc:
            self.error = str(exc) or "Account created, but sign-in failed."
            return

        panel = type(self)._panel
        home = "/"
        if panel is not None:
            home = panel.url() if hasattr(panel, "url") else str(panel.get_path() or "/")
            if not str(home).startswith("/"):
                home = f"/{home}"
        self.password = ""
        self.password_confirmation = ""
        self.redirect(home)

    def _user_model(self) -> type[Any]:
        import importlib

        path = "app.models.user.User"
        try:
            from almasix.config import config

            path = str(
                config("auth.providers.users.model", "app.models.user.User")
                or "app.models.user.User"
            )
        except Exception:
            pass
        module_name, _, class_name = path.rpartition(".")
        module = importlib.import_module(module_name)
        model = getattr(module, class_name, None)
        if model is None:
            raise AttributeError(f"{class_name} not found in {module_name}")
        return model

    @staticmethod
    async def _email_taken(user_model: type[Any], email: str) -> bool:
        """Best-effort existence check before INSERT (IntegrityError remains the race fallback).

        Almasix ORM ``QueryBuilder.first()`` is async — awaiting is required. Treating the
        bare coroutine as a row made every signup look like a duplicate email.
        """
        email_l = email.lower()

        async def _resolve(row: Any) -> Any:
            if hasattr(row, "__await__"):
                return await row
            return row

        try:
            where = getattr(user_model, "where", None)
            if callable(where):
                row = await _resolve(where("email", email).first())
                if row is not None:
                    return True
            query = getattr(user_model, "query", None)
            if callable(query):
                builder = query()
                where_b = getattr(builder, "where", None)
                if callable(where_b):
                    row = await _resolve(where_b("email", email).first())
                    if row is not None:
                        return True
            # In-memory / test models with a class-level records list
            records = getattr(user_model, "records", None)
            if isinstance(records, list):
                return any(
                    str(
                        getattr(r, "email", None)
                        or (r.get("email") if isinstance(r, dict) else "")
                        or ""
                    ).lower()
                    == email_l
                    for r in records
                )
        except Exception:
            return False
        return False

    def render(self) -> str:
        from almasix.orbit.panels.auth import Register

        panel = type(self)._panel
        page_cls = type(self)._page_cls or Register
        brand = "Orbit"
        brand_logo = None
        brand_logo_dark = None
        brand_logo_only = False
        login_url = "/login"
        if panel is not None:
            brand = str(getattr(panel, "_brand", None) or brand)
            getter = getattr(panel, "get_brand_logo_url", None)
            if callable(getter):
                brand_logo = getter(dark=False)
                brand_logo_dark = getter(dark=True)
            else:
                brand_logo = getattr(panel, "_brand_logo", None)
                brand_logo_dark = getattr(panel, "_brand_logo_dark", None) or brand_logo
            brand_logo_only = bool(getattr(panel, "_brand_logo_only", False))
            login_url = panel.url("login")
        return page_cls.render(
            name=self.name,
            email=self.email,
            brand=brand,
            brand_logo=brand_logo,
            brand_logo_dark=brand_logo_dark,
            brand_logo_only=brand_logo_only,
            error=self._display_error(),
            login_url=login_url,
        )

    def _display_error(self) -> str | None:
        if self.error:
            return self.error
        bag = getattr(self, "errors", None) or {}
        for key in ("email", "password", "name", "password_confirmation", "_method"):
            msgs = bag.get(key)
            if msgs:
                return str(msgs[0])
        return None
