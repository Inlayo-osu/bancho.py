from __future__ import annotations

__all__ = ("db", "http", "version", "cache")

from typing import TYPE_CHECKING

import config  # imported for indirect use

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from redis import asyncio as aioredis
    from utils import AsyncSQLPool
    from utils import Version

db: AsyncSQLPool
redis: aioredis
http: ClientSession
version: Version

cache = {"bcrypt": {}}
