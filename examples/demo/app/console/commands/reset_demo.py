"""Reset catalog data without touching users or cookie sessions."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine, TypeVar

from almasix.console import Command
from almasix.orm import DB

T = TypeVar("T")


def _run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run a coroutine from sync CLI *or* from inside an HTTP event loop."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda: asyncio.run(coro)).result()


class ResetDemo(Command):
    signature = "demo:reset"
    description = (
        "Truncate artists/albums/tracks and reseed the catalog "
        "(keeps users and cookie sessions)."
    )

    def handle(self) -> int:
        self.info("Resetting Orbit Records catalog…")
        _run_async(self._reset())
        # CatalogSeeder no-ops when artists exist; NotificationSeeder upserts seed ids.
        # db:seed also uses asyncio.run — run it off the HTTP loop when needed.
        _run_async(self._seed())
        self.info("Catalog reset complete (users preserved).")
        return 0

    async def _reset(self) -> None:
        # Child → parent so SQLite FK checks stay happy.
        await DB.table("tracks").truncate()
        await DB.table("albums").truncate()
        await DB.table("artists").truncate()
        # Clear bell rows so seeded + activity notifications feel fresh.
        try:
            await DB.table("notifications").truncate()
        except Exception:
            # Table may not exist until migrate runs on older DBs.
            pass

    async def _seed(self) -> None:
        # Invoke seeding in this thread's event loop (avoids nested asyncio.run).
        from almasix.console.commands.database import SeederOutput
        from almasix.orm.seeder import invoke_seeder

        await invoke_seeder(
            None,
            base_path=self.app.base_path if self.app else None,
            container=self.app.container if self.app else None,
            command=SeederOutput(self.line),
        )
