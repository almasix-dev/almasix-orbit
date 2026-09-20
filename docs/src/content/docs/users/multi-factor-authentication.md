---
title: Multi-factor authentication
description: Require an authenticator TOTP or emailed one-time code after password login.
---

## Introduction

**Multi-factor authentication** (MFA) is the second step after a correct email and password. Orbit parks the session as *pending*, sends the operator to `/mfa-challenge`, and only then lets them into the panel.

Two built-in providers cover the usual cases:

- `AppAuthentication` — six-digit codes from an authenticator app (RFC 6238 TOTP), plus one-time recovery codes
- `EmailAuthentication` — a code delivered through a `Mailer` (`MemoryMailer` for demos, `SmtpMailer` for production)

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit.panels.mfa import AppAuthentication, EmailAuthentication, SmtpMailer

Panel.make("admin")
    .login()
    .multi_factor_authentication(
        AppAuthentication(brand_name="Orbit"),
        EmailAuthentication(
            mailer=SmtpMailer(
                "smtp.example.com",
                587,
                username="orbit",
                password="secret",
                from_address="noreply@example.com",
            )
        ),
    )
```

Flags on the user object decide which methods are live: `mfa_app_enabled` / `mfa_app_secret` / `mfa_recovery_codes` for the app, `mfa_email_enabled` plus `email` for the mailbox. Persist those columns on your account model.

![Orbit MFA challenge (light)](/examples/light/users/mfa/challenge.png)

![Orbit MFA challenge (dark)](/examples/dark/users/mfa/challenge.png)

## Authenticator app

`AppAuthentication.provision(user)` creates a base32 secret and an `otpauth://` URI the operator pastes into their app. `verify(user, code)` accepts the current TOTP (one period of clock skew) or a recovery code, which is then consumed.

```python title="app/orbit/auth/mfa.py"
from almasix.orbit.panels.mfa import AppAuthentication

app = AppAuthentication(brand_name="Orbit")
details = app.provision(user)
# details["secret"], details["otpauth_uri"], details["recovery_codes"]
```

![Orbit authenticator setup (light)](/examples/light/users/mfa/app-setup.png)

![Orbit authenticator setup (dark)](/examples/dark/users/mfa/app-setup.png)

## Email codes

`EmailAuthentication.send_code(user)` stores a six-digit code (default ten minutes) and hands it to the mailer. The default `MemoryMailer` appends to `.outbox` — swap in `SmtpMailer` when you have an SMTP host. `verify` consumes the code once.

```python title="app/orbit/auth/mfa.py"
from almasix.orbit.panels.mfa import EmailAuthentication, MemoryMailer

mailer = MemoryMailer()
EmailAuthentication(mailer=mailer).send_code(user)
assert mailer.outbox[-1]["to"] == user.email
```

![Orbit email MFA (light)](/examples/light/users/mfa/email.png)

![Orbit email MFA (dark)](/examples/dark/users/mfa/email.png)

## Sign-in flow

1. `LoginHost.authenticate` checks email and password.
2. If any registered provider `is_enabled(user)`, Orbit sets `orbit_mfa_pending` and redirects to `{panel}/mfa-challenge`.
3. `MfaChallengeHost.verifyMfa` checks the code, clears the pending flag, and sends the operator home.
4. While pending, other panel routes redirect back to the challenge. Logout clears the flag.

Implement `MfaProvider` (`get_id`, `is_enabled`, `get_challenge_form`, `get_management_schema`, `verify`, optional `send_code` / `provision`) for a custom method.

See also [Users overview](/users/overview/).
