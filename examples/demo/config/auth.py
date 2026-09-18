"""Authentication defaults — guards, providers, password brokers."""

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
