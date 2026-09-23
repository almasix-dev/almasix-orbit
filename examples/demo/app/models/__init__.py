"""Application models."""

from app.models.album import Album
from app.models.artist import Artist
from app.models.track import Track
from app.models.user import User

__all__ = ["Album", "Artist", "Track", "User"]
