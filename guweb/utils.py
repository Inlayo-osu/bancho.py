"""Utility functions to replace cmyui dependencies"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

import aiomysql


class Ansi(str, Enum):
    """ANSI color codes for terminal output"""

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    GRAY = "\033[90m"
    LRED = "\033[91m"
    LGREEN = "\033[92m"
    LYELLOW = "\033[93m"
    LBLUE = "\033[94m"
    LMAGENTA = "\033[95m"
    LCYAN = "\033[96m"
    LWHITE = "\033[97m"

    RESET = "\033[0m"


def log(msg: str, color: Ansi = Ansi.RESET) -> None:
    """Simple colored logging function"""
    print(f"{color}{msg}{Ansi.RESET}")
    logging.info(msg)


class Version:
    """Simple version class"""

    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch

    def __repr__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __str__(self) -> str:
        return self.__repr__()


class AsyncSQLPool:
    """Simple async MySQL connection pool wrapper"""

    def __init__(self) -> None:
        self.pool: aiomysql.Pool | None = None

    async def connect(self, config: dict[str, Any]) -> None:
        """Connect to MySQL database"""
        self.pool = await aiomysql.create_pool(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            db=config["db"],
            autocommit=True,
            maxsize=10,
        )

    async def close(self) -> None:
        """Close the connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def fetch(
        self,
        query: str,
        params: tuple[Any, ...] | None = None,
    ) -> dict[str, Any] | None:
        """Fetch a single row"""
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params or ())
                return await cursor.fetchone()

    async def fetchall(
        self,
        query: str,
        params: tuple[Any, ...] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch all rows"""
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params or ())
                return await cursor.fetchall()

    async def execute(self, query: str, params: tuple[Any, ...] | None = None) -> int:
        """Execute a query and return affected rows"""
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params or ())
                return cursor.rowcount
