---
title: Overview
description: Login/Register/Profile pages, tenant switcher, and MFA provider protocol.
---

## Auth pages

Built-in `Login` / `Register` pages can be extended and passed to the panel:

```python
from almasix.orbit import Panel, Login, Register, Dashboard

class MyLogin(Login):
    title = "Welcome back"

panel = (
    Panel.make("admin")
    .login(MyLogin)
    .signup()                 # or .signup(MyRegister)
    .dashboard()              # default home; .dashboard(False) to disable
)
```

```python
from almasix.orbit.panels.auth import PasswordReset, Profile

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

![Login (light)](/examples/light/users/login.png)

![Login (dark)](/examples/dark/users/login.png)
