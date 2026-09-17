"""Database connections."""

from almasix.config import env

config = {
    "default": env("DB_CONNECTION", "sqlite"),
    "connections": {
        "sqlite": {
            "driver": "sqlite",
            "database": env("DB_DATABASE", "database/database.sqlite"),
        },
    },
}
