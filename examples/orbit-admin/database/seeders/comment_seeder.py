"""Seed comments so the Posts relation manager has rows to show."""

from __future__ import annotations

from almasix.orm import Seeder
from app.models.comment import Comment
from app.models.post import Post

_SEED_COMMENTS = [
    {"author": "Ada Lovelace", "body": "Shipping this week?", "status": "visible"},
    {"author": "Grace Hopper", "body": "The tables feel fast now.", "status": "visible"},
    {"author": "Anon", "body": "Spam removed by a moderator.", "status": "hidden"},
]


class CommentSeeder(Seeder):
    async def run(self) -> None:
        if await Comment.count() > 0:
            return
        posts = await Post.all()
        for index, post in enumerate(list(posts)[:3]):
            row = _SEED_COMMENTS[index % len(_SEED_COMMENTS)]
            await Comment.create({**row, "post_id": post.id})
