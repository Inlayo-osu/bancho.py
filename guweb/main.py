#!/usr/bin/env python3.11

from __future__ import annotations

__all__ = ()

import os

import aiohttp
import orjson
from objects import glob
from quart import Quart
from quart import render_template
from utils import Ansi
from utils import AsyncSQLPool
from utils import Version
from utils import log

app = Quart(__name__)

version = Version(1, 3, 0)

# used to secure session data.
# we recommend using a long randomly generated ascii string.
app.secret_key = glob.config.secret_key


@app.before_serving
async def mysql_conn() -> None:
    glob.db = AsyncSQLPool()
    await glob.db.connect(glob.config.mysql)  # type: ignore
    log("Connected to MySQL!", Ansi.LGREEN)


@app.before_serving
async def http_conn() -> None:
    glob.http = aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode())
    log("Got our Client Session!", Ansi.LGREEN)


@app.after_serving
async def shutdown() -> None:
    await glob.db.close()
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
