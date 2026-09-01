"""bancho.py's v2 apis for public chat channels."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from app.api import dependencies as api_dependencies
from app.api.v2.common import responses
from app.api.v2.common.responses import Failure
from app.api.v2.common.responses import Success
from app.api.v2.models import BaseModel
from app.repositories.channels import ChannelsRepository

router = APIRouter()

CHANNEL_LOG_RE = re.compile(
    r"^\[(?P<time>[^\]]+)\]\s+(?P<author>.+?)\s+@\s+(?P<channel>#[^:]+):\s*(?P<message>.*)$",
)


class ChatChannel(BaseModel):
    id: int
    name: str
    topic: str
    read_priv: int
    write_priv: int
    auto_join: bool


class ChatMessage(BaseModel):
    id: int
    channel: str
    author: str
    text: str
    time: str


def _read_channel_log_messages(channel_name: str, limit: int = 100) -> list[ChatMessage]:
    log_path = Path.cwd() / ".data" / "logs" / "chat.log"
    if not log_path.exists():
        return []

    items: list[ChatMessage] = []
    with log_path.open("r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    for idx, line in enumerate(reversed(lines), start=1):
        match = CHANNEL_LOG_RE.match(line.strip())
        if match is None:
            continue
        if match.group("channel") != channel_name:
            continue

        items.append(
            ChatMessage(
                id=idx,
                channel=match.group("channel"),
                author=match.group("author"),
                text=match.group("message"),
                time=match.group("time"),
            ),
        )
        if len(items) >= limit:
            break

    return list(reversed(items))


@router.get("/chat/channels")
async def get_chat_channels(
    *,
    channels_repository: Annotated[
        ChannelsRepository,
        Depends(api_dependencies.get_channels_repository),
    ],
) -> Success[list[ChatChannel]] | Failure:
    rows = sorted(
        await channels_repository.fetch_many(),
        key=lambda channel: channel.id,
    )
    return responses.success(
        [
            ChatChannel.model_validate(
                {
                    "id": row.id,
                    "name": row.name,
                    "topic": row.topic,
                    "read_priv": row.read_priv,
                    "write_priv": row.write_priv,
                    "auto_join": row.auto_join,
                },
            )
            for row in rows
        ],
        meta={"total": len(rows)},
    )


@router.get("/chat/channels/{channel_name}/messages")
async def get_chat_channel_messages(
    channel_name: str,
    *,
    limit: int = Query(100, ge=1, le=200),
) -> Success[list[ChatMessage]] | Failure:
    if not channel_name.startswith("#"):
        return responses.failure(
            message="Invalid channel name.",
            status_code=400,
        )

    messages = _read_channel_log_messages(channel_name, limit=limit)
    return responses.success(messages, meta={"channel": channel_name, "limit": limit})
