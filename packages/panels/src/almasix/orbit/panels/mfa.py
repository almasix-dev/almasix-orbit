
"""MFA providers — authenticator TOTP and emailed one-time codes."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import time
from collections.abc import Callable
from email.message import EmailMessage
from typing import Any, Protocol

from almasix.orbit.forms.components import OneTimeCodeInput, TextInput
from almasix.orbit.forms.form import Form

MFA_PENDING_KEY = "orbit_mfa_pending"
_FALLBACK_PENDING: dict[str, Any] = {}


class MfaProvider(Protocol):
    """Host implements TOTP/email MFA; Orbit supplies challenge schema hooks."""

    def get_id(self) -> str: ...

    def is_enabled(self, user: Any) -> bool: ...

    def get_management_schema(self) -> Form: ...

    def get_challenge_form(self) -> Form: ...

    def verify(self, user: Any, code: str) -> bool: ...

    def send_code(self, user: Any) -> None: ...

    def provision(self, user: Any) -> dict[str, Any]: ...


def generate_totp_secret(*, nbytes: int = 20) -> str:
    """Return a base32 secret suitable for authenticator apps."""
    return base64.b32encode(secrets.token_bytes(nbytes)).decode("ascii").rstrip("=")


def totp_at(secret: str, timestamp: int | None = None, *, digits: int = 6, period: int = 30) -> str:
    """RFC 6238 TOTP for ``secret`` (base32, padding optional)."""
    padded = secret.upper() + ("=" * ((8 - len(secret.upper()) % 8) % 8))
    key = base64.b32decode(padded, casefold=True)
    counter = int((time.time() if timestamp is None else timestamp) // period)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10**digits)).zfill(digits)


def verify_totp(secret: str, code: str, *, window: int = 1, digits: int = 6, period: int = 30) -> bool:
    """Accept the current TOTP plus ``window`` periods on either side."""
    cleaned = "".join(ch for ch in str(code) if ch.isdigit())
    if len(cleaned) != digits:
        return False
    now = int(time.time())
    for step in range(-window, window + 1):
        if hmac.compare_digest(totp_at(secret, now + step * period, digits=digits, period=period), cleaned):
            return True
    return False


def otpauth_uri(secret: str, *, account: str, issuer: str, period: int = 30, digits: int = 6) -> str:
    from urllib.parse import quote

    label = quote(f"{issuer}:{account}")
    issuer_q = quote(issuer)
    return (
        f"otpauth://totp/{label}?secret={secret}&issuer={issuer_q}"
        f"&period={period}&digits={digits}"
    )


def generate_recovery_codes(*, count: int = 8) -> list[str]:
    return [secrets.token_hex(4) for _ in range(count)]


def _session_store() -> Any | None:
    try:
        from almasix.session.store import get_session

        return get_session()
    except Exception:
        return None


def set_mfa_pending(value: bool) -> None:
    session = _session_store()
    if session is not None and hasattr(session, "put"):
        try:
            session.put(MFA_PENDING_KEY, bool(value))
            return
        except Exception:
            pass
    _FALLBACK_PENDING[MFA_PENDING_KEY] = bool(value)


def is_mfa_pending() -> bool:
    session = _session_store()
    if session is not None:
        try:
            if hasattr(session, "get"):
                return bool(session.get(MFA_PENDING_KEY))
            getter = getattr(session, MFA_PENDING_KEY, None)
            if getter is not None:
                return bool(getter)
        except Exception:
            pass
    return bool(_FALLBACK_PENDING.get(MFA_PENDING_KEY))


def clear_mfa_pending() -> None:
    set_mfa_pending(False)


class MemoryMailer:
    """Collect outbound MFA messages for tests and local demos."""

    def __init__(self) -> None:
        self.outbox: list[dict[str, str]] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.outbox.append({"to": to, "subject": subject, "body": body})


class SmtpMailer:
    """Send MFA mail through SMTP. Inject ``client_factory`` in tests."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 587,
        *,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
        from_address: str = "orbit@localhost",
        client_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.from_address = from_address
        self.client_factory = client_factory

    def send(self, to: str, subject: str, body: str) -> None:
        import smtplib

        msg = EmailMessage()
        msg["From"] = self.from_address
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        factory = self.client_factory or smtplib.SMTP
        client = factory(self.host, self.port)
        try:
            if self.use_tls and hasattr(client, "starttls"):
                client.starttls()
            if self.username:
                client.login(self.username, self.password or "")
            client.send_message(msg)
        finally:
            quit = getattr(client, "quit", None)
            if callable(quit):
                quit()


class MemoryEmailCodeStore:
    """In-memory emailed codes: ``{user_key: (code, expires_at)}``."""

    def __init__(self, *, ttl_seconds: int = 600) -> None:
        self.ttl_seconds = ttl_seconds
        self._codes: dict[str, tuple[str, float]] = {}

    def put(self, key: str, code: str) -> None:
        self._codes[key] = (code, time.time() + self.ttl_seconds)

    def consume(self, key: str, code: str) -> bool:
        row = self._codes.get(key)
        if row is None:
            return False
        stored, expires = row
        if time.time() > expires:
            self._codes.pop(key, None)
            return False
        if not hmac.compare_digest(str(stored), str(code)):
            return False
        self._codes.pop(key, None)
        return True


