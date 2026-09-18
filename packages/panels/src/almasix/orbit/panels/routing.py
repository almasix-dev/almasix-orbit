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
    RegisterHost,
    ViewRecordHost,
)
from almasix.orbit.panels.panel import Panel, PanelRegistry

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


def _auth_gate(panel: Panel, path: str | None, user: Any) -> Any | None:
    """Redirect to login when the panel requires auth and the path is not guest."""
    if not panel.login_enabled():
        return None
    if user is not None:
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

        async def action_with_record(request: Request, record_id: str) -> Any:
            path = _request_path(request)
            user = _current_user(panel) if auth_shell else None
            gated = _auth_gate(panel, path, user) if auth_shell else None
            if gated is not None:
                return gated
            extras = {**(params or {}), "record_id": record_id}
            instance = _instantiate_host(host_cls, extras)
            slot = await _embed_async(instance)
            body = panel.render_shell(
                slot,
                user=user,
                active_path=path,
                extra_head=_conduit_assets(),
                bare=not auth_shell,
            )
            return _html_response(body)

        return action_with_record

    async def action(request: Request) -> Any:
        path = _request_path(request)
        user = _current_user(panel) if auth_shell else None
        gated = _auth_gate(panel, path, user) if auth_shell else None
        if gated is not None:
            return gated
        instance = _instantiate_host(host_cls, params)
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


def mount_panel(router: Any, panel: Panel) -> None:
    """Mount list/create/edit/view (+ login) under the panel path prefix."""
    panel.load_discovered()
    prefix = panel.get_path().rstrip("/")
    if panel.get_path() == "/":
        prefix = ""

    middleware = [str(m) for m in panel.get_middleware()]

    def _add(uri: str, action: Any, *, name: str, mw: list[str] | None = None) -> None:
        full = f"{prefix}{uri}" if uri.startswith("/") else f"{prefix}/{uri}"
        if full == "":
            full = "/"
        router.add(
            ["GET"],
            full,
            action,
            name=name,
            middleware=mw if mw is not None else middleware,
        )

    resources = panel.get_resources()
    dash_cls = panel.dashboard_page() if panel.dashboard_enabled() else None

    if dash_cls is not None:

        async def dashboard_home(request: Request) -> Any:
            page_cls = dash_cls
            path = _request_path(request)
            user = _current_user(panel)
            gated = _auth_gate(panel, path, user)
            if gated is not None:
                return gated
            html_body = page_cls.render(
                brand=getattr(panel, "_brand", "Orbit"),
                user=user,
            )
            body = panel.render_shell(
                html_body,
                user=user,
                active_path=path,
                extra_head=_conduit_assets(),
            )
            return _html_response(body)

        _add("/", dashboard_home, name=f"orbit.{panel.id}.home")
    elif resources:
        home_host = ListRecordsHost.bind(panel=panel, resource=resources[0])
        _add("/", make_panel_page_action(panel, home_host), name=f"orbit.{panel.id}.home")
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

        _add("/", empty_home, name=f"orbit.{panel.id}.home")

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

        async def logout_action(request: Request) -> Any:
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
        list_host = ListRecordsHost.bind(panel=panel, resource=resource)
        create_host = CreateRecordHost.bind(panel=panel, resource=resource)
        edit_host = EditRecordHost.bind(panel=panel, resource=resource)
        view_host = ViewRecordHost.bind(panel=panel, resource=resource)

        _add(
            f"/{slug}",
            make_panel_page_action(panel, list_host),
            name=f"orbit.{panel.id}.{slug}.index",
        )
        _add(
            f"/{slug}/create",
            make_panel_page_action(panel, create_host),
            name=f"orbit.{panel.id}.{slug}.create",
        )
        _add(
            f"/{slug}/{{record_id}}/edit",
            make_panel_page_action(panel, edit_host, pass_record_id=True),
            name=f"orbit.{panel.id}.{slug}.edit",
        )
        _add(
            f"/{slug}/{{record_id}}",
            make_panel_page_action(panel, view_host, pass_record_id=True),
            name=f"orbit.{panel.id}.{slug}.view",
        )

    for page in panel.get_pages():
        # Dashboard home already owns ``/`` — skip a duplicate ``/dashboard`` mount.
        if dash_cls is not None and page is dash_cls:
            continue
        slug = getattr(page, "get_slug", lambda p=page: p.__name__.lower())()

        def _make_page_action(page_cls: Any) -> Any:
            async def page_action(request: Request) -> Any:
                path = _request_path(request)
                user = _current_user(panel)
                gated = _auth_gate(panel, path, user)
                if gated is not None:
                    return gated
                html_body = page_cls.render() if hasattr(page_cls, "render") else ""
                body = panel.render_shell(
                    html_body,
                    user=user,
                    active_path=path,
                    extra_head=_conduit_assets(),
                )
                return _html_response(body)

            return page_action

        _add(f"/{slug}", _make_page_action(page), name=f"orbit.{panel.id}.page.{slug}")


def mount_orbit_assets(router: Any) -> None:
    """Serve Orbit CSS/JS from the package.

    Almasix only auto-mounts ``public/{css,js,images,fonts,build}/``, so the
    Filament-style ``/vendor/orbit/*`` URLs need an explicit route (or a publish
    into ``public/css`` + ``public/js``).
    """
    css_path = _ASSETS / "css" / "orbit.css"
    js_path = _ASSETS / "js" / "orbit.js"

    async def orbit_css() -> Any:
        from almasix.http import Response

        body = css_path.read_text(encoding="utf-8") if css_path.is_file() else "/* missing orbit.css */"
        return Response(body, media_type="text/css; charset=utf-8")

    async def orbit_js() -> Any:
        from almasix.http import Response

        body = js_path.read_text(encoding="utf-8") if js_path.is_file() else "/* missing orbit.js */"
        return Response(body, media_type="application/javascript; charset=utf-8")

    try:
        uris = {getattr(r, "uri", None) for r in getattr(router, "routes", [])}
    except Exception:
        uris = set()
    if "/vendor/orbit/orbit.css" not in uris:
        router.add(["GET"], "/vendor/orbit/orbit.css", orbit_css, name="orbit.assets.css")
    if "/vendor/orbit/orbit.js" not in uris:
        router.add(["GET"], "/vendor/orbit/orbit.js", orbit_js, name="orbit.assets.js")


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
        for callback in panel._plugin_callbacks:
            callback(panel)
        mount_panel(router, panel)
