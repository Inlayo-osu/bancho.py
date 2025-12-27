from __future__ import annotations

__all__ = ("db", "http", "version", "cache")

from typing import TYPE_CHECKING

import config  # imported for indirect use

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from utils import AsyncSQLPool
    from utils import Version

db: AsyncSQLPool
http: ClientSession
version: Version

cache = {"bcrypt": {}}
