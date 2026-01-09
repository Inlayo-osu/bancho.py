#!/usr/bin/env python3.9

from __future__ import annotations

__all__ = ()

import asyncio
import os

import aiohttp
import orjson
import redis.asyncio as redis
from objects import glob
from objects.utils import Ansi
from objects.utils import AsyncSQLPool
from objects.utils import Version
from objects.utils import log
from quart import Quart
from quart import render_template

app = Quart(__name__)

version = Version(1, 3, 0)

# used to secure session data.
# we recommend using a long randomly generated ascii string.
app.secret_key = glob.config.secret_key


@app.before_serving
async def mysql_conn() -> None:
    glob.db = AsyncSQLPool()
    
    # Retry connection with exponential backoff
    max_retries = 5
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            await glob.db.connect(glob.config.mysql)  # type: ignore
            log("Connected to MySQL!", Ansi.GREEN)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                log(f"MySQL connection attempt {attempt + 1}/{max_retries} failed: {e}", Ansi.YELLOW)
                log(f"Retrying in {retry_delay} seconds...", Ansi.YELLOW)
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                log(f"Failed to connect to MySQL after {max_retries} attempts", Ansi.RED)
                raise


@app.before_serving
async def redis_conn() -> None:
    redis_config = glob.config.redis
    
    # Retry connection with exponential backoff
    max_retries = 5
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            glob.redis = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                password=redis_config["password"] if redis_config["password"] else None,
                decode_responses=True,
            )
            # Test connection
            await glob.redis.ping()
            log("Connected to Redis!", Ansi.GREEN)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                log(f"Redis connection attempt {attempt + 1}/{max_retries} failed: {e}", Ansi.YELLOW)
                log(f"Retrying in {retry_delay} seconds...", Ansi.YELLOW)
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                log(f"Failed to connect to Redis after {max_retries} attempts", Ansi.RED)
                raise


@app.before_serving
async def http_conn() -> None:
    glob.http = aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode())
    log("Got our Client Session!", Ansi.GREEN)


@app.after_serving
async def shutdown() -> None:
    await glob.db.close()
    await glob.redis.aclose()
    await glob.http.close()


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
