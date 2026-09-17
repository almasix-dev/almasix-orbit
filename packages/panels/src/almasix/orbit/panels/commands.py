"""Smith commands for Orbit scaffolding.

Canonical ``make:orbit-*`` names plus ``orbit:*`` aliases share the same handlers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from almasix.console.command import Command


def _studly(name: str) -> str:
    parts = name.replace("-", "_").replace("\\", "/").replace(".", "/").split("/")
    last = parts[-1]
    return "".join(p[:1].upper() + p[1:] for p in last.replace("-", "_").split("_") if p)


def _snake(name: str) -> str:
    studly = _studly(name)
    out: list[str] = []
    for i, c in enumerate(studly):
        if c.isupper() and i:
            out.append("_")
        out.append(c.lower())
    return "".join(out)


def _resolve_name(command: Command, *args: Any, **kwargs: Any) -> str | None:
    raw = kwargs.get("name")
    if raw is None and args:
        raw = args[0]
    if raw is None:
        raw = command.argument("name")
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


class OrbitInstallCommand(Command):
    signature = (
        "orbit:install"
        " {--path=admin : Panel URL path (without leading slash)}"
        " {--panel=admin : Panel id}"
        " {--force : Overwrite existing config / provider stubs}"
    )
    description = "Publish Orbit assets and scaffold config + first panel provider"
    aliases: ClassVar[tuple[str, ...]] = ()
    boots_application: ClassVar[bool] = True

    def handle(self) -> int:
        panel_id = str(self.option("panel") or "admin").strip() or "admin"
        path = str(self.option("path") or "admin").strip().lstrip("/") or "admin"
        force = bool(self.option("force"))

        try:
            self.call(
                "vendor:publish",
                {"--tag": "orbit-assets", **({"--force": True} if force else {})},
            )
        except Exception as exc:  # pragma: no cover
            self.warn(f"Asset publish skipped: {exc}")

        if self.app is None:
            self.error("Application is required for orbit:install")
            return self.FAILURE

        config_path = Path(self.app.path("config", "orbit.py"))
        if config_path.exists() and not force:
            self.info(f"config exists → {config_path}")
        else:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                f'''"""Orbit panel defaults."""

from __future__ import annotations

ORBIT = {{
    "path": "/{path}",
    "font": "Outfit",
    "brand": "Orbit",
    "panel": "{panel_id}",
}}
''',
                encoding="utf-8",
            )
            self.info(f"wrote {config_path}")

        provider_path = Path(self.app.path("app", "providers", "orbit_panel_provider.py"))
        if provider_path.exists() and not force:
            self.info(f"provider exists → {provider_path}")
        else:
            provider_path.parent.mkdir(parents=True, exist_ok=True)
            provider_path.write_text(
                f'''"""Register the default Orbit panel."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.providers import ServiceProvider


class OrbitPanelProvider(ServiceProvider):
    def boot(self) -> None:
        panel = (
            Panel.make("{panel_id}")
            .path("{path}")
            .brand_name("Orbit")
            .navigation_layout("apps")
            .login()
        )
        self.app.make(PanelRegistry).register(panel)
