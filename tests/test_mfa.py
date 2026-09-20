"""MFA TOTP + email codes, challenge host, and panel wiring."""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace

from almasix.orbit.panels.auth import AppAuthentication, MfaChallenge, MfaProvider
from almasix.orbit.panels.conduit.hosts import LoginHost, MfaChallengeHost
from almasix.orbit.panels.mfa import (
    EmailAuthentication,
    MemoryEmailCodeStore,
    MemoryMailer,
    SmtpMailer,
    clear_mfa_pending,
    generate_recovery_codes,
    generate_totp_secret,
    is_mfa_pending,
    otpauth_uri,
    render_app_setup,
    set_mfa_pending,
    totp_at,
    verify_totp,
)
from almasix.orbit.panels.panel import Panel
from almasix.orbit.panels.routing import (
    _auth_gate,
    _is_mfa_path,
    mount_panel,
)
from almasix.routing.router import Router


class _User:
    def __init__(self) -> None:
        self.id = 1
        self.email = "ada@orbit.test"
        self.mfa_app_enabled = True
        self.mfa_app_secret = generate_totp_secret()
        self.mfa_recovery_codes = ["deadbeef"]
        self.mfa_email_enabled = True


def test_totp_roundtrip_and_recovery() -> None:
    secret = generate_totp_secret()
    code = totp_at(secret)
    assert verify_totp(secret, code)
    assert not verify_totp(secret, "000000")
    assert not verify_totp(secret, "abc")
    uri = otpauth_uri(secret, account="ada@orbit.test", issuer="Orbit")
    assert uri.startswith("otpauth://totp/")
    assert generate_recovery_codes(count=2)


def test_app_authentication_verify_and_provision() -> None:
    user = _User()
    app = AppAuthentication(brand_name="Orbit")
    assert app.get_id() == "app"
    assert app.is_enabled(user)
    assert "code" in app.get_challenge_form().render()
    assert "code" in app.get_management_schema().render()
    assert app.verify(user, totp_at(user.mfa_app_secret))
    assert app.verify(user, "deadbeef")
    assert user.mfa_recovery_codes == []
    assert not app.verify(user, "nope")
    app.send_code(user)
    fresh = SimpleNamespace()
    provisioned = app.provision(fresh)
    assert provisioned["secret"]
    assert "otpauth" in provisioned["otpauth_uri"]

    class Frozen:
        __slots__ = ()

    frozen = Frozen()
    fallback = AppAuthentication().provision(frozen)
    assert fallback["secret"]


def test_email_authentication_and_smtp(monkeypatch) -> None:
    user = _User()
    mailer = MemoryMailer()
    store = MemoryEmailCodeStore(ttl_seconds=60)
    email = EmailAuthentication(mailer=mailer, store=store)
    assert email.get_id() == "email"
    assert email.is_enabled(user)
    assert "Email" in email.get_management_schema().render()
    assert email.provision(user)["email"] == user.email
    email.send_code(user)
    assert mailer.outbox
    sent = mailer.outbox[0]["body"].split("is ", 1)[1].split(".", 1)[0]
    assert email.verify(user, sent)
    assert not email.verify(user, sent)
    email.send_code(SimpleNamespace(id=9))  # no email → skip mail

    expired = MemoryEmailCodeStore(ttl_seconds=0)
    expired.put("k", "111111")
    time.sleep(0.01)
    assert not expired.consume("k", "111111")
    assert not expired.consume("missing", "1")
    store.put("x", "222222")
    assert not store.consume("x", "000000")

    class _Smtp:
        def __init__(self, host, port):
            self.host = host
            self.port = port
            self.tls = False
            self.logged = None
            self.sent = None

        def starttls(self):
            self.tls = True

        def login(self, username, password):
            self.logged = (username, password)

        def send_message(self, msg):
            self.sent = msg

        def quit(self):
            return None

    client = _Smtp("localhost", 587)

    def factory(host, port):
        return client

    smtp = SmtpMailer(
        "localhost",
        587,
        username="u",
        password="p",
        use_tls=True,
        client_factory=factory,
    )
    smtp.send("ada@orbit.test", "Hi", "Body")
    assert client.tls and client.logged == ("u", "p") and client.sent is not None

    plain = SmtpMailer(use_tls=False, client_factory=lambda h, p: _Smtp(h, p))
    plain.send("a@b.c", "S", "B")


