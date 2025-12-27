from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.responses import Response

import app.settings
from app.logging import Ansi
from app.logging import log
from app.logging import magnitude_fmt_time


class OsuSubdomainRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect non-API requests from osu.domain to main domain"""

    # API and game communication paths that should NOT be redirected
    API_PATHS = (
        "/web/",
        "/api/",
        "/ss/",
        "/d/",
        "/p/",
        "/community/",
        "/difficulty-rating",
        "/vote-callback",
    )

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        host = request.headers.get("host", "")
        path = request.url.path

        # Check if request is to osu subdomain
        if host.startswith(f"osu.{app.settings.DOMAIN}") or host.startswith(
            "osu.ppy.sh",
        ):
            # Check if this is an API/game communication path
            is_api_path = any(path.startswith(api_path) for api_path in self.API_PATHS)

            if not is_api_path:
                # Redirect to main domain with same path and query string
                main_domain = app.settings.DOMAIN
                redirect_path = request.url.path
                
                # Convert /users/ to /u/ for shorter URLs
                if redirect_path.startswith("/users/"):
                    redirect_path = redirect_path.replace("/users/", "/u/", 1)
                
                redirect_url = f"https://{main_domain}{redirect_path}"
                if request.url.query:
                    redirect_url += f"?{request.url.query}"

                return RedirectResponse(url=redirect_url, status_code=301)

        return await call_next(request)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        start_time = time.perf_counter_ns()
        response = await call_next(request)
        end_time = time.perf_counter_ns()

        time_elapsed = end_time - start_time

        col = Ansi.LGREEN if response.status_code < 400 else Ansi.LRED

        host = request.headers.get("host", "unknown")
        url = f"{host}{request['path']}"

        log(
            f"[{request.method}] {response.status_code} {url}{Ansi.RESET!r} | {Ansi.LBLUE!r}Request took: {magnitude_fmt_time(time_elapsed)}",
            col,
        )

        response.headers["process-time"] = str(round(time_elapsed) / 1e6)
        return response
