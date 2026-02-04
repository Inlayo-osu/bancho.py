"""bmap: static beatmap info (thumbnails, previews, etc.)"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse

# import app.settings

router = APIRouter(tags=["Beatmaps"])


@router.get("/favicon.ico")
async def get_favicon() -> FileResponse:
    """Serve favicon.ico from assets."""
    favicon_path = (
        Path.cwd() / ".data" / "assets" / "images" / "favicon" / "favicon.ico"
    )
    return FileResponse(favicon_path, media_type="image/x-icon")


# forward any unmatched request to osu!
# eventually if we do bmap submission, we'll need this.
@router.get("/{file_path:path}")
async def everything(request: Request) -> RedirectResponse:
    return RedirectResponse(
        url=f"https://b.ppy.sh{request['path']}",
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
    )
