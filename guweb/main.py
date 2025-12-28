#!/usr/bin/env python3.11

from __future__ import annotations

__all__ = ()

import logging
import os
import sys

import aiohttp
import orjson
from objects import glob
from quart import Quart
from quart import render_template
from redis import asyncio as aioredis
from utils import AsyncSQLPool
from utils import Version
from utils import log

# Configure logging properly
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,  # Force reconfiguration even if already configured
)

# Configure guweb logger
guweb_logger = logging.getLogger("guweb")
guweb_logger.setLevel(logging.INFO)

# Completely disable hypercorn logs to avoid duplicates
logging.getLogger("hypercorn.access").disabled = True
logging.getLogger("hypercorn.error").disabled = True
logging.getLogger("hypercorn").disabled = True

app = Quart(__name__)
app.logger.setLevel(logging.INFO)
app.logger.propagate = False

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
    redis_config = {
        "host": glob.config.redis["host"],
        "port": glob.config.redis["port"],
        "db": glob.config.redis["db"],
    }
    # Add password if configured
    if glob.config.redis.get("password"):
        redis_config["password"] = glob.config.redis["password"]
    
    glob.redis = aioredis.Redis(**redis_config)
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
        if "A" <= char <= "Z":
            codepoint = ord(char) - ord("A") + 0x1F1E6
            codepoints.append(f"{codepoint:x}")

    return "-".join(codepoints) if codepoints else "1f3f4"


from blueprints.frontend import frontend

app.register_blueprint(frontend)
log("Registered frontend blueprint")

from blueprints.admin import admin

app.register_blueprint(admin, url_prefix="/admin")
log("Registered admin blueprint")


@app.errorhandler(404)
async def page_not_found(e):
    # NOTE: we set the 404 status explicitly
    return (await render_template("404.html"), 404)


@app.errorhandler(500)
async def internal_server_error(e):
    """Handle 500 Internal Server Error."""
    guweb_logger.error(f"Internal server error: {e}", exc_info=True)
    return (
        await render_template(
            "error.html",
            error_code=500,
            error_message="Internal Server Error",
            error_details="An unexpected error occurred. Please try again later.",
        ),
        500,
    )


@app.errorhandler(Exception)
async def handle_exception(e):
    """Catch-all exception handler for unhandled exceptions."""
    guweb_logger.error(f"Unhandled exception: {e}", exc_info=True)
    
    # Return 500 error for any unhandled exception
    return (
        await render_template(
            "error.html",
            error_code=500,
            error_message="Internal Server Error",
            error_details="An unexpected error occurred. Please try again later." if not glob.config.debug else str(e),
        ),
        500,
    )


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    app.run(port=8000, debug=glob.config.debug)  # blocking call
