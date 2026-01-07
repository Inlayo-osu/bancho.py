from __future__ import annotations

__all__ = ("db", "http", "redis", "version", "cache")

from typing import TYPE_CHECKING

import config  # imported for indirect use

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from objects.utils import AsyncSQLPool
    from objects.utils import Version
    from redis.asyncio import Redis

db: AsyncSQLPool
http: ClientSession
redis: Redis
version: Version

cache = {"bcrypt": {}}
