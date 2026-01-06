from __future__ import annotations

import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Optional

import aiomysql
from objects import glob
from objects import utils
from quart import render_template
from quart import session

if TYPE_CHECKING:
    from PIL.Image import Image


# ============================================================================
# Logging utilities
# ============================================================================


class Ansi(str, Enum):
    """ANSI color codes for terminal output"""

    # Text colors
    BLACK = "\x1b[30m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    WHITE = "\x1b[37m"

    # Light colors
    LBLACK = "\x1b[90m"
    LRED = "\x1b[91m"
    LGREEN = "\x1b[92m"
    LYELLOW = "\x1b[93m"
    LBLUE = "\x1b[94m"
    LMAGENTA = "\x1b[95m"
    LCYAN = "\x1b[96m"
    LWHITE = "\x1b[97m"

    # Reset
    RESET = "\x1b[0m"


def log(msg: str, color: Ansi = Ansi.RESET) -> None:
    """Simple logging function with ANSI color support"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{timestamp}] {msg}{Ansi.RESET}", file=sys.stdout, flush=True)


# ============================================================================
# Database utilities
# ============================================================================


class AsyncSQLPool:
    """Async MySQL connection pool wrapper using aiomysql"""

    def __init__(self) -> None:
        self.pool: aiomysql.Pool | None = None

    async def connect(self, config: dict[str, Any]) -> None:
        """Connect to MySQL database"""
        self.pool = await aiomysql.create_pool(
            host=config.get("host", "localhost"),
            port=config.get("port", 3306),
            user=config.get("user", "root"),
            password=config.get("password", ""),
            db=config.get("database", ""),
            autocommit=True,
            maxsize=config.get("pool_size", 10),
        )

    async def close(self) -> None:
        """Close the connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def fetch(
        self,
        query: str,
        params: list | None = None,
    ) -> dict[str, Any] | None:
        """Fetch a single row"""
        if not self.pool:
            raise RuntimeError("Database pool not connected")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params or [])
                return await cursor.fetchone()

    async def fetchall(
        self,
        query: str,
        params: list | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch all rows"""
        if not self.pool:
            raise RuntimeError("Database pool not connected")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params or [])
                return await cursor.fetchall()

    async def execute(self, query: str, params: list | None = None) -> int:
        """Execute a query and return the number of affected rows"""
        if not self.pool:
            raise RuntimeError("Database pool not connected")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params or [])
                return cursor.rowcount


# ============================================================================
# Version utilities
# ============================================================================


class Version:
    """Simple semantic version class"""

    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch

    def __repr__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __str__(self) -> str:
        return self.__repr__()


# ============================================================================
# Template utilities
# ============================================================================


async def flash(status: str, msg: str, template: str) -> str:
    """Flashes a success/error message on a specified template."""
    return await render_template(f"{template}.html", flash=msg, status=status)


async def flash_with_customizations(status: str, msg: str, template: str) -> str:
    """Flashes a success/error message on a specified template. (for customisation settings)"""
    profile_customizations = utils.has_profile_customizations(
        session["user_data"]["id"],
    )
    return await render_template(
        template_name_or_list=f"{template}.html",
        flash=msg,
        status=status,
        customizations=profile_customizations,
    )


def get_safe_name(name: str) -> str:
    """Returns the safe version of a username."""
    # Safe name should meet few criterias.
    # - Whole name should be lower letters.
    # - Space must be replaced with _
    return name.lower().replace(" ", "_")


def convert_mode_int(mode: str) -> int | None:
    """Converts mode (str) to mode (int)."""
    if mode not in _str_mode_dict:
        print("invalid mode passed into utils.convert_mode_int?")
        return
    return _str_mode_dict[mode]


_str_mode_dict = {"std": 0, "taiko": 1, "catch": 2, "mania": 3}


def convert_mode_str(mode: int) -> str | None:
    """Converts mode (int) to mode (str)."""
    if mode not in _mode_str_dict:
        print("invalid mode passed into utils.convert_mode_str?")
        return
    return _mode_str_dict[mode]


_mode_str_dict = {0: "std", 1: "taiko", 2: "catch", 3: "mania"}


async def fetch_geoloc(ip: str) -> str:
    """Fetches the country code corresponding to an IP."""
    url = f"http://ip-api.com/line/{ip}"

    async with glob.http.get(url) as resp:
        if not resp or resp.status != 200:
            if glob.config.debug:
                log("Failed to get geoloc data: request failed.", Ansi.LRED)
            return "xx"
        status, *lines = (await resp.text()).split("\n")
        if status != "success":
            if glob.config.debug:
                log(f"Failed to get geoloc data: {lines[0]}.", Ansi.LRED)
            return "xx"
        return lines[1].lower()


async def validate_captcha(data: str) -> bool:
    """Verify `data` with hcaptcha's API."""
    url = f"https://hcaptcha.com/siteverify"

    request_data = {"secret": glob.config.hCaptcha_secret, "response": data}

    async with glob.http.post(url, data=request_data) as resp:
        if not resp or resp.status != 200:
            if glob.config.debug:
                log("Failed to verify captcha: request failed.", Ansi.LRED)
            return False

        res = await resp.json()

        return res["success"]


def get_required_score_for_level(level: int) -> float:
    if level <= 100:
        if level >= 2:
            return 5000 / 3 * (4 * (level**3) - 3 * (level**2) - level) + 1.25 * (
                1.8 ** (level - 60)
            )
        else:
            return 1.0  # Should be 0, but we get division by 0 below so set to 1
    else:
        return 26931190829 + 1e11 * (level - 100)


def get_level(totalScore: int) -> int:
    level = 1
    while True:
        # Avoid endless loops
        if level > 120:
            return level

        # Calculate required score
        reqScore = get_required_score_for_level(level)

        # Check if this is our level
        if totalScore <= reqScore:
            # Our level, return it and break
            return level - 1
        else:
            # Not our level, calculate score for next level
            level += 1


BANNERS_PATH = Path.cwd() / ".data/banners"
BACKGROUND_PATH = Path.cwd() / ".data/backgrounds"


def has_profile_customizations(user_id: int = 0) -> dict[str, bool]:
    # check for custom banner image file
    for ext in ("jpg", "jpeg", "png", "gif"):
        path = BANNERS_PATH / f"{user_id}.{ext}"
        if has_custom_banner := path.exists():
            break
    else:
        has_custom_banner = False

    # check for custom background image file
    for ext in ("jpg", "jpeg", "png", "gif"):
        path = BACKGROUND_PATH / f"{user_id}.{ext}"
        if has_custom_background := path.exists():
            break
    else:
        has_custom_background = False

    return {"banner": has_custom_banner, "background": has_custom_background}


def crop_image(image: Image) -> Image:
    width, height = image.size
    if width == height:
        return image

    offset = int(abs(height - width) / 2)

    if width > height:
        image = image.crop([offset, 0, width - offset, height])
    else:
        image = image.crop([0, offset, width, height - offset])

    return image