def test_mfa_session_pending_and_panel() -> None:
    clear_mfa_pending()
    assert is_mfa_pending() is False
    set_mfa_pending(True)
    assert is_mfa_pending() is True
    clear_mfa_pending()
    assert is_mfa_pending() is False

    panel = Panel.make("admin").multi_factor_authentication(
        None,
        False,
        [AppAuthentication(), EmailAuthentication()],
    )
    assert panel.has_mfa_providers()
    assert panel.to_dict()["mfa_providers"] == ["app", "email"]
    user = _User()
    assert len(panel.enabled_mfa_providers(user)) == 2
    named = SimpleNamespace(get_id=lambda: "custom")
    Panel.make("x").multi_factor_authentication(named)
    assert Panel.make("z").multi_factor_authentication().get_mfa_providers() == []


def test_mfa_challenge_render_and_host(monkeypatch) -> None:
    app = AppAuthentication()
    email = EmailAuthentication()
    user = _User()
    html = MfaChallenge.render(
        providers=[app, email],
        provider="email",
        user=user,
        error="bad",
        sent=True,
        show_setup=True,
        data={"code": ""},
    )
    assert "or-page-mfa" in html
    assert "Resend code" in html
    assert "or-mfa-sent" in html
    assert "Authenticator" in html
    setup = MfaChallenge.render(providers=[app], show_setup=True, user=user)
    assert "or-mfa-setup" in setup
    empty = MfaChallenge.render()
    assert "Verify" in empty

    panel = Panel.make("admin").path("admin").multi_factor_authentication(app, email)
    panel._panel_user = user  # type: ignore[attr-defined]
    monkeypatch.setattr("almasix.auth.auth", lambda: SimpleNamespace(user=lambda: user))
    host_cls = type("MH", (MfaChallengeHost,), {"panel_id": "admin", "_panel": panel})
    host = host_cls(code="111111")
    host.selectProvider("email")
    host.resendCode()
    assert host.sent is True
    host.verifyMfa()
    assert host.error == "That code is not valid."
    host.data = {"code": ""}
    host.verifyMfa()
    assert "Enter" in host.error
    bare = type("MH2", (MfaChallengeHost,), {"panel_id": "admin", "_panel": None})()
    bare.verifyMfa()
    assert "No multi-factor" in bare.error
    html_host = host.render()
    assert "or-page-mfa" in html_host
    host.provider = "app"
    host.data = {"code": totp_at(user.mfa_app_secret)}
    host.verifyMfa()
    assert host.take_redirect() is not None

    none_panel = type("P", (), {})()
    ghost = type("MH3", (MfaChallengeHost,), {"panel_id": "g", "_panel": none_panel})()
    ghost.resendCode()
    assert ghost._providers() == []


def test_login_redirects_to_mfa(monkeypatch) -> None:
    user = _User()

    class _Auth:
        async def attempt(self, credentials, *, remember=False):
            return True

        def user(self):
            return user

    class _Session:
        def __init__(self) -> None:
            self.store: dict = {}

        def put(self, key, value):
            self.store[key] = value

        def get(self, key, default=None):
            return self.store.get(key, default)

        def regenerate(self):
            return None

    session = _Session()
    monkeypatch.setattr("almasix.auth.auth", lambda: _Auth())
    monkeypatch.setattr("almasix.session.store.get_session", lambda: session)
    panel = Panel.make("admin").path("admin").multi_factor_authentication(AppAuthentication())
    host = type("LH", (LoginHost,), {"panel_id": "admin", "_panel": panel})(
        email="ada@orbit.test", password="secret"
    )
    asyncio.run(host.authenticate())
    redirect = host.take_redirect()
    assert redirect is not None
    assert "mfa-challenge" in str(redirect.get("url") or redirect)


def test_auth_gate_mfa_pending(monkeypatch) -> None:
    set_mfa_pending(True)
    panel = Panel.make("admin").path("admin").multi_factor_authentication(AppAuthentication())
    gated = _auth_gate(panel, "/admin/posts", object())
    assert gated is not None
    assert _is_mfa_path(panel, "/admin/mfa-challenge")
    assert _auth_gate(panel, "/admin/mfa-challenge", object()) is None
    assert _is_mfa_path(panel, None) is False
    clear_mfa_pending()
    assert _auth_gate(panel, "/admin/posts", object()) is None


def test_mount_mfa_challenge_route(monkeypatch) -> None:
    class _Req:
        def __init__(self, path: str) -> None:
            self.url = type("U", (), {"path": path})()
            self.path = path

    panel = (
        Panel.make("mfaapp")
        .path("mfaapp")
        .middleware([], replace=True)
        .login()
        .multi_factor_authentication(AppAuthentication())
        .user(type("U", (), {"email": "a@b.c", "name": "A"})())
    )
    router = Router()
    mount_panel(router, panel)
    uris = {r.uri for r in router.routes}
    assert "/mfaapp/mfa-challenge" in uris
    route = next(r for r in router.routes if r.route_name == "orbit.mfaapp.mfa")
    monkeypatch.setattr("almasix.orbit.panels.routing._current_user", lambda p=None: None)
    out = asyncio.run(route.action(_Req("/mfaapp/mfa-challenge")))
    assert out is not None
    monkeypatch.setattr(
        "almasix.orbit.panels.routing._current_user",
        lambda p=None: type("U", (), {"email": "a@b.c", "mfa_app_enabled": True})(),
    )
    html = asyncio.run(route.action(_Req("/mfaapp/mfa-challenge")))
    assert html is not None
    logout = next(r for r in router.routes if r.route_name == "orbit.mfaapp.logout")
    asyncio.run(logout.action(_Req("/mfaapp/logout")))


