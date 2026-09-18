"""Password hashing configuration."""

from almasix.config import env

config = {
    "driver": env("HASH_DRIVER", "bcrypt"),
    "bcrypt": {
        "rounds": int(env("BCRYPT_ROUNDS", 12) or 12),
    },
    "rehash_on_login": True,
}
