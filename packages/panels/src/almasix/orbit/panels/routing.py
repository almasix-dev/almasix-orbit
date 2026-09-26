"""Register Orbit Conduit hosts under each panel path prefix."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from almasix.http import Request
from almasix.orbit.panels.conduit.hosts import (
    CreateRecordHost,
    EditRecordHost,
    ListRecordsHost,
    LoginHost,
    MfaChallengeHost,
    RegisterHost,
    ViewRecordHost,
)
from almasix.orbit.panels.global_search import (
    collect_global_search_results,
    render_global_search_groups,
)
from almasix.orbit.panels.notification_routes import (
    handle_database_notifications,
    handle_live_broadcasts,
    panel_live_url,
    panel_notifications_url,
    read_json_body,
)
from almasix.orbit.panels.panel import Panel, PanelRegistry
from almasix.orbit.panels.uploads import (
    handle_serve_upload,
    handle_upload,
    handle_upload_delete,
    panel_upload_url,
)

_ASSETS = Path(__file__).resolve().parent.parent / "resources"


def _current_user(panel: Panel | None = None) -> Any:
    """Resolve Almasix Auth session user, else panel ``.user()`` / legacy ``demo_user``."""
    try:
        from almasix.auth import auth

        user = auth().user()
        if user is not None:
            return user
    except Exception:
        pass
    try:
        from almasix.auth import Auth  # type: ignore[attr-defined]

        user = Auth.user()  # type: ignore[misc]
        if user is not None:
            return user
    except Exception:
        pass
    if panel is not None:
        return getattr(panel, "_panel_user", None) or getattr(panel, "_demo_user", None)
    return None


def _redirect(url: str) -> Any:
    try:
        from almasix.http import redirect

        return redirect(url)
    except Exception:  # pragma: no cover
        from starlette.responses import RedirectResponse

        return RedirectResponse(url=url, status_code=302)


def _login_path(panel: Panel) -> str:
    return panel.url("login")


def _register_path(panel: Panel) -> str:
    return panel.url("register")


def _is_guest_path(panel: Panel, path: str | None) -> bool:
    if not path:
        return False
    normalized = path.rstrip("/") or "/"
    login = _login_path(panel).rstrip("/") or "/"
    if normalized == login or path.endswith("/login"):
        return True
    if panel.signup_enabled():
        register = _register_path(panel).rstrip("/") or "/"
        if normalized == register or path.endswith("/register"):
            return True
    return False


def _mfa_challenge_path(panel: Panel) -> str:
    return panel.url("mfa-challenge")


def _is_mfa_path(panel: Panel, path: str | None) -> bool:
    if not path:
        return False
    challenge = _mfa_challenge_path(panel).rstrip("/") or "/"
    normalized = path.rstrip("/") or "/"
    return normalized == challenge or path.endswith("/mfa-challenge")


def _auth_gate(panel: Panel, path: str | None, user: Any) -> Any | None:
    """Redirect to login when the panel requires auth and the path is not guest."""
    if not panel.login_enabled():
        return None
    if user is not None:
        from almasix.orbit.panels.mfa import is_mfa_pending

        if (
            panel.has_mfa_providers()
            and is_mfa_pending()
            and not _is_mfa_path(panel, path)
            and not _is_guest_path(panel, path)
        ):
            return _redirect(_mfa_challenge_path(panel))
        return None
    if _is_guest_path(panel, path):
        return None
    return _redirect(_login_path(panel))


def _html_response(body: str) -> Any:
    try:
        from almasix.http import html

        return html(body)
    except Exception:  # pragma: no cover
        from starlette.responses import HTMLResponse

        return HTMLResponse(body)


def _request_path(request: Request | None = None) -> str | None:
    if request is not None:
        url = getattr(request, "url", None)
        if url is not None and getattr(url, "path", None):
            return str(url.path)
        path = getattr(request, "path", None)
        if path:
            return str(path)
    try:
        from almasix.http import request as current_request

        req = current_request()
        url = getattr(req, "url", None)
        if url is not None and getattr(url, "path", None):
            return str(url.path)
    except Exception:
        pass
    return None


def _embed(component: Any) -> str:
    """Sync embed (tests / non-async callers). Prefer ``_embed_async`` in routes."""
    from almasix.conduit.routing import embed_component

    return embed_component(component)


async def _embed_async(component: Any) -> str:
    """Embed a Conduit host, awaiting async ``mount()`` (ORM-backed resources)."""
    import inspect

    from almasix.conduit.mechanism import (
        new_id,
        render_html,
        snapshot,
        wrap_root,
    )

    if getattr(component, "conduit_id", None) is None:
        component.conduit_id = new_id()
    if getattr(component, "lazy", False) or getattr(component, "defer", False):
        from almasix.conduit.mechanism import _embed_lazy

        return _embed_lazy(
            component,
            defer=bool(getattr(component, "defer", False) and not getattr(component, "lazy", False)),
        )

    mount = getattr(component, "mount", None)
    if callable(mount):
        result = mount()
        if inspect.iscoroutine(result):
            await result
    booted = getattr(component, "booted", None)
    if callable(booted):
        booted()
    snap = snapshot(component)
    html = render_html(component)
    return wrap_root(component, html, snap)


def _conduit_assets() -> str:
    try:
        from almasix.conduit.routing import conduit_assets_script

        return conduit_assets_script()
    except Exception:
        return ""


def _dashboard_page_filters(request: Request, page_cls: type) -> dict[str, Any]:
    """Collect dashboard filter values from query string (and optional session)."""
    filters: dict[str, Any] = {}
    try:
        qp = getattr(request, "query_params", None) or getattr(
            getattr(request, "url", None), "query", None
        )
        if hasattr(qp, "multi_items"):
            for key, value in qp.multi_items():
                filters[str(key)] = value
        elif hasattr(qp, "items") and not isinstance(qp, str):
            for key, value in qp.items():
                filters[str(key)] = value
    except Exception:
        pass
    if getattr(page_cls, "persists_filters_in_session", False):
        try:
            session = getattr(request, "session", None)
            if session is not None:
                stored = session.get("orbit_dashboard_filters")
                if isinstance(stored, dict):
                    filters = {**stored, **filters}
                    session["orbit_dashboard_filters"] = filters
        except Exception:
            pass
    return filters


def _instantiate_host(host_cls: type, extras: dict[str, Any] | None = None) -> Any:
    from almasix.conduit import Conduit

    name = getattr(host_cls, "_conduit_name", None) or host_cls.__name__
    try:
        for key, registered in Conduit.registry()._map.items():
            if registered is host_cls:
                name = key
                break
        else:
            Conduit.register(name, host_cls)
    except Exception:
        pass

    public = host_cls._public_property_names()
    payload = {k: v for k, v in (extras or {}).items() if k in public}
    return Conduit.component(name, **payload)


def _apply_tenant_slug(panel: Panel, slug: str | None, user: Any = None) -> None:
    """Resolve ``slug`` against panel tenancy and set the current tenant."""
    tenancy = panel.get_tenancy()
    if tenancy is None or not tenancy.is_enabled() or not slug:
        return
    found = tenancy.find_by_slug(str(slug))
    if found is None:
        # Also search user-resolved tenants (HasTenants).
        for t in tenancy.resolve_tenants(user=user, panel=panel):
            if t.slug == str(slug) or str(t.id) == str(slug):
                found = t
                break
    if found is None:
        return
    if user is not None:
        checker = getattr(user, "can_access_tenant", None)
        if callable(checker) and not checker(found):
            return
    tenancy.current(found)
    stamp = getattr(panel, "_stamp_tenant_paths", None)
    if callable(stamp):
        stamp(found)


def _tenant_path_prefix(panel: Panel) -> str:
    """``team/{tenant}`` or ``{tenant}`` fragment when route prefixes are enabled."""
    tenancy = panel.get_tenancy()
    if tenancy is None or not tenancy.is_enabled() or not tenancy.get_tenant_route_prefix():
        return ""
    return tenancy.path_prefix_for("{tenant}")


def make_panel_page_action(
    panel: Panel,
    host_cls: type,
    *,
    params: dict[str, Any] | None = None,
    auth_shell: bool = True,
    pass_record_id: bool = False,
):
    """Return a route action that embeds a Conduit host inside the panel shell."""

    if pass_record_id:

        async def action_with_record(
            request: Request,
            record_id: str,
            tenant: str | None = None,
        ) -> Any:
            path = _request_path(request)
            user = _current_user(panel) if auth_shell else None
            gated = _auth_gate(panel, path, user) if auth_shell else None
            if gated is not None:
                return gated
            _apply_tenant_slug(panel, tenant, user)
            extras = {**(params or {}), "record_id": record_id}
            if tenant:
                extras["tenant"] = tenant
            instance = _instantiate_host(host_cls, extras)
            slot = await _embed_async(instance)
            body = panel.render_shell(
                slot,
                user=user,
                active_path=path,
                extra_head=_conduit_assets(),
                bare=not auth_shell,
                record_title=_host_record_title(instance),
            )
            return _html_response(body)

        return action_with_record

    async def action(
        request: Request,
        tenant: str | None = None,
    ) -> Any:
        path = _request_path(request)
        user = _current_user(panel) if auth_shell else None
        gated = _auth_gate(panel, path, user) if auth_shell else None
        if gated is not None:
            return gated
        _apply_tenant_slug(panel, tenant, user)
        mount_params = dict(params or {})
        if tenant:
            mount_params["tenant"] = tenant
        instance = _instantiate_host(host_cls, mount_params or None)
        slot = await _embed_async(instance)
        body = panel.render_shell(
            slot,
            user=user,
            active_path=path,
            extra_head=_conduit_assets(),
            bare=not auth_shell,
        )
        return _html_response(body)

    return action


async def _upload_payload(request: Request | None) -> dict[str, Any]:
    """Normalize an upload (multipart) or delete (form field) request."""
    out: dict[str, Any] = {
        "resource": _form_param(request, "resource") or _query_param(request, "resource"),
        "field": _form_param(request, "field") or _query_param(request, "field"),
    }
    path = _form_param(request, "path") or _query_param(request, "path")
    intent = _form_param(request, "intent") or _query_param(request, "intent")
    if intent == "delete" or (path and not _request_file(request)):
        out["_delete"] = True
        out["path"] = path
        return out
    upload = _request_file(request)
    if upload is None:
        out["filename"] = ""
        out["data"] = b""
        return out
    out["filename"] = str(getattr(upload, "filename", "") or "file")
    read = getattr(upload, "read", None)
    data = await read() if callable(read) else b""
    out["data"] = data if isinstance(data, (bytes, bytearray)) else bytes(str(data), "utf-8")
    return out


def _request_file(request: Request | None) -> Any:
    if request is None:
        return None
    getter = getattr(request, "file", None)
    if not callable(getter):
        return None
    try:
        found = getter("file")
    except Exception:
        return None
    if isinstance(found, list):
        return found[0] if found else None
    return found


def _form_param(request: Request | None, name: str) -> str:
    """Read a submitted form value without assuming a single request API."""
    if request is None:
        return ""
    getter = getattr(request, "input", None)
    if callable(getter):
        try:
            value = getter(name)
        except Exception:
            value = None
        if value not in (None, ""):
            return str(value)
    return ""


def _json_response(payload: dict[str, Any]) -> Any:
    try:
        from almasix.http import json as json_response

        return json_response(payload)
    except Exception:  # pragma: no cover - framework fallback
        from starlette.responses import JSONResponse

        return JSONResponse(payload)


def _host_record_title(instance: Any) -> str | None:
    """Record title from a mounted view/edit host, for the breadcrumb leaf."""
    record = getattr(instance, "record", None)
    if not isinstance(record, dict) or not record:
        record = getattr(instance, "data", None)
    if not isinstance(record, dict) or not record:
        return None
    get_resource = getattr(instance, "get_resource", None)
    if not callable(get_resource):
        return None
    try:
        resource = get_resource()
        title = resource.get_record_title(record)
    except Exception:
        return None
    return str(title) if title else None


def _query_param(request: Request | None, name: str) -> str:
    """Read one query-string value across the supported request objects."""
    if request is None:
        return ""
    params = getattr(request, "query_params", None)
    if params is None:
        params = getattr(request, "query", None)
    if params is None:
        return ""
    getter = getattr(params, "get", None)
    value = getter(name) if callable(getter) else None
    return str(value or "")


async def _global_search_groups(panel: Panel, term: str, user: Any) -> list[dict[str, Any]]:
    """Load searchable records per resource, then group the matches."""
    from almasix.orbit.panels.conduit.hosts import (
        _orm_fetch_all,
        _resource_model,
        _resource_records,
    )

    records_by_resource: dict[Any, list[Any]] = {}
    for resource in panel.get_resources():
        searchable = getattr(resource, "is_globally_searchable", None)
        if not callable(searchable) or not searchable():
            continue
        model = _resource_model(resource)
        if model is not None:
            records_by_resource[resource] = await _orm_fetch_all(model)
        else:
            records_by_resource[resource] = _resource_records(resource)
    groups = collect_global_search_results(
        panel,
        term,
        user=user,
        records_by_resource=records_by_resource,
    )
    limit = getattr(panel, "_global_search_limit", 10)
    remaining = int(limit)
    trimmed: list[dict[str, Any]] = []
    for group in groups:
        if remaining <= 0:
            break
        results = list(group["results"])[:remaining]
        remaining -= len(results)
        trimmed.append({**group, "results": results})
    return trimmed


def mount_panel(router: Any, panel: Panel) -> None:
    """Mount list/create/edit/view (+ login) under the panel path prefix."""
    panel.load_discovered()
    prefix = panel.get_path().rstrip("/")
    if panel.get_path() == "/":
        prefix = ""

    middleware = [str(m) for m in panel.get_middleware()]
    auth_extra = [str(m) for m in panel.get_auth_middleware()]
    auth_middleware = list(middleware)
    for item in auth_extra:
        if item not in auth_middleware:
            auth_middleware.append(item)
    domain = panel.get_domain()

    def _add(
        uri: str,
        action: Any,
        *,
        name: str,
        mw: list[str] | None = None,
    ) -> None:
        # Empty ``uri`` (root panel home) uses concat so ``full == ""`` can normalize to ``/``.
        if uri.startswith("/") or uri == "":
            full = f"{prefix}{uri}"
        else:
            full = f"{prefix}/{uri}"
        if full == "":
            full = "/"
        # Guest routes pass ``mw=`` explicitly (e.g. ``["web"]``); others use auth stack.
        stack = mw if mw is not None else auth_middleware
        router.add(
            ["GET"],
            full,
            action,
            name=name,
            middleware=stack,
            domain=domain,
        )

    home_uri = "/" if prefix else ""

    resources = panel.get_resources()
    dash_cls = panel.dashboard_page() if panel.dashboard_enabled() else None

    if dash_cls is not None:

        async def dashboard_home(request: Request, tenant: str | None = None) -> Any:
            page_cls = dash_cls
            path = _request_path(request)
            user = _current_user(panel)
            gated = _auth_gate(panel, path, user)
            if gated is not None:
                return gated
            _apply_tenant_slug(panel, tenant, user)
            page_filters = _dashboard_page_filters(request, page_cls)
            html_body = page_cls.render(
                brand=getattr(panel, "_brand", "Orbit"),
                user=user,
                panel=panel,
                tenant=panel.get_tenant(),
                page_filters=page_filters,
                request=request,
            )
            body = panel.render_shell(
                html_body,
                user=user,
                active_path=path,
                extra_head=_conduit_assets(),
            )
            return _html_response(body)

        _add(home_uri, dashboard_home, name=f"orbit.{panel.id}.home")
        tenant_prefix = _tenant_path_prefix(panel)
        if tenant_prefix:
            _add(
                f"/{tenant_prefix}" if not tenant_prefix.startswith("/") else tenant_prefix,
                dashboard_home,
                name=f"orbit.{panel.id}.home.tenant",
            )
    elif resources:
        home_host = ListRecordsHost.bind(panel=panel, resource=resources[0])
        _add(
            home_uri,
            make_panel_page_action(panel, home_host),
            name=f"orbit.{panel.id}.home",
        )
    else:

        async def empty_home(request: Request) -> Any:
            path = _request_path(request)
            user = _current_user(panel)
            gated = _auth_gate(panel, path, user)
            if gated is not None:
                return gated
            body = panel.render_shell(
                '<div class="or-page"><h1 class="or-page-title">Dashboard</h1>'
                '<p class="or-muted">Register resources on this panel.</p></div>',
                user=user,
                active_path=path,
                extra_head=_conduit_assets(),
            )
            return _html_response(body)

        _add(home_uri, empty_home, name=f"orbit.{panel.id}.home")

    if panel.uploads_enabled():

        async def upload_action(request: Request) -> Any:
            payload = await _upload_payload(request)
            if payload.get("_delete"):
                result = await handle_upload_delete(
                    panel,
                    resource=payload.get("resource", ""),
                    field=payload.get("field", ""),
                    path=payload.get("path", ""),
                )
            else:
                result = await handle_upload(
                    panel,
                    resource=payload.get("resource", ""),
                    field=payload.get("field", ""),
                    filename=payload.get("filename", ""),
                    data=payload.get("data", b""),
                )
            return _json_response(result)

        router.add(
            ["POST"],
            panel_upload_url(panel),
            upload_action,
            name=f"orbit.{panel.id}.upload",
            middleware=auth_middleware,
            domain=domain,
        )

    if panel.database_notifications_enabled():

        async def database_notifications_action(request: Request) -> Any:
            method = str(getattr(request, "method", "GET") or "GET")
            payload: dict[str, Any] = {}
            if method.upper() == "POST":
                payload = await read_json_body(request)
            return _json_response(
                handle_database_notifications(
                    panel,
                    user=_current_user(panel),
                    method=method,
                    payload=payload,
                )
            )

        router.add(
            ["GET", "POST"],
            panel_notifications_url(panel),
            database_notifications_action,
            name=f"orbit.{panel.id}.database-notifications",
            middleware=auth_middleware,
            domain=domain,
        )

    if panel.live_broadcasts_enabled():

        async def live_broadcasts_action(request: Request) -> Any:
            return _json_response(
                handle_live_broadcasts(panel, since=_query_param(request, "since"))
            )

        router.add(
            ["GET"],
            panel_live_url(panel),
            live_broadcasts_action,
            name=f"orbit.{panel.id}.live",
            middleware=auth_middleware,
            domain=domain,
        )

    if panel.has_global_search():

        async def global_search_action(request: Request) -> Any:
            user = _current_user(panel)
            term = _query_param(request, "search")
            groups = await _global_search_groups(panel, term, user)
            return _html_response(render_global_search_groups(groups))

        _add(
            "/global-search",
            global_search_action,
            name=f"orbit.{panel.id}.global-search",
        )

    if panel.login_enabled():
        from almasix.conduit import Conduit

        login_page = panel.login_page()
        login_host = type(
            f"LoginHost_{panel.id}",
            (LoginHost,),
            {
                "panel_id": panel.id,
                "_panel": panel,
                "_page_cls": login_page,
            },
        )
        Conduit.register(f"orbit.{panel.id}.login", login_host)
        # Always ``web`` (session/CSRF) — never panel ``auth`` middleware, or guests
        # cannot reach the login form.
        _add(
            "/login",
            make_panel_page_action(panel, login_host, auth_shell=False),
            name=f"orbit.{panel.id}.login",
            mw=["web"],
        )

        if panel.has_mfa_providers():
            mfa_host = type(
                f"MfaChallengeHost_{panel.id}",
                (MfaChallengeHost,),
                {
                    "panel_id": panel.id,
                    "_panel": panel,
                },
            )
            Conduit.register(f"orbit.{panel.id}.mfa", mfa_host)

            async def mfa_action(request: Request) -> Any:
                path = _request_path(request)
                user = _current_user(panel)
                if user is None:
                    return _redirect(_login_path(panel))
                instance = _instantiate_host(mfa_host, {})
                slot = await _embed_async(instance)
                body = panel.render_shell(
                    slot,
                    user=user,
                    active_path=path,
                    extra_head=_conduit_assets(),
                    bare=True,
                )
                return _html_response(body)

            _add(
                "/mfa-challenge",
                mfa_action,
                name=f"orbit.{panel.id}.mfa",
                mw=["web"],
            )

        async def logout_action(request: Request) -> Any:
            try:
                from almasix.orbit.panels.mfa import clear_mfa_pending

                clear_mfa_pending()
            except Exception:
                pass
            try:
                from almasix.auth import auth

                await auth().logout()
            except Exception:
                pass
            return _redirect(_login_path(panel))

        _add(
            "/logout",
            logout_action,
            name=f"orbit.{panel.id}.logout",
            mw=["web"],
        )

    if panel.signup_enabled():
        from almasix.conduit import Conduit

        signup_page = panel.signup_page()
        register_host = type(
            f"RegisterHost_{panel.id}",
            (RegisterHost,),
            {
                "panel_id": panel.id,
                "_panel": panel,
                "_page_cls": signup_page,
            },
        )
        Conduit.register(f"orbit.{panel.id}.register", register_host)
        _add(
            "/register",
            make_panel_page_action(panel, register_host, auth_shell=False),
            name=f"orbit.{panel.id}.register",
            mw=["web"],
        )

    for resource in resources:
        slug = resource.get_slug()
        # Stamp panel path so get_pages() / page_url() include prefixes.
        resource._panel_path = panel.get_path()  # type: ignore[attr-defined]
        get_cluster = getattr(resource, "get_cluster", None)
        cluster = (
            get_cluster()
            if callable(get_cluster)
            else getattr(resource, "cluster", None)
        )
        cluster_prefix = ""
        if cluster is not None:
            if isinstance(cluster, str):
                cluster_prefix = cluster.strip().strip("/")
            else:
                cluster_prefix = str(cluster.path_prefix()).strip("/")
        resource_base = f"{cluster_prefix}/{slug}" if cluster_prefix else slug
        tenant_prefix = _tenant_path_prefix(panel)
        if tenant_prefix:
            resource_base = f"{tenant_prefix}/{resource_base}"

        list_host = ListRecordsHost.bind(panel=panel, resource=resource)
        create_host = CreateRecordHost.bind(panel=panel, resource=resource)
        edit_host = EditRecordHost.bind(panel=panel, resource=resource)
        view_host = ViewRecordHost.bind(panel=panel, resource=resource)

        _add(
            f"{resource_base}",
            make_panel_page_action(panel, list_host),
            name=f"orbit.{panel.id}.{slug}.index",
        )
        _add(
            f"{resource_base}/create",
            make_panel_page_action(panel, create_host),
            name=f"orbit.{panel.id}.{slug}.create",
        )
        _add(
            f"{resource_base}/{{record_id}}/edit",
            make_panel_page_action(panel, edit_host, pass_record_id=True),
            name=f"orbit.{panel.id}.{slug}.edit",
        )
        _add(
            f"{resource_base}/{{record_id}}",
            make_panel_page_action(panel, view_host, pass_record_id=True),
            name=f"orbit.{panel.id}.{slug}.view",
        )

    for page in panel.get_pages():
        # Dashboard home already owns ``/`` — skip a duplicate ``/dashboard`` mount.
        if dash_cls is not None and page is dash_cls:
            continue
        page._panel_path = panel.get_path()  # type: ignore[attr-defined]
        get_slug = getattr(page, "get_slug", None)
        slug = get_slug() if callable(get_slug) else page.__name__.lower()
        get_cluster = getattr(page, "get_cluster", None)
        cluster = (
            get_cluster()
            if callable(get_cluster)
            else getattr(page, "cluster", None)
        )
        cluster_prefix = ""
        if cluster is not None:
            if isinstance(cluster, str):
                cluster_prefix = cluster.strip().strip("/")
            else:
                cluster_prefix = str(cluster.path_prefix()).strip("/")
        page_base = f"{cluster_prefix}/{slug}" if cluster_prefix else slug
        tenant_prefix = _tenant_path_prefix(panel)
        if tenant_prefix:
            page_base = f"{tenant_prefix}/{page_base}"

        def _make_page_action(page_cls: Any) -> Any:
            async def page_action(
                request: Request,
                tenant: str | None = None,
            ) -> Any:
                path = _request_path(request)
                user = _current_user(panel)
                gated = _auth_gate(panel, path, user)
                if gated is not None:
                    return gated
                _apply_tenant_slug(panel, tenant, user)
                html_body = (
                    page_cls.render(panel=panel, user=user, tenant=panel.get_tenant())
                    if hasattr(page_cls, "render")
                    else ""
                )
                body = panel.render_shell(
                    html_body,
                    user=user,
                    active_path=path,
                    extra_head=_conduit_assets(),
                )
                return _html_response(body)

            return page_action

        _add(
            f"{page_base}",
            _make_page_action(page),
            name=f"orbit.{panel.id}.page.{slug}",
        )

    # Tenant registration / profile pages (when enabled).
    tenancy = panel.get_tenancy()
    if tenancy is not None and tenancy.is_enabled():
        reg_page = tenancy.registration_page()
        if reg_page is not None:
            reg_slug = getattr(reg_page, "get_slug", lambda: "new")()
            tenant_prefix = _tenant_path_prefix(panel)

            async def tenant_register_action(
                request: Request,
                tenant: str | None = None,
            ) -> Any:
                path = _request_path(request)
                user = _current_user(panel)
                gated = _auth_gate(panel, path, user)
                if gated is not None:
                    return gated
                _apply_tenant_slug(panel, tenant, user)
                html_body = reg_page.render(
                    panel=panel, user=user, tenant=panel.get_tenant()
                )
                return _html_response(
                    panel.render_shell(
                        html_body,
                        user=user,
                        active_path=path,
                        extra_head=_conduit_assets(),
                    )
                )

            _add(
                reg_slug,
                tenant_register_action,
                name=f"orbit.{panel.id}.tenant.register",
            )

        profile_page = tenancy.profile_page()
        if profile_page is not None:
            profile_slug = getattr(profile_page, "get_slug", lambda: "profile")()
            tenant_prefix = _tenant_path_prefix(panel)
            profile_uri = (
                f"{tenant_prefix}/{profile_slug}" if tenant_prefix else profile_slug
            )

            async def tenant_profile_action(
                request: Request,
                tenant: str | None = None,
            ) -> Any:
                path = _request_path(request)
                user = _current_user(panel)
                gated = _auth_gate(panel, path, user)
                if gated is not None:
                    return gated
                _apply_tenant_slug(panel, tenant, user)
                html_body = profile_page.render(
                    panel=panel, user=user, tenant=panel.get_tenant()
                )
                return _html_response(
                    panel.render_shell(
                        html_body,
                        user=user,
                        active_path=path,
                        extra_head=_conduit_assets(),
                    )
                )

            _add(
                profile_uri,
                tenant_profile_action,
                name=f"orbit.{panel.id}.tenant.profile",
            )

        billing_page = tenancy.billing_page()
        if billing_page is not None:
            billing_slug = getattr(billing_page, "get_slug", lambda: "billing")()
            tenant_prefix = _tenant_path_prefix(panel)
            billing_uri = (
                f"{tenant_prefix}/{billing_slug}" if tenant_prefix else billing_slug
            )

            async def tenant_billing_action(
                request: Request,
                tenant: str | None = None,
            ) -> Any:
                path = _request_path(request)
                user = _current_user(panel)
                gated = _auth_gate(panel, path, user)
                if gated is not None:
                    return gated
                _apply_tenant_slug(panel, tenant, user)
                method = str(getattr(request, "method", "GET") or "GET")
                if method.upper() == "POST":
                    payload = await read_json_body(request)
                    plan_id = str(
                        payload.get("plan_id")
                        or payload.get("plan")
                        or _form_param(request, "plan_id")
                        or _query_param(request, "plan_id")
                        or ""
                    )
                    handler = getattr(billing_page, "handle_subscribe", None)
                    if callable(handler) and plan_id:
                        try:
                            handler(
                                plan_id,
                                panel=panel,
                                user=user,
                                tenant=panel.get_tenant(),
                            )
                        except Exception:
                            pass
                html_body = billing_page.render(
                    panel=panel, user=user, tenant=panel.get_tenant()
                )
                return _html_response(
                    panel.render_shell(
                        html_body,
                        user=user,
                        active_path=path,
                        extra_head=_conduit_assets(),
                    )
                )

            if billing_uri.startswith("/") or billing_uri == "":
                billing_full = f"{prefix}{billing_uri}"
            else:
                billing_full = f"{prefix}/{billing_uri}" if prefix else f"/{billing_uri}"
            if billing_full == "":
                billing_full = "/"
            router.add(
                ["GET", "POST"],
                billing_full,
                tenant_billing_action,
                name=f"orbit.{panel.id}.tenant.billing",
                middleware=auth_middleware,
                domain=domain,
            )


def mount_orbit_assets(router: Any) -> None:
    """Serve Orbit CSS/JS from the package.

    Almasix only auto-mounts ``public/{css,js,images,fonts,build}/``, so the
    ``/vendor/orbit/*`` URLs need an explicit route (or a publish
    into ``public/css`` + ``public/js``).
    """
    css_path = _ASSETS / "css" / "orbit.css"
    js_path = _ASSETS / "js" / "orbit.js"
    datepicker_js_path = _ASSETS / "js" / "orbit-datepicker.js"
    vendor_dir = _ASSETS / "vendor"

    async def orbit_css() -> Any:
        from almasix.http import Response

        body = css_path.read_text(encoding="utf-8") if css_path.is_file() else "/* missing orbit.css */"
        return Response(body, media_type="text/css; charset=utf-8")

    async def orbit_js() -> Any:
        from almasix.http import Response

        body = js_path.read_text(encoding="utf-8") if js_path.is_file() else "/* missing orbit.js */"
        return Response(body, media_type="application/javascript; charset=utf-8")

    async def orbit_datepicker_js() -> Any:
        from almasix.http import Response

        body = (
            datepicker_js_path.read_text(encoding="utf-8")
            if datepicker_js_path.is_file()
            else "/* missing orbit-datepicker.js */"
        )
        return Response(body, media_type="application/javascript; charset=utf-8")

    def _vendor_js(filename: str):
        async def serve() -> Any:
            from almasix.http import Response

            path = vendor_dir / filename
            body = path.read_text(encoding="utf-8") if path.is_file() else f"/* missing {filename} */"
            return Response(body, media_type="application/javascript; charset=utf-8")

        return serve

    def _vendor_css(filename: str, *, missing: str):
        async def serve() -> Any:
            from almasix.http import Response

            path = vendor_dir / filename
            body = path.read_text(encoding="utf-8") if path.is_file() else missing
            return Response(body, media_type="text/css; charset=utf-8")

        return serve

    try:
        uris = {getattr(r, "uri", None) for r in getattr(router, "routes", [])}
    except Exception:
        uris = set()
    if "/vendor/orbit/orbit.css" not in uris:
        router.add(["GET"], "/vendor/orbit/orbit.css", orbit_css, name="orbit.assets.css")
    if "/vendor/orbit/orbit.js" not in uris:
        router.add(["GET"], "/vendor/orbit/orbit.js", orbit_js, name="orbit.assets.js")
    if "/vendor/orbit/orbit-datepicker.js" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/orbit-datepicker.js",
            orbit_datepicker_js,
            name="orbit.assets.datepicker.js",
        )
    if "/vendor/orbit/chart.umd.min.js" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/chart.umd.min.js",
            _vendor_js("chart.umd.min.js"),
            name="orbit.assets.chartjs",
        )
    if "/vendor/orbit/apexcharts.min.js" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/apexcharts.min.js",
            _vendor_js("apexcharts.min.js"),
            name="orbit.assets.apex",
        )
    if "/vendor/orbit/filepond.bundle.min.js" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/filepond.bundle.min.js",
            _vendor_js("filepond.bundle.min.js"),
            name="orbit.assets.filepond.js",
        )
    if "/vendor/orbit/flowbite-datepicker.min.js" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/flowbite-datepicker.min.js",
            _vendor_js("flowbite-datepicker.min.js"),
            name="orbit.assets.flowbite.datepicker.js",
        )

    if "/vendor/orbit/cropper.min.js" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/cropper.min.js",
            _vendor_js("cropper.min.js"),
            name="orbit.assets.cropper.js",
        )
    if "/vendor/orbit/cropper.min.css" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/cropper.min.css",
            _vendor_css(
                "cropper.min.css",
                missing="/* missing cropper.min.css */",
            ),
            name="orbit.assets.cropper.css",
        )
    if "/vendor/orbit/filepond.bundle.min.css" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/filepond.bundle.min.css",
            _vendor_css(
                "filepond.bundle.min.css",
                missing="/* missing filepond.bundle.min.css */",
            ),
            name="orbit.assets.filepond.css",
        )
    rich_dir = _ASSETS / "js" / "rich-editor"

    async def orbit_rich_editor(file: str = "") -> Any:
        from almasix.http import Response

        name = Path(file).name
        if name != file or not name.endswith((".js", ".css")):
            return Response("Not found", status_code=404)
        path = rich_dir / name
        if not path.is_file():
            return Response("Not found", status_code=404)
        media = "text/css; charset=utf-8" if name.endswith(".css") else "text/javascript; charset=utf-8"
        return Response(path.read_text(encoding="utf-8"), media_type=media)

    if "/vendor/orbit/rich-editor/{file}" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/rich-editor/{file}",
            orbit_rich_editor,
            name="orbit.assets.rich_editor",
        )

    if "/vendor/orbit/flowbite-datepicker.min.css" not in uris:
        router.add(
            ["GET"],
            "/vendor/orbit/flowbite-datepicker.min.css",
            _vendor_css(
                "flowbite-datepicker.min.css",
                missing="/* missing flowbite-datepicker.min.css */",
            ),
            name="orbit.assets.flowbite.datepicker.css",
        )
    if "/orbit-uploads/{path:path}" not in uris:
        async def orbit_memory_upload(path: str = "") -> Any:
            return await handle_serve_upload(path)

        router.add(
            ["GET"],
            "/orbit-uploads/{path:path}",
            orbit_memory_upload,
            name="orbit.assets.memory.upload",
        )


def mount_registered_panels(app: Any) -> None:
    """Mount every panel in the registry onto the application router."""
    try:
        registry = app.make(PanelRegistry)
    except Exception:
        return
    router = getattr(app, "router", None)
    if router is None:
        try:
            from almasix.routing import get_router

            router = get_router()
        except Exception:
            return
    try:
        mount_orbit_assets(router)
    except Exception:  # pragma: no cover
        pass
    for panel in registry.all():
        panel.run_plugins()
        mount_panel(router, panel)
