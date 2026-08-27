from __future__ import annotations

from . import BaseModel

# input models


class RegistrationRequest(BaseModel):
    username: str
    email: str
    password: str
    captcha_token: str | None = None


class EmailRequest(BaseModel):
    email: str


class TokenRequest(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    token: str
    password: str


# output models
