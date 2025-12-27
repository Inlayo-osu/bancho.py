#!/usr/bin/env python3.11

from __future__ import annotations

__all__ = ()

import logging
import os

import aiohttp
import orjson
from objects import glob
from quart import Quart
from quart import render_template
from redis import asyncio as aioredis
from utils import AsyncSQLPool
from utils import Version
from utils import log

# Configure logging to avoid duplicate messages
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)

# Disable duplicate hypercorn access logs
logging.getLogger("hypercorn.access").disabled = True
logging.getLogger("hypercorn.error").propagate = False

app = Quart(__name__)
app.logger.setLevel(logging.INFO)

version = Version(1, 3, 0)

# used to secure session data.
# we recommend using a long randomly generated ascii string.
app.secret_key = glob.config.secret_key


@app.before_serving
async def mysql_conn() -> None:
    glob.db = AsyncSQLPool()
    await glob.db.connect(glob.config.mysql)  # type: ignore
    log("Connected to MySQL.")


@app.before_serving
async def redis_conn() -> None:
    glob.redis = aioredis.Redis(
        host=glob.config.redis["host"],
        port=glob.config.redis["port"],
        db=glob.config.redis["db"],
    )
    log("Connected to Redis.")


@app.before_serving
async def http_conn() -> None:
    glob.http = aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode())
    log("HTTP client session initialized.")


@app.before_serving
async def startup_complete() -> None:
    log("guweb startup complete | listening on 0.0.0.0:8000")


@app.after_serving
async def shutdown() -> None:
    log("Shutting down guweb...")
    await glob.db.close()
    await glob.redis.close()
    await glob.http.close()
    log("guweb shutdown complete.")


# globals which can be used in template code
@app.template_global()
def appVersion() -> str:
    return repr(version)


@app.template_global()
def appName() -> str:
    return glob.config.app_name


@app.template_global()
def captchaKey() -> str:
    return glob.config.hCaptcha_sitekey


@app.template_global()
def domain() -> str:
    return glob.config.domain


@app.template_global()
def country_emoji(country_code: str) -> str:
    """Convert ISO 3166-1 alpha-2 country code to emoji unicode codepoints."""
    if not country_code or len(country_code) != 2:
        return "1f3f4"  # black flag as fallback
    
    # Convert each character to regional indicator symbol
    # A-Z (0x41-0x5A) -> 0x1F1E6-0x1F1FF
    codepoints = []
    for char in country_code.upper():
        if 'A' <= char <= 'Z':
            codepoint = ord(char) - ord('A') + 0x1F1E6
            codepoints.append(f"{codepoint:x}")
    
    return "-".join(codepoints) if codepoints else "1f3f4"


from blueprints.frontend import frontend

app.register_blueprint(frontend)

from blueprints.admin import admin

app.register_blueprint(admin, url_prefix="/admin")


@app.errorhandler(404)
async def page_not_found(e):
    # NOTE: we set the 404 status explicitly
    return (await render_template("404.html"), 404)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    app.run(port=8000, debug=glob.config.debug)  # blocking call
