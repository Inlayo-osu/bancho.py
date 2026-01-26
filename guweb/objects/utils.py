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


def log(msg: str, color: Ansi | None = None) -> None:
    """Simple logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", file=sys.stdout, flush=True)


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
            db=config.get("db", ""),
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
    # Use fields parameter to ensure consistent response format
    # Response format: status\ncountryCode\n
    url = f"http://ip-api.com/line/{ip}?fields=status,countryCode"

    async with glob.http.get(url) as resp:
        if not resp or resp.status != 200:
            if glob.config.debug:
                log("Failed to get geoloc data: request failed.")
            return "xx"

        lines = (await resp.text()).strip().split("\n")

        if len(lines) < 2:
            if glob.config.debug:
                log("Failed to get geoloc data: invalid response format.")
            return "xx"

        status = lines[0]
        if status != "success":
            if glob.config.debug:
                log(
                    f"Failed to get geoloc data: {lines[1] if len(lines) > 1 else 'unknown error'}.",
                )
            return "xx"

        country_code = lines[1].lower()

        if glob.config.debug:
            log(f"Fetched geoloc for IP {ip}: {country_code}")

        return country_code


async def validate_captcha(data: str) -> bool:
    """Verify `data` with hcaptcha's API."""
    url = f"https://hcaptcha.com/siteverify"

    request_data = {"secret": glob.config.hCaptcha_secret, "response": data}

    async with glob.http.post(url, data=request_data) as resp:
        if not resp or resp.status != 200:
            if glob.config.debug:
                log("Failed to verify captcha: request failed.")
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


def get_difficulty_colour_spectrum(diff_value):
    """Get color for difficulty rating based on spectrum"""
    domain = [0.1, 1.25, 2, 2.5, 3.3, 4.2, 4.9, 5.8, 6.7, 7.7, 9]
    range_ = [
        "#4290FB",
        "#4FC0FF",
        "#4FFFD5",
        "#7CFF4F",
        "#F6F05C",
        "#FF8068",
        "#FF4E6F",
        "#C645B8",
        "#6563DE",
        "#18158E",
        "#000000",
    ]

    if diff_value > 9:
        return "#000000"

    # Find the index where diff_value fits in the domain
    index = 0
    while index < len(domain) - 1 and diff_value >= domain[index]:
        index += 1

    # Interpolate the color value based on the index
    if index == 0:
        return range_[0]
    elif index == len(domain):
        return range_[-1]
    else:
        prev_value = domain[index - 1]
        next_value = domain[index]
        prev_color = range_[index - 1]
        next_color = range_[index]
        proportion = (diff_value - prev_value) / (next_value - prev_value)

        red = int(prev_color[1:3], 16) + int(
            (int(next_color[1:3], 16) - int(prev_color[1:3], 16)) * proportion,
        )
        green = int(prev_color[3:5], 16) + int(
            (int(next_color[3:5], 16) - int(prev_color[3:5], 16)) * proportion,
        )
        blue = int(prev_color[5:7], 16) + int(
            (int(next_color[5:7], 16) - int(prev_color[5:7], 16)) * proportion,
        )

        return f"#{red:02X}{green:02X}{blue:02X}"


def get_mode_icon(id: int):
    """Get mode icon class based on mode ID"""
    if id in [0, 4, 8]:
        mode = "mode-icon mode-osu"
    elif id in [1, 5]:
        mode = "mode-icon mode-taiko"
    elif id in [2, 6]:
        mode = "mode-icon mode-catch"
    elif id in [3]:
        mode = "mode-icon mode-mania"
    else:
        mode = "mode-icon mode-osu"

    return mode


def get_color_formatted_grade(a):
    """Get color and formatted letter for grade"""
    color = "#fff"
    if a in ["A"]:
        color = "#28a745"
    elif a in ["B"]:
        color = "#3d97ff"
    elif a in ["C"]:
        color = "#ff56da"
    elif a in ["SH"]:
        a = "S"
        color = "#cde7e7"
    elif a in ["XH"]:
        a = "SS"
        color = "#cde7e7"
    elif a in ["D", "F"]:
        color = "#ff6262"
    elif a in ["S"]:
        color = "#fc2"
    elif a in ["X"]:
        a = "SS"
        color = "#fc2"

    return {"letter": a, "color": color}


mod_dict = {
    1: "NF",
    2: "EZ",
    4: "TD",
    8: "HD",
    16: "HR",
    32: "SD",
    64: "DT",
    128: "RX",
    256: "HT",
    512: "NC",
    1024: "FL",
    2048: "AP",
    4096: "SO",
    8192: "AP",
    16384: "PF",
    32768: "4K",
    65536: "5K",
    131072: "6K",
    262144: "7K",
    524288: "8K",
    1015808: "",
    1048576: "FD",
    2097152: "RD",
    4194304: "CN",
    16777216: "9K",
    33554432: "10K",
    67108864: "1K",
    134217728: "3K",
    268435456: "2K",
    536870912: "V2",
}


def get_mods(mods_int):
    """Convert mod integer to readable string"""
    mods = []

    for mod_value, mod_str in mod_dict.items():
        if mods_int & mod_value:
            mods.append(mod_str)

    mods_str = (
        "".join(mods)
        .replace("RXNC", "NCRX")
        .replace("APNC", "NCAP")
        .replace("HDHRNC", "HDNCHR")
        .replace("NFNC", "NCNF")
        .replace("DTNC", "NC")
    )
    return f"+{mods_str}" if mods else ""