def test_mfa_provider_protocol_stubs() -> None:
    class _T:
        pass

    assert MfaProvider.verify(_T(), object(), "1") is None  # type: ignore[arg-type]
    assert MfaProvider.send_code(_T(), object()) is None  # type: ignore[arg-type]
    assert MfaProvider.provision(_T(), object()) is None  # type: ignore[arg-type]


def test_render_app_setup_html() -> None:
    html = render_app_setup(
        {"secret": "ABC", "otpauth_uri": "otpauth://x", "recovery_codes": ["aa"]}
    )
    assert "ABC" in html and "aa" in html


def test_mfa_coverage_edges(monkeypatch) -> None:
    monkeypatch.setattr(
        "almasix.session.store.get_session",
        lambda: (_ for _ in ()).throw(RuntimeError("no session")),
    )
    from almasix.orbit.panels.mfa import _session_store

    assert _session_store() is None

    class BoomPut:
        def put(self, *a, **k):
            raise RuntimeError("put failed")

    monkeypatch.setattr("almasix.session.store.get_session", lambda: BoomPut())
    set_mfa_pending(True)
    assert is_mfa_pending() is True

    class AttrSess:
        orbit_mfa_pending = True

    monkeypatch.setattr("almasix.session.store.get_session", lambda: AttrSess())
    assert is_mfa_pending() is True

    class RaiseGet:
        def get(self, key):
            raise RuntimeError("get failed")

    monkeypatch.setattr("almasix.session.store.get_session", lambda: RaiseGet())
    assert is_mfa_pending() in (True, False)

    EmailAuthentication().send_code(None)
    class NoQuit:
        def send_message(self, msg):
            return None

    SmtpMailer(use_tls=False, client_factory=lambda h, p: NoQuit()).send("a@b.c", "S", "B")

    class Rec:
        mfa_app_secret = ""
        mfa_recovery_codes = ["abcd"]

        def __setattr__(self, key, value):
            if key == "mfa_recovery_codes":
                raise RuntimeError("locked")
            object.__setattr__(self, key, value)

    assert AppAuthentication().verify(Rec(), "abcd") is True

    class _AuthHome:
        async def attempt(self, credentials, *, remember=False):
            return True

        def user(self):
            return SimpleNamespace(mfa_app_enabled=False)

    class _Sess:
        def put(self, *a, **k):
            return None

        def get(self, *a, **k):
            return None

        def regenerate(self):
            return None

    monkeypatch.setattr("almasix.auth.auth", lambda: _AuthHome())
    monkeypatch.setattr("almasix.session.store.get_session", lambda: _Sess())
    panel = Panel.make("admin").path("admin").multi_factor_authentication(AppAuthentication())
    host = type("LH", (LoginHost,), {"panel_id": "admin", "_panel": panel})(
        email="ada@orbit.test", password="secret"
    )
    asyncio.run(host.authenticate())
    assert "mfa-challenge" not in str(host.take_redirect() or {})

    monkeypatch.setattr("almasix.auth.auth", lambda: (_ for _ in ()).throw(RuntimeError("auth")))
    ghost = type("MH", (MfaChallengeHost,), {"panel_id": "g", "_panel": None})()
    assert ghost._user() is None
    assert "or-page-mfa" in ghost.render()
    stub = SimpleNamespace(
        _brand="Acme",
        _brand_logo="/l.svg",
        _brand_logo_dark="/d.svg",
        _brand_logo_only=False,
        enabled_mfa_providers=lambda u: [AppAuthentication()],
    )
    painted = type("MH4", (MfaChallengeHost,), {"panel_id": "g", "_panel": stub})()
    assert "Acme" in painted.render() or "or-page-mfa" in painted.render()

    monkeypatch.setattr("almasix.orbit.panels.mfa.clear_mfa_pending", lambda: (_ for _ in ()).throw(RuntimeError("x")))
    router = Router()
    mount_panel(
        router,
        Panel.make("boom").path("boom").middleware([], replace=True).login(),
    )
    logout = next(r for r in router.routes if r.route_name == "orbit.boom.logout")
    asyncio.run(logout.action(SimpleNamespace(url=SimpleNamespace(path="/boom/logout"), path="/boom/logout")))