''',
                encoding="utf-8",
            )
            self.info(f"wrote {provider_path}")
            self.warn(
                "Register OrbitPanelProvider in config/app.py providers "
                "(or your app's provider list) if it is not auto-discovered."
            )

        self.success(
            f"Orbit installed. Next: smith orbit:resource Post --panel={panel_id} "
            f"then open /{path}"
        )
        return self.SUCCESS


class MakeOrbitPanelCommand(Command):
    signature = (
        "make:orbit-panel {name : Panel id (e.g. admin)}"
        " {--path= : URL path (defaults to panel id)}"
        " {--force : Overwrite}"
    )
    description = "Create an Orbit panel registration stub"
    aliases: ClassVar[tuple[str, ...]] = ("orbit:panel",)
    boots_application: ClassVar[bool] = True

    def handle(self, *args: Any, **kwargs: Any) -> int:
        name = _resolve_name(self, *args, **kwargs)
        if not name:
            self.error("name is required")
            return self.INVALID
        panel_id = name.replace("/", "_").replace("-", "_").lower()
        path = str(self.option("path") or panel_id).strip().lstrip("/") or panel_id
        force = bool(self.option("force") or kwargs.get("force"))
        if self.app is None:
            self.error("Application is required")
            return self.FAILURE
        out = Path(self.app.path("app", "orbit", f"{panel_id}_panel.py"))
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists() and not force:
            self.error(f"{out} already exists")
            return self.FAILURE
        studly = _studly(panel_id)
        out.write_text(
            f'''"""Orbit panel: {panel_id}."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry


def register_{panel_id}_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("{panel_id}")
        .path("{path}")
        .brand_name("{studly}")
        .navigation_layout("apps")
        .login()
    )
    registry.register(panel)
    return panel
''',
            encoding="utf-8",
        )
        self.info(f"panel → {out}")
        self.success("orbit panel stub created")
        return self.SUCCESS


class MakeOrbitResourceCommand(Command):
    signature = (
        "make:orbit-resource {name : Resource class name (e.g. Post or Blog/Post)}"
        " {--panel=admin : Panel id (documentation only)}"
        " {--force : Overwrite}"
    )
    description = "Create a new Orbit resource class"
    aliases: ClassVar[tuple[str, ...]] = ("orbit:resource",)
    boots_application: ClassVar[bool] = True

    def handle(self, *args: Any, **kwargs: Any) -> int:
        raw = _resolve_name(self, *args, **kwargs)
        if not raw:
            self.error("name is required")
            return self.INVALID
        force = bool(self.option("force") or kwargs.get("force"))
        parts = [p for p in raw.replace("\\", "/").replace(".", "/").split("/") if p]
        class_name = _studly(parts[-1])
        if not class_name.endswith("Resource"):
            class_name = f"{class_name}Resource"
        module_parts = [_snake(p) for p in parts]
        if not module_parts[-1].endswith("_resource"):
            module_parts[-1] = _snake(class_name)
        rel = Path(*module_parts[:-1]) if len(module_parts) > 1 else Path()
        if self.app is None:
            # Unit-test / dry path: validate only.
            return self.SUCCESS
        out = Path(self.app.path("app", "orbit", "resources", *rel.parts, f"{module_parts[-1]}.py"))
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists() and not force:
            self.error(f"{out} already exists")
            return self.FAILURE
        model_hint = class_name.removesuffix("Resource")
        out.write_text(
            f'''"""Orbit resource: {class_name}."""

from __future__ import annotations

from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn


class {class_name}(Resource):
    # model = {model_hint}
    navigation_label = "{model_hint}"
    navigation_group = "Content"
    navigation_icon = "heroicon-o-rectangle-stack"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema(
            [
                TextInput.make("title").required().max_length(200),
            ]
        )

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns(
            [
                TextColumn.make("title").searchable().sortable(),
            ]
        )
''',
            encoding="utf-8",
        )
        self.info(f"resource → {out}")
        self.success("orbit resource created")
        return self.SUCCESS


class MakeOrbitFieldCommand(Command):
    signature = (
        "make:orbit-field {name : Field class name (e.g. MoneyInput)}"
        " {--force : Overwrite}"
    )
    description = "Create a custom Orbit form Field subclass"
    aliases: ClassVar[tuple[str, ...]] = ("orbit:field",)
    boots_application: ClassVar[bool] = True

    def handle(self, *args: Any, **kwargs: Any) -> int:
        raw = _resolve_name(self, *args, **kwargs)
        if not raw:
            self.error("name is required")
            return self.INVALID
        force = bool(self.option("force") or kwargs.get("force"))
        class_name = _studly(raw)
        snake = _snake(class_name)
        if self.app is None:
            return self.SUCCESS
        out = Path(self.app.path("app", "orbit", "fields", f"{snake}.py"))
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists() and not force:
            self.error(f"{out} already exists")
            return self.FAILURE
        out.write_text(
            f'''"""Custom Orbit form field: {class_name}."""

from __future__ import annotations

from typing import Any

from almasix.orbit.forms import Field
from almasix.orbit.support.html import e


class {class_name}(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        name = e(self.get_state_path() or self.get_name() or "")
        value = "" if state is None else e(state)
        binding = self._wire_binding(name)
        control = (
            f'<input class="or-input" id="or-{{name}}" name="{{name}}" '
            f'value="{{value}}"{{binding}} />'
        )
        return self.wrap_field(name, control, **ctx)
''',
            encoding="utf-8",
        )
        self.info(f"field → {out}")
        self.success("orbit field created")
        return self.SUCCESS


class MakeOrbitUserCommand(Command):
    """Create an application user for Orbit panel auth (Filament ``make:filament-user``)."""

    signature = (
        "make:orbit-user"
        " {--name= : Display name}"
        " {--email= : Email address}"
        " {--password= : Password (prompted if omitted)}"
        " {--model= : User model FQCN (defaults to auth.providers.users.model)}"
        " {--scaffold : Create a minimal app.models.user.User if missing}"
    )
    description = "Create the initial Orbit admin / panel user"
    aliases: ClassVar[tuple[str, ...]] = ("orbit:user",)
    boots_application: ClassVar[bool] = True

    def handle(self) -> int:
        name = str(self.option("name") or "").strip() or self.ask("Name", required=True)
        email = str(self.option("email") or "").strip() or self.ask("Email address", required=True)
        password = str(self.option("password") or "")
        if not password:
            password = self.secret("Password", required=True)
            confirm = self.secret("Confirm password", required=True)
            if password != confirm:
                self.error("Passwords do not match")
                return self.FAILURE

        model_path = str(self.option("model") or "").strip() or self._default_user_model()
        if bool(self.option("scaffold")):
            try:
                self._scaffold_user_model(model_path)
            except Exception as exc:
                self.error(f"Could not scaffold user model: {exc}")
                return self.FAILURE

        try:
            user_model = self._load_model(model_path)
        except Exception as exc:
            self.error(f"Could not import user model {model_path!r}: {exc}")
            self.comment(
                "Add an Authenticatable User model (app/models/user.py) and "
                "config/auth.py, then migrate. Or re-run with --scaffold:"
            )
            self.line("  smith orbit:user --scaffold")
            self.line("  smith migrate")
            self.line("  smith orbit:user")
            return self.FAILURE

        try:
            user = self._create_user(user_model, name=name, email=email, password=password)
        except Exception as exc:
            self.error(f"Could not create user: {exc}")
            self.comment("If the users table is missing, run: smith migrate")
            return self.FAILURE

        label = getattr(user, "email", None) or email
        self.success(f"Orbit user created → {label}")
        self.comment(
            "Use panel auth middleware (not only .default_user()) so this account can sign in."
        )
        return self.SUCCESS

    def _default_user_model(self) -> str:
        try:
            from almasix.config import config

            return str(
                config("auth.providers.users.model", "app.models.user.User")
                or "app.models.user.User"
            )
        except Exception:
            return "app.models.user.User"

    def _load_model(self, path: str) -> type[Any]:
        import importlib

        module_name, _, class_name = path.rpartition(".")
        if not module_name or not class_name:
            raise ValueError("model must be a fully-qualified class path")
        module = importlib.import_module(module_name)
        model = getattr(module, class_name, None)
        if model is None:
            raise AttributeError(f"{class_name} not found in {module_name}")
        return model

    def _scaffold_user_model(self, model_path: str) -> None:
        """Write a minimal Authenticatable User when the app has none yet."""
        if self.app is None:
            raise RuntimeError("Application is required to scaffold a user model")
        if model_path != "app.models.user.User":
            raise ValueError("--scaffold only supports app.models.user.User")

        models_init = Path(self.app.path("app", "models", "__init__.py"))
        user_path = Path(self.app.path("app", "models", "user.py"))
        auth_config = Path(self.app.path("config", "auth.py"))
        models_init.parent.mkdir(parents=True, exist_ok=True)

        if not user_path.exists():
            user_path.write_text(
                '''"""User model for Orbit panel auth."""

from __future__ import annotations

from almasix.auth import AuthenticatableMixin
from almasix.orm import Model


class User(AuthenticatableMixin, Model):
    fillable = ("name", "email", "password", "remember_token")
    hidden = ("password", "remember_token")
''',
                encoding="utf-8",
            )
            self.info(f"wrote {user_path}")
        else:
            self.info(f"user model exists → {user_path}")

        if not models_init.exists():
            models_init.write_text(
                '"""Application models."""\n\nfrom app.models.user import User\n\n__all__ = ["User"]\n',
                encoding="utf-8",
            )

        if not auth_config.exists():
            auth_config.parent.mkdir(parents=True, exist_ok=True)
            auth_config.write_text(
                '''"""Authentication defaults — guards, providers, password brokers."""

from almasix.config import env

config = {
    "defaults": {
        "guard": env("AUTH_GUARD", "web"),
        "passwords": env("AUTH_PASSWORD_BROKER", "users"),
    },
    "guards": {
        "web": {
            "driver": "session",
            "provider": "users",
        },
    },
    "providers": {
        "users": {
            "driver": "articulate",
            "model": "app.models.user.User",
        },
    },
    "passwords": {
        "users": {
            "provider": "users",
            "table": "password_reset_tokens",
            "expire": 60,
            "throttle": 60,
        },
    },
    "password_timeout": 10800,
}
''',
                encoding="utf-8",
            )
            self.info(f"wrote {auth_config}")

    def _create_user(self, model: type[Any], *, name: str, email: str, password: str) -> Any:
        import asyncio

        from almasix.hashing import Hash

        attrs = {
            "name": name,
            "email": email,
            "password": Hash.make(password),
        }

        async def _run() -> Any:
            create = getattr(model, "create", None)
            if create is None:
                raise TypeError(f"{model!r} has no create()")
            result = create(attrs)
            if asyncio.iscoroutine(result):
                return await result
            return result

        return asyncio.run(_run())


ORBIT_COMMANDS: list[type[Command]] = [
    OrbitInstallCommand,
    MakeOrbitPanelCommand,
    MakeOrbitResourceCommand,
    MakeOrbitFieldCommand,
    MakeOrbitUserCommand,
]
