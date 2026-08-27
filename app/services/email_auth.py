from __future__ import annotations

import asyncio
import hashlib
import secrets
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr
from urllib.parse import quote

from redis import asyncio as aioredis

from app import settings
from app.repositories.users import UsersRepository

TOKEN_EXPIRY_SECONDS = 60 * 60


def _token_key(kind: str, token_hash: str) -> str:
    return f"bancho:web_email:{kind}:{token_hash}"


def _pending_key(user_id: int) -> str:
    return f"bancho:web_email:pending:{user_id}"


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@dataclass(frozen=True)
class EmailAuthService:
    users: UsersRepository
    redis: aioredis.Redis
    password_cache: dict[bytes, bytes]

    async def send_verification(self, email: str) -> None:
        user = await self.users.fetch_one(email=email)
        if user is None:
            return
        token = await self._create_token("verify", str(user.id))
        await self.redis.set(_pending_key(user.id), "1", ex=TOKEN_EXPIRY_SECONDS)
        link = f"{settings.WEB_BASE_URL}/verify-email?token={quote(token)}&email={quote(email)}"
        await self._send(
            email,
            "Verify your email address",
            f"Open this link to verify your account:\n\n{link}\n\nThis link expires in one hour.",
        )

    async def verify_email(self, token: str) -> bool:
        user_id = await self._consume_token("verify", token)
        if user_id is None:
            return False
        user = await self.users.fetch_one(id=int(user_id))
        if user is None:
            return False
        await self.redis.delete(_pending_key(user.id))
        return True

    async def is_email_pending(self, user_id: int) -> bool:
        return await self.redis.exists(_pending_key(user_id)) == 1

    async def send_password_reset(self, email: str) -> None:
        user = await self.users.fetch_one(email=email)
        if user is None:
            return
        token = await self._create_token("reset", str(user.id))
        link = f"{settings.WEB_BASE_URL}/forgot-password?token={quote(token)}"
        await self._send(
            email,
            "Reset your password",
            f"Open this link to choose a new password:\n\n{link}\n\nThis link expires in one hour.",
        )

    async def reset_password(self, token: str, password: str) -> bool:
        user_id = await self._consume_token("reset", token)
        if user_id is None:
            return False
        user = await self.users.fetch_one(id=int(user_id))
        if user is None:
            return False

        import bcrypt

        password_md5 = hashlib.md5(password.encode()).hexdigest().encode()
        password_bcrypt = bcrypt.hashpw(password_md5, bcrypt.gensalt())
        self.password_cache[password_bcrypt] = password_md5
        await self.users.partial_update(id=user.id, pw_bcrypt=password_bcrypt)
        return True

    async def _create_token(self, kind: str, value: str) -> str:
        token = secrets.token_urlsafe(32)
        await self.redis.set(
            _token_key(kind, _hash_token(token)),
            value,
            ex=TOKEN_EXPIRY_SECONDS,
        )
        return token

    async def _consume_token(self, kind: str, token: str) -> str | None:
        key = _token_key(kind, token)
        value = await self.redis.getdel(key)
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else str(value)

    async def _send(self, recipient: str, subject: str, body: str) -> None:
        if not settings.SMTP_HOST:
            raise RuntimeError("SMTP is not configured.")

        message = EmailMessage()
        message["From"] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_FROM_EMAIL))
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        def send_sync() -> None:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
                if settings.SMTP_TLS:
                    smtp.starttls()
                if settings.SMTP_USER:
                    smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                smtp.send_message(message)

        try:
            await asyncio.to_thread(send_sync)
        except (OSError, smtplib.SMTPException) as exc:
            raise RuntimeError("Email delivery failed.") from exc
