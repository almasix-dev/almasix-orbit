"""Console schedule for the Orbit Records demo."""

from __future__ import annotations

from almasix.console import schedule

# Soft catalog reset — preserves users / cookie sessions.
# Requires ``smith schedule:work`` (started from the Docker entrypoint).
schedule.command("demo:reset").hourly()
