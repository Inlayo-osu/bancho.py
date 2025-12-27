"""Helper functions for frontend blueprint."""

from __future__ import annotations

__all__ = (
    "generate_verification_key",
    "send_verification_email",
    "verify_email_code",
    "validate_password",
    "validate_username",
    "validate_email",
    "hash_password",
    "check_password",
    "validate_mode_mods",
)

import hashlib
import random
import string
from typing import Optional

import bcrypt
from cmyui.logging import Ansi
from cmyui.logging import log
from constants import regexes
from objects import glob


def generate_verification_key() -> str:
    """Generate a random verification key."""
    return "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=glob.config.EmailVerifyKeyLength,
        ),
    )


async def send_verification_email(
    redis_key: str,
    username: str,
    email: str,
    subject: str,
    body_prefix: str = "",
) -> str:
    """
    Send verification email and store key in Redis.

    Returns:
        "sent" if successful
        str(ttl) if key already exists and not expired
        "ERROR | {error}" if failed
    """
    from objects.sendEmail import mailSend

    # Check if key already exists
    ttl = await glob.redis.ttl(redis_key)
    if ttl != -2:  # Key exists
        return str(ttl)

    # Generate and store key
    key = generate_verification_key()
    await glob.redis.set(redis_key, key, glob.config.SentEmailTimeout)

    # Prepare email body
    body = f"{body_prefix}\n\n{key}" if body_prefix else key
    
    # Determine email type from redis key
    email_type = ""
    if "ForgotEmailVerify" in redis_key:
        email_type = "Forgot Password"
    elif "RegisterEmailVerify" in redis_key:
        email_type = "Registration"
    elif "Settings/profile" in redis_key:
        email_type = "Profile Update"
    
    # Send email
    result = mailSend(username, email, subject, body, email_type)

    if result == 200:
        return "sent"
    else:
        # Clean up on failure
        await glob.redis.delete(redis_key)
        error_msg = str(result) if isinstance(result, Exception) else result
        return f"ERROR | {error_msg}"


async def verify_email_code(
    redis_key: str,
    provided_code: str,
) -> tuple[bool, str | None]:
    """
    Verify email code from Redis.

    Returns:
        (success: bool, error_message: Optional[str])
    """
    try:
        redis_key_bytes = await glob.redis.get(redis_key)
        if redis_key_bytes is None:
            return False, "Email verification code is Expired."

        stored_code = redis_key_bytes.decode("utf-8")
    except (AttributeError, UnicodeDecodeError) as e:
        log(f"Redis key decode error: {e}", Ansi.LRED)
        return False, "Email verification code is invalid."

    if provided_code == stored_code:
        await glob.redis.delete(redis_key)
        return True, None
    else:
        return False, "Email verification code is Incorrect."


def validate_password(password: str) -> str | None:
    """
    Validate password requirements.

    Returns:
        None if valid, error message if invalid
    """
    if not 8 <= len(password) <= 32:
        return "Password must be 8-32 characters in length."

    if len(set(password)) <= 3:
        return "Password must have more than 3 unique characters."

    if password.lower() in glob.config.disallowed_passwords:
        return "That password was deemed too simple."

    return None


def validate_username(username: str) -> str | None:
    """
    Validate username requirements.

    Returns:
        None if valid, error message if invalid
    """
    if not regexes.username.match(username):
        return "Username syntax is invalid."

    if "_" in username and " " in username:
        return 'Username may contain "_" or " ", but not both.'

    if username in glob.config.disallowed_names:
        return "Username isn't allowed; pick another."

    if username.startswith(" ") or username.endswith(" ") or "  " in username:
        return 'Username may not start or end with " " or have two spaces in a row.'

    return None


def validate_email(email: str) -> str | None:
    """
    Validate email requirements.

    Returns:
        None if valid, error message if invalid
    """
    if not regexes.email.match(email):
        return "Email syntax is invalid."

    return None


def hash_password(password: str) -> tuple[bytes, bytes]:
    """
    Hash password using MD5 and bcrypt.

    Returns:
        (pw_md5, pw_bcrypt)
    """
    pw_md5 = hashlib.md5(password.encode()).hexdigest().encode()
    pw_bcrypt = bcrypt.hashpw(pw_md5, bcrypt.gensalt())
    return pw_md5, pw_bcrypt


async def check_password(
    password: str,
    user_id: int,
    username: str,
) -> tuple[bool, bytes | None]:
    """
    Check password against database.

    Returns:
        (is_valid: bool, pw_bcrypt: Optional[bytes])
    """
    bcrypt_cache = glob.cache["bcrypt"]

    # Get stored password
    pw_bcrypt = (await glob.db.fetch("SELECT pw_bcrypt FROM users WHERE id = %s", [user_id]))["pw_bcrypt"].encode()

    pw_md5 = hashlib.md5(password.encode()).hexdigest().encode()

    # Check credentials (password) against db
    # intentionally slow, will cache to speed up
    if pw_bcrypt in bcrypt_cache:
        if pw_md5 != bcrypt_cache[pw_bcrypt]:  # ~0.1ms
            if glob.config.debug:
                log(f"{username}'s password check failed - pw incorrect.", Ansi.LYELLOW)
            return False, None
    else:  # ~200ms
        if not bcrypt.checkpw(pw_md5, pw_bcrypt):
            if glob.config.debug:
                log(f"{username}'s password check failed - pw incorrect.", Ansi.LYELLOW)
            return False, None

        # Cache password for next check
        bcrypt_cache[pw_bcrypt] = pw_md5

    return True, pw_bcrypt


def validate_mode_mods(mode: str, mods: str) -> bool:
    """
    Validate mode and mods combination.

    Returns:
        True if valid combination
    """
    VALID_MODES = {"std", "taiko", "catch", "mania"}
    VALID_MODS = {"vn", "rx", "ap"}

    if mode not in VALID_MODES or mods not in VALID_MODS:
        return False

    # Enforce combinations: std: vn/rx/ap, taiko: vn/rx, catch: vn/rx, mania: vn only
    if mode == "mania" and mods != "vn":
        return False

    if mods == "ap" and mode != "std":
        return False

    return True
