"""bancho.py's v2 apis for direct message mail conversations"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from app.api import dependencies as api_dependencies
from app.api.v2.common import actors
from app.api.v2.common import responses
from app.api.v2.common.responses import Failure
from app.api.v2.common.responses import Success
from app.api.v2.models import BaseModel
from app.repositories.mail import MailRepository
from app.repositories.users import User
from app.repositories.users import UsersRepository

router = APIRouter()


class MailMessage(BaseModel):
    id: int
    from_id: int
    to_id: int
    msg: str
    time: int
    read: bool
    from_name: str
    to_name: str


class MailThreadSummary(BaseModel):
    user_id: int
    name: str
    unread_count: int
    last_message: str
    last_message_at: int
    last_message_from_me: bool


class SendMailRequest(BaseModel):
    message: str


@router.get("/mail/conversations")
async def get_mail_conversations(
    *,
    actor: Annotated[
        User | None,
        Depends(actors.get_optional_actor),
    ],
    mail_repository: Annotated[
        MailRepository,
        Depends(api_dependencies.get_mail_repository),
    ],
) -> Success[list[MailThreadSummary]] | Failure:
    if actor is None:
        return responses.failure(
            message="Authentication required.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    rows = await mail_repository.fetch_all_mail_for_user(actor.id)
    threads: dict[int, dict[str, object]] = {}

    for row in rows:
        peer_id = row.from_id if row.from_id != actor.id else row.to_id
        peer_name = row.from_name if row.from_id != actor.id else row.to_name
        thread = threads.setdefault(
            peer_id,
            {
                "user_id": peer_id,
                "name": peer_name,
                "unread_count": 0,
                "last_message": row.msg,
                "last_message_at": row.time,
                "last_message_from_me": row.from_id == actor.id,
            },
        )

        thread["name"] = peer_name
        if row.to_id == actor.id and not row.read:
            thread["unread_count"] = int(thread["unread_count"]) + 1
        if row.time > int(thread["last_message_at"]):
            thread["last_message"] = row.msg
            thread["last_message_at"] = row.time
            thread["last_message_from_me"] = row.from_id == actor.id

    items = [
        MailThreadSummary.model_validate(
            {
                "user_id": int(thread["user_id"]),
                "name": str(thread["name"]),
                "unread_count": int(thread["unread_count"]),
                "last_message": str(thread["last_message"]),
                "last_message_at": int(thread["last_message_at"]),
                "last_message_from_me": bool(thread["last_message_from_me"]),
            },
        )
        for thread in sorted(
            threads.values(),
            key=lambda item: int(item["last_message_at"]),
            reverse=True,
        )
    ]

    return responses.success(items, meta={"total": len(items)})


@router.get("/mail/conversations/{other_user_id}")
async def get_mail_conversation(
    other_user_id: int,
    *,
    actor: Annotated[
        User | None,
        Depends(actors.get_optional_actor),
    ],
    mail_repository: Annotated[
        MailRepository,
        Depends(api_dependencies.get_mail_repository),
    ],
    users_repository: Annotated[
        UsersRepository,
        Depends(api_dependencies.get_users_repository),
    ],
) -> Success[list[MailMessage]] | Failure:
    if actor is None:
        return responses.failure(
            message="Authentication required.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if other_user_id == actor.id:
        return responses.failure(
            message="You cannot open a conversation with yourself.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    target = await users_repository.fetch_one(id=other_user_id)
    if target is None:
        return responses.failure(
            message="User not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    rows = await mail_repository.fetch_conversation(actor.id, other_user_id)
    messages = [
        MailMessage.model_validate(
            {
                "id": row.id,
                "from_id": row.from_id,
                "to_id": row.to_id,
                "msg": row.msg,
                "time": row.time,
                "read": row.read,
                "from_name": row.from_name,
                "to_name": row.to_name,
            },
        )
        for row in rows
    ]
    return responses.success(
        messages,
        meta={"user_id": other_user_id, "name": target.name},
    )


@router.patch("/mail/conversations/{other_user_id}/read")
async def mark_mail_conversation_as_read(
    other_user_id: int,
    *,
    actor: Annotated[
        User | None,
        Depends(actors.get_optional_actor),
    ],
    mail_repository: Annotated[
        MailRepository,
        Depends(api_dependencies.get_mail_repository),
    ],
) -> Success[list[MailMessage]] | Failure:
    if actor is None:
        return responses.failure(
            message="Authentication required.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    rows = await mail_repository.mark_conversation_as_read(
        to_id=actor.id,
        from_id=other_user_id,
    )
    messages = [
        MailMessage.model_validate(
            {
                "id": row.id,
                "from_id": row.from_id,
                "to_id": row.to_id,
                "msg": row.msg,
                "time": row.time,
                "read": row.read,
                "from_name": "",
                "to_name": "",
            },
        )
        for row in rows
    ]
    return responses.success(messages, meta={"marked_read": len(messages)})


@router.post("/mail/conversations/{other_user_id}/messages")
async def create_mail_message(
    other_user_id: int,
    payload: SendMailRequest,
    *,
    actor: Annotated[
        User | None,
        Depends(actors.get_optional_actor),
    ],
    mail_repository: Annotated[
        MailRepository,
        Depends(api_dependencies.get_mail_repository),
    ],
    users_repository: Annotated[
        UsersRepository,
        Depends(api_dependencies.get_users_repository),
    ],
) -> Success[MailMessage] | Failure:
    if actor is None:
        return responses.failure(
            message="Authentication required.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if other_user_id == actor.id:
        return responses.failure(
            message="You cannot send mail to yourself.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    message = payload.message.strip()
    if not message:
        return responses.failure(
            message="Message cannot be empty.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    target = await users_repository.fetch_one(id=other_user_id)
    if target is None:
        return responses.failure(
            message="User not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    created = await mail_repository.create(
        from_id=actor.id,
        to_id=other_user_id,
        msg=message,
    )

    return responses.success(
        MailMessage.model_validate(
            {
                "id": created.id,
                "from_id": created.from_id,
                "to_id": created.to_id,
                "msg": created.msg,
                "time": created.time,
                "read": created.read,
                "from_name": actor.name,
                "to_name": target.name,
            },
        ),
    )
