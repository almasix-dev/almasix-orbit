"""Filesystem disks."""

from almasix.config import env

config = {
    "default": env("FILESYSTEM_DISK", "public"),
    "cloud": "s3",
    "disks": {
        "local": {
            "driver": "local",
            "root": "storage/app",
            "visibility": "private",
        },
        "public": {
            "driver": "local",
            "root": "storage/app/public",
            "url": "/storage",
            "visibility": "public",
        },
    },
    "links": {
        "public/storage": "storage/app/public",
    },
}