def _user_key(user: Any) -> str:
    if user is None:
        return "anon"
    return str(getattr(user, "id", None) or getattr(user, "email", None) or id(user))


def _user_email(user: Any) -> str:
    return str(getattr(user, "email", None) or "")


class AppAuthentication:
    """TOTP authenticator-app provider. Host persists secret / enabled flags on the user."""

    def __init__(self, *, brand_name: str = "Orbit", code_expiry_seconds: int = 30) -> None:
        self.brand_name = brand_name
        self.code_expiry_seconds = code_expiry_seconds

    def get_id(self) -> str:
        return "app"

    def is_enabled(self, user: Any) -> bool:
        return bool(getattr(user, "mfa_app_enabled", False))

    def get_management_schema(self) -> Form:
        return Form.make("mfa_app").schema(
            [TextInput.make("code").label("Authenticator code").required()]
        )

    def get_challenge_form(self) -> Form:
        return Form.make("mfa_challenge").schema(
            [
                OneTimeCodeInput.make("code")
                .label("Authentication code")
                .max_length(6)
                .required()
            ]
        )

    def provision(self, user: Any) -> dict[str, Any]:
        secret = str(getattr(user, "mfa_app_secret", None) or "")
        if not secret:
            secret = generate_totp_secret()
            try:
                user.mfa_app_secret = secret
            except Exception:
                pass
        account = _user_email(user) or "user"
        codes = list(getattr(user, "mfa_recovery_codes", None) or generate_recovery_codes())
        try:
            user.mfa_recovery_codes = codes
        except Exception:
            pass
        return {
            "secret": secret,
            "otpauth_uri": otpauth_uri(secret, account=account, issuer=self.brand_name),
            "recovery_codes": codes,
        }

    def verify(self, user: Any, code: str) -> bool:
        secret = str(getattr(user, "mfa_app_secret", None) or "")
        cleaned = "".join(ch for ch in str(code) if ch.isalnum())
        if secret and verify_totp(secret, cleaned, period=self.code_expiry_seconds):
            return True
        recovery = [str(c) for c in (getattr(user, "mfa_recovery_codes", None) or [])]
        if cleaned.lower() in {c.lower() for c in recovery}:
            remaining = [c for c in recovery if c.lower() != cleaned.lower()]
            try:
                user.mfa_recovery_codes = remaining
            except Exception:
                pass
            return True
        return False

    def send_code(self, user: Any) -> None:
        return None


class EmailAuthentication:
    """Email one-time codes via a pluggable ``Mailer`` (memory default, SMTP for production)."""

    def __init__(
        self,
        *,
        mailer: Any | None = None,
        store: MemoryEmailCodeStore | None = None,
        from_address: str = "orbit@localhost",
        ttl_seconds: int = 600,
    ) -> None:
        self.mailer = mailer or MemoryMailer()
        self.store = store or MemoryEmailCodeStore(ttl_seconds=ttl_seconds)
        self.from_address = from_address

    def get_id(self) -> str:
        return "email"

    def is_enabled(self, user: Any) -> bool:
        return bool(getattr(user, "mfa_email_enabled", False))

    def get_management_schema(self) -> Form:
        return Form.make("mfa_email").schema(
            [TextInput.make("email").label("Email").email().disabled()]
        )

    def get_challenge_form(self) -> Form:
        return Form.make("mfa_email_challenge").schema(
            [
                OneTimeCodeInput.make("code")
                .label("Email code")
                .max_length(6)
                .required()
            ]
        )

    def provision(self, user: Any) -> dict[str, Any]:
        return {"email": _user_email(user)}

    def send_code(self, user: Any) -> None:
        code = f"{secrets.randbelow(1_000_000):06d}"
        self.store.put(_user_key(user), code)
        to = _user_email(user)
        if not to:
            return
        self.mailer.send(
            to,
            "Your Orbit sign-in code",
            f"Your one-time code is {code}. It expires in {self.store.ttl_seconds // 60} minutes.",
        )

    def verify(self, user: Any, code: str) -> bool:
        cleaned = "".join(ch for ch in str(code) if ch.isdigit())
        return self.store.consume(_user_key(user), cleaned)


def enabled_providers(providers: list[Any], user: Any) -> list[Any]:
    return [p for p in providers if hasattr(p, "is_enabled") and p.is_enabled(user)]


def render_app_setup(provision: dict[str, Any]) -> str:
    from almasix.orbit.support.html import e

    secret = e(str(provision.get("secret") or ""))
    uri = e(str(provision.get("otpauth_uri") or ""))
    codes = "".join(f"<li><code>{e(c)}</code></li>" for c in provision.get("recovery_codes") or [])
    return (
        f'<div class="or-mfa-setup">'
        f'<p class="or-mfa-setup-lead">Scan this otpauth URI in your authenticator, or type the secret.</p>'
        f'<p class="or-mfa-secret"><code>{secret}</code></p>'
        f'<p class="or-mfa-uri"><code>{uri}</code></p>'
        f'<p class="or-muted">Recovery codes</p><ul class="or-mfa-recovery">{codes}</ul>'
        f"</div>"
    )
