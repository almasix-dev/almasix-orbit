"""Application configuration."""

from __future__ import annotations

from almasix.config import env

config = {
    "name": env("APP_NAME", "Orbit Demo"),
    "env": env("APP_ENV", "local"),
    "debug": env("APP_DEBUG", True),
    "url": env("APP_URL", "http://127.0.0.1:8000"),
    "base_path": env("APP_BASE_PATH", ""),
    "key": env("APP_KEY", "base64:orbit-demo-local-dev-key-change-me"),
    "locale": env("APP_LOCALE", "en"),
    "fallback_locale": env("APP_FALLBACK_LOCALE", "en"),
    "providers": [
        "app.providers.app_service_provider.AppServiceProvider",
        "app.providers.orbit_panel_provider.OrbitPanelProvider",
    ],
    "skip_provider_discovery": False,
    "dont_discover": [],
}
