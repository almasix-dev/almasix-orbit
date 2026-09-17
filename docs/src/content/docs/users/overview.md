---
title: Overview
description: Login/Register/Profile pages, tenant switcher, and MFA provider protocol.
---

## Auth pages

```python
from almasix.orbit.panels import Login, Register, PasswordReset, Profile

Login.render()
Register.render()
```

## Tenancy

```python
from almasix.orbit.panels import Tenancy, Tenant

tenancy = (
    Tenancy()
    .tenants([Tenant(1, "Acme"), Tenant(2, "Beta")])
    .current(Tenant(1, "Acme"))
    .scope_using(lambda q, t: [r for r in q if r["tenant_id"] == t.id])
)
tenancy.render_switcher()
```

## MFA

Implement `MfaProvider` or use `AppAuthentication` for TOTP-shaped challenge/management forms. Host verifies codes.

## Preview

![Login (light)](/examples/light/login.png)

![Login (dark)](/examples/dark/login.png)
