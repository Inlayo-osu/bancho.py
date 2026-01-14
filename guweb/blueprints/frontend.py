from __future__ import annotations

__all__ = ()

import hashlib
import os
import random
import string
import time
from datetime import datetime
from datetime import timedelta
from functools import wraps
from pathlib import Path

import bcrypt
from constants import regexes
from objects import glob
from objects import utils
from objects.email_utils import send_password_reset_email
from objects.email_utils import send_verification_email
from objects.privileges import Privileges
from objects.utils import Ansi
from objects.utils import flash
from objects.utils import flash_with_customizations
from objects.utils import log
from PIL import Image
from quart import Blueprint
from quart import redirect
from quart import render_template
from quart import request
from quart import send_file
from quart import session

VALID_MODES = frozenset({"std", "taiko", "catch", "mania"})
VALID_MODS = frozenset({"vn", "rx", "ap"})

frontend = Blueprint("frontend", __name__)


def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not session:
            return await flash(
                "error",
                "You must be logged in to access that page.",
                "login",
            )
        return await func(*args, **kwargs)

    return wrapper


@frontend.route("/home")
@frontend.route("/")
async def home():
    return await render_template("home.html")


@frontend.route("/home/account/edit")
async def home_account_edit():
    return redirect("/settings/profile")


@frontend.route("/settings")
@frontend.route("/settings/profile")
@login_required
async def settings_profile():
    return await render_template("settings/profile.html")


@frontend.route("/settings/profile", methods=["POST"])
@login_required
async def settings_profile_post():
    form = await request.form

    new_name = form.get("username", type=str)
    new_email = form.get("email", type=str)

    if new_name is None or new_email is None:
        return await flash("error", "Invalid parameters.", "home")

    old_name = session["user_data"]["name"]
    old_email = session["user_data"]["email"]

    # no data has changed; deny post
    if new_name == old_name and new_email == old_email:
        return await flash("error", "No changes have been made.", "settings/profile")

    if new_name != old_name:
        # Usernames must:
        # - be within 2-15 characters in length
        # - not contain both ' ' and '_', one is fine
        # - not be in the config's `disallowed_names` list
        # - not already be taken by another player
        if not regexes.username.match(new_name):
            return await flash(
                "error",
                "Your new username syntax is invalid.",
                "settings/profile",
            )

        if "_" in new_name and " " in new_name:
            return await flash(
                "error",
                'Your new username may contain "_" or " ", but not both.',
                "settings/profile",
            )

        if new_name in glob.config.disallowed_names:
            return await flash(
                "error",
                "Your new username isn't allowed; pick another.",
                "settings/profile",
            )

        if await glob.db.fetch("SELECT 1 FROM users WHERE name = %s", [new_name]):
            return await flash(
                "error",
                "Your new username already taken by another user.",
                "settings/profile",
            )

        safe_name = utils.get_safe_name(new_name)

        # username change successful
        await glob.db.execute(
            "UPDATE users " "SET name = %s, safe_name = %s " "WHERE id = %s",
            [new_name, safe_name, session["user_data"]["id"]],
        )

    if new_email != old_email:
        # Emails must:
        # - match the regex `^[^@\s]{1,200}@[^@\s\.]{1,30}\.[^@\.\s]{1,24}$`
        # - not already be taken by another player
        if not regexes.email.match(new_email):
            return await flash(
                "error",
                "Your new email syntax is invalid.",
                "settings/profile",
            )

        if await glob.db.fetch("SELECT 1 FROM users WHERE email = %s", [new_email]):
            return await flash(
                "error",
                "Your new email already taken by another user.",
                "settings/profile",
            )

        # email change successful
        await glob.db.execute(
            "UPDATE users " "SET email = %s " "WHERE id = %s",
            [new_email, session["user_data"]["id"]],
        )

    # logout
    session.pop("authenticated", None)
    session.pop("user_data", None)
    return await flash(
        "success",
        "Your username/email have been changed! Please login again.",
        "login",
    )


@frontend.route("/settings/avatar")
@login_required
async def settings_avatar():
    return await render_template("settings/avatar.html")


@frontend.route("/settings/avatar", methods=["POST"])
@login_required
async def settings_avatar_post():
    # constants
    MAX_IMAGE_SIZE = glob.config.max_image_size * 1024 * 1024
    AVATARS_PATH = f"{glob.config.path_to_gulag}.data/avatars"
    ALLOWED_EXTENSIONS = [".jpeg", ".jpg", ".png"]

    avatar = (await request.files).get("avatar")

    # no file uploaded; deny post
    if avatar is None or not avatar.filename:
        return await flash("error", "No image was selected!", "settings/avatar")

    filename, file_extension = os.path.splitext(avatar.filename.lower())

    # bad file extension; deny post
    if not file_extension in ALLOWED_EXTENSIONS:
        return await flash(
            "error",
            "The image you select must be either a .JPG, .JPEG, or .PNG file!",
            "settings/avatar",
        )

    # check file size of avatar
    if avatar.content_length > MAX_IMAGE_SIZE:
        return await flash(
            "error",
            "The image you selected is too large!",
            "settings/avatar",
        )

    # remove old avatars
    for fx in ALLOWED_EXTENSIONS:
        if os.path.isfile(
            f'{AVATARS_PATH}/{session["user_data"]["id"]}{fx}',
        ):  # Checking file e
            os.remove(f'{AVATARS_PATH}/{session["user_data"]["id"]}{fx}')

    # avatar cropping to 1:1
    pilavatar = Image.open(avatar.stream)

    # avatar change success
    pilavatar = utils.crop_image(pilavatar)
    pilavatar.save(
        os.path.join(
            AVATARS_PATH,
            f'{session["user_data"]["id"]}{file_extension.lower()}',
        ),
    )
    return await flash(
        "success",
        "Your avatar has been successfully changed!",
        "settings/avatar",
    )


@frontend.route("/settings/custom")
@login_required
async def settings_custom():
    profile_customizations = utils.has_profile_customizations(
        session["user_data"]["id"],
    )
    return await render_template(
        "settings/custom.html",
        customizations=profile_customizations,
    )


@frontend.route("/settings/custom", methods=["POST"])
@login_required
async def settings_custom_post():
    files = await request.files
    banner = files.get("banner")
    background = files.get("background")
    ALLOWED_EXTENSIONS = [".jpeg", ".jpg", ".png", ".gif"]

    # no file uploaded; deny post
    if banner is None and background is None:
        return await flash_with_customizations(
            "error",
            "No image was selected!",
            "settings/custom",
        )

    if banner is not None and banner.filename:
        _, file_extension = os.path.splitext(banner.filename.lower())
        if not file_extension in ALLOWED_EXTENSIONS:
            return await flash_with_customizations(
                "error",
                f"The banner you select must be either a .JPG, .JPEG, .PNG or .GIF file!",
                "settings/custom",
            )

        banner_file_no_ext = os.path.join(
            f".data/banners",
            f'{session["user_data"]["id"]}',
        )

        # remove old picture
        for ext in ALLOWED_EXTENSIONS:
            banner_file_with_ext = f"{banner_file_no_ext}{ext}"
            if os.path.isfile(banner_file_with_ext):
                os.remove(banner_file_with_ext)

        await banner.save(f"{banner_file_no_ext}{file_extension}")

    if background is not None and background.filename:
        _, file_extension = os.path.splitext(background.filename.lower())
        if not file_extension in ALLOWED_EXTENSIONS:
            return await flash_with_customizations(
                "error",
                f"The background you select must be either a .JPG, .JPEG, .PNG or .GIF file!",
                "settings/custom",
            )

        background_file_no_ext = os.path.join(
            f".data/backgrounds",
            f'{session["user_data"]["id"]}',
        )

        # remove old picture
        for ext in ALLOWED_EXTENSIONS:
            background_file_with_ext = f"{background_file_no_ext}{ext}"
            if os.path.isfile(background_file_with_ext):
                os.remove(background_file_with_ext)

        await background.save(f"{background_file_no_ext}{file_extension}")

    return await flash_with_customizations(
        "success",
        "Your customisation has been successfully changed!",
        "settings/custom",
    )


@frontend.route("/settings/password")
@login_required
async def settings_password():
    return await render_template("settings/password.html")


@frontend.route("/settings/password", methods=["POST"])
@login_required
async def settings_password_post():
    form = await request.form
    old_password = form.get("old_password")
    new_password = form.get("new_password")
    repeat_password = form.get("repeat_password")

    # new password and repeat password don't match; deny post
    if new_password != repeat_password:
        return await flash(
            "error",
            "Your new password doesn't match your repeated password!",
            "settings/password",
        )

    # new password and old password match; deny post
    if old_password == new_password:
        return await flash(
            "error",
            "Your new password cannot be the same as your old password!",
            "settings/password",
        )

    # Passwords must:
    # - be within 8-32 characters in length
    # - have more than 3 unique characters
    # - not be in the config's `disallowed_passwords` list
    if not 8 < len(new_password) <= 32:
        return await flash(
            "error",
            "Your new password must be 8-32 characters in length.",
            "settings/password",
        )

    if len(set(new_password)) <= 3:
        return await flash(
            "error",
            "Your new password must have more than 3 unique characters.",
            "settings/password",
        )

    if new_password.lower() in glob.config.disallowed_passwords:
        return await flash(
            "error",
            "Your new password was deemed too simple.",
            "settings/password",
        )

    # cache and other password related information
    bcrypt_cache = glob.cache["bcrypt"]
    pw_bcrypt = (
        await glob.db.fetch(
            "SELECT pw_bcrypt " "FROM users " "WHERE id = %s",
            [session["user_data"]["id"]],
        )
    )["pw_bcrypt"].encode()

    pw_md5 = hashlib.md5(old_password.encode()).hexdigest().encode()

    # check old password against db
    # intentionally slow, will cache to speed up
    if pw_bcrypt in bcrypt_cache:
        if pw_md5 != bcrypt_cache[pw_bcrypt]:  # ~0.1ms
            if glob.config.debug:
                log(
                    f"{session['user_data']['name']}'s change pw failed - pw incorrect.",
                )
            return await flash(
                "error",
                "Your old password is incorrect.",
                "settings/password",
            )
    else:  # ~200ms
        if not bcrypt.checkpw(pw_md5, pw_bcrypt):
            if glob.config.debug:
                log(
                    f"{session['user_data']['name']}'s change pw failed - pw incorrect.",
                )
            return await flash(
                "error",
                "Your old password is incorrect.",
                "settings/password",
            )

    # remove old password from cache
    if pw_bcrypt in bcrypt_cache:
        del bcrypt_cache[pw_bcrypt]

    # calculate new md5 & bcrypt pw
    pw_md5 = hashlib.md5(new_password.encode()).hexdigest().encode()
    pw_bcrypt = bcrypt.hashpw(pw_md5, bcrypt.gensalt())

    # update password in cache and db
    bcrypt_cache[pw_bcrypt] = pw_md5
    await glob.db.execute(
        "UPDATE users " "SET pw_bcrypt = %s " "WHERE safe_name = %s",
        [pw_bcrypt, utils.get_safe_name(session["user_data"]["name"])],
    )

    # logout
    session.pop("authenticated", None)
    session.pop("user_data", None)
    return await flash(
        "success",
        "Your password has been changed! Please log in again.",
        "login",
    )


@frontend.route("/u/<id>")
async def profile_select(id):

    mode = request.args.get("mode", "std", type=str)  # 1. key 2. default value
    mods = request.args.get("mods", "vn", type=str)
    user_data = await glob.db.fetch(
        "SELECT name, safe_name, id, priv, country "
        "FROM users "
        "WHERE safe_name = %s OR id = %s LIMIT 1",
        [utils.get_safe_name(id), id],
    )

    # no user
    if not user_data:
        return (await render_template("404.html"), 404)

    # make sure mode & mods are valid args
    if mode is not None and mode not in VALID_MODES:
        return (await render_template("404.html"), 404)

    if mods is not None and mods not in VALID_MODS:
        return (await render_template("404.html"), 404)

    is_staff = "authenticated" in session and session["user_data"]["is_staff"]
    if not user_data or not (user_data["priv"] & Privileges.Normal or is_staff):
        return (await render_template("404.html"), 404)

    user_data["customisation"] = utils.has_profile_customizations(user_data["id"])
    return await render_template("profile.html", user=user_data, mode=mode, mods=mods)


@frontend.route("/leaderboard")
@frontend.route("/lb")
@frontend.route("/leaderboard/<mode>/<sort>/<mods>")
@frontend.route("/lb/<mode>/<sort>/<mods>")
async def leaderboard(mode="std", sort="pp", mods="vn"):
    return await render_template("leaderboard.html", mode=mode, sort=sort, mods=mods)


@frontend.route("/topplays")
async def topplays():
    mode = request.args.get("mode", "std", type=str)
    mods = request.args.get("mods", "vn", type=str)
    
    # Validate parameters
    if mode not in VALID_MODES or mods not in VALID_MODS:
        return await render_template("404.html"), 404
    
    return await render_template("topplays.html", mode=mode, mods=mods)


@frontend.route("/login")
async def login():
    if "authenticated" in session:
        return await flash("error", "You're already logged in!", "home")

    return await render_template("login.html")


@frontend.route("/login", methods=["POST"])
async def login_post():
    if "authenticated" in session:
        return await flash("error", "You're already logged in!", "home")

    if glob.config.debug:
        login_time = time.time_ns()

    form = await request.form
    username = form.get("username", type=str)
    passwd_txt = form.get("password", type=str)

    if username is None or passwd_txt is None:
        return await flash("error", "Invalid parameters.", "home")

    # check if account exists
    user_info = await glob.db.fetch(
        "SELECT id, name, email, priv, "
        "pw_bcrypt, silence_end "
        "FROM users "
        "WHERE safe_name = %s",
        [utils.get_safe_name(username)],
    )

    # user doesn't exist; deny post
    # NOTE: Bot isn't a user.
    if not user_info or user_info["id"] == 1:
        if glob.config.debug:
            log(f"{username}'s login failed - account doesn't exist.")
        return await flash("error", "Account does not exist.", "login")

    # cache and other related password information
    bcrypt_cache = glob.cache["bcrypt"]
    pw_bcrypt = user_info["pw_bcrypt"].encode()
    pw_md5 = hashlib.md5(passwd_txt.encode()).hexdigest().encode()

    # check credentials (password) against db
    # intentionally slow, will cache to speed up
    if pw_bcrypt in bcrypt_cache:
        if pw_md5 != bcrypt_cache[pw_bcrypt]:  # ~0.1ms
            if glob.config.debug:
                log(f"{username}'s login failed - pw incorrect.")
            return await flash("error", "Password is incorrect.", "login")
    else:  # ~200ms
        if not bcrypt.checkpw(pw_md5, pw_bcrypt):
            if glob.config.debug:
                log(f"{username}'s login failed - pw incorrect.")
            return await flash("error", "Password is incorrect.", "login")

        # login successful; cache password for next login
        bcrypt_cache[pw_bcrypt] = pw_md5

    # user banned; deny post
    if not user_info["priv"] & Privileges.Normal:
        if glob.config.debug:
            log(f"{username}'s login failed - banned.")
        return await flash(
            "error",
            "Your account is restricted. You are not allowed to log in.",
            "login",
        )

    # login successful; store session data
    if glob.config.debug:
        log(f"{username}'s login succeeded.")

    session["authenticated"] = True
    session["user_data"] = {
        "id": user_info["id"],
        "name": user_info["name"],
        "email": user_info["email"],
        "priv": user_info["priv"],
        "silence_end": user_info["silence_end"],
        "is_staff": user_info["priv"] & Privileges.Staff != 0,
        "is_donator": user_info["priv"] & Privileges.Donator != 0,
    }

    if glob.config.debug:
        login_time = (time.time_ns() - login_time) / 1e6
        log(f"Login took {login_time:.2f}ms!")

    return await flash("success", f"Hey, welcome back {username}!", "home")


@frontend.route("/register")
async def register():
    if "authenticated" in session:
        return await flash("error", "You're already logged in.", "home")

    if not glob.config.registration:
        return await flash("error", "Registrations are currently disabled.", "home")

    return await render_template("register.html")


@frontend.route("/register", methods=["POST"])
async def register_post():
    if "authenticated" in session:
        return await flash("error", "You're already logged in.", "home")

    if not glob.config.registration:
        return await flash("error", "Registrations are currently disabled.", "home")

    form = await request.form
    username = form.get("username", type=str)
    email = form.get("email", type=str)
    passwd_txt = form.get("password", type=str)

    if username is None or email is None or passwd_txt is None:
        return await flash("error", "Invalid parameters.", "home")

    if glob.config.hCaptcha_sitekey != "changeme":
        captcha_data = form.get("h-captcha-response", type=str)
        if captcha_data is None or not await utils.validate_captcha(captcha_data):
            return await flash("error", "Captcha failed.", "register")

    # Usernames must:
    # - be within 2-15 characters in length
    # - not contain both ' ' and '_', one is fine
    # - not be in the config's `disallowed_names` list
    # - not already be taken by another player
    # check if username exists
    if not regexes.username.match(username):
        return await flash("error", "Invalid username syntax.", "register")

    if "_" in username and " " in username:
        return await flash(
            "error",
            'Username may contain "_" or " ", but not both.',
            "register",
        )

    if username in glob.config.disallowed_names:
        return await flash("error", "Disallowed username; pick another.", "register")

    if await glob.db.fetch("SELECT 1 FROM users WHERE name = %s", username):
        return await flash(
            "error",
            "Username already taken by another user.",
            "register",
        )

    # Emails must:
    # - match the regex `^[^@\s]{1,200}@[^@\s\.]{1,30}\.[^@\.\s]{1,24}$`
    # - not already be taken by another player
    if not regexes.email.match(email):
        return await flash("error", "Invalid email syntax.", "register")

    if await glob.db.fetch("SELECT 1 FROM users WHERE email = %s", email):
        return await flash("error", "Email already taken by another user.", "register")

    # Passwords must:
    # - be within 8-32 characters in length
    # - have more than 3 unique characters
    # - not be in the config's `disallowed_passwords` list
    if not 8 <= len(passwd_txt) <= 32:
        return await flash(
            "error",
            "Password must be 8-32 characters in length.",
            "register",
        )

    if len(set(passwd_txt)) <= 3:
        return await flash(
            "error",
            "Password must have more than 3 unique characters.",
            "register",
        )

    if passwd_txt.lower() in glob.config.disallowed_passwords:
        return await flash("error", "That password was deemed too simple.", "register")

    # Hash password
    pw_md5 = hashlib.md5(passwd_txt.encode()).hexdigest().encode()
    pw_bcrypt = bcrypt.hashpw(pw_md5, bcrypt.gensalt())

    safe_name = utils.get_safe_name(username)

    # fetch the users' country
    # First try CF-IPCountry (Cloudflare header)
    if request.headers and (country := request.headers.get("CF-IPCountry", type=str)) is not None:
        country = country.lower()
        if glob.config.debug:
            log(f"Country from CF-IPCountry header: {country}")
    elif (
        request.headers
        and (ip := request.headers.get("X-Real-IP", type=str)) is not None
    ):
        country = await utils.fetch_geoloc(ip)
        if glob.config.debug:
            log(f"Country from IP geolocation: {country}")
    else:
        country = "xx"
        if glob.config.debug:
            log("Country set to 'xx' (no header or IP found)")

    # Generate verification code
    verification_code = "".join(random.choices(string.digits, k=6))

    # Store ALL registration data in Redis (expires in 24 hours)
    # User account will be created only AFTER email verification
    redis_key = f"email_verification:registration:{email}"
    await glob.redis.hset(
        redis_key,
        mapping={
            "code": verification_code,
            "username": username,
            "safe_name": safe_name,
            "email": email,
            "pw_bcrypt": pw_bcrypt.decode("utf-8"),
            "pw_md5": pw_md5.decode("utf-8"),
            "country": country,
        },
    )
    await glob.redis.expire(redis_key, 600)  # 10 minutes

    # Send verification email
    email_sent, error_msg = await send_verification_email(email, username, verification_code)

    if not email_sent:
        # Delete registration data from Redis since email failed
        await glob.redis.delete(redis_key)
        
        if glob.config.debug:
            log(f"Failed to send verification email: {error_msg}")
        
        # Show user-friendly error message
        return await flash("error", error_msg or "Failed to send verification email. Please check your email address.", "register")

    if glob.config.debug:
        log(f"{username} registration pending - verification code: {verification_code}")

    # Store pending verification data in session
    session["pending_verification_email"] = email
    session["pending_verification_username"] = username
    return await render_template("verify_email.html")


@frontend.route("/logout")
async def logout():
    if "authenticated" not in session:
        return await flash(
            "error",
            "You can't logout if you aren't logged in!",
            "login",
        )

    if glob.config.debug:
        log(f'{session["user_data"]["name"]} logged out.')

    # clear session data
    session.pop("authenticated", None)
    session.pop("user_data", None)

    return await flash("success", "Successfully logged out!", "login")


@frontend.route("/verify")
async def verify():
    """Show in-game verification instructions page."""
    return await render_template("verify.html")


@frontend.route("/verify-email", methods=["POST"])
async def verify_email():
    """Verify email with code and create user account."""
    try:
        form = await request.form
        code = form.get("code", type=str)

        log(f"[EMAIL VERIFY] Received verification request with code: {code}")

        if not code or len(code) != 6:
            log(f"[EMAIL VERIFY] Invalid code format: {code}")
            return {"status": "error", "message": "Invalid code format"}

        # Get pending verification data from session
        email = session.get("pending_verification_email")
        log(f"[EMAIL VERIFY] Session email: {email}")
        
        if not email:
            log(f"[EMAIL VERIFY] No pending verification in session")
            return {"status": "error", "message": "No pending verification"}

        # Check verification code in Redis
        redis_key = f"email_verification:registration:{email}"
        log(f"[EMAIL VERIFY] Checking Redis key: {redis_key}")
        stored_data = await glob.redis.hgetall(redis_key)
        log(f"[EMAIL VERIFY] Redis data: {stored_data}")

        if not stored_data:
            log(f"[EMAIL VERIFY] No data found in Redis for key: {redis_key}")
            return {"status": "error", "message": "Verification code expired or not found"}

        stored_code = stored_data.get("code")
        log(f"[EMAIL VERIFY] Stored code: {stored_code}, Input code: {code}")
        
        if stored_code != code:
            log(f"[EMAIL VERIFY] Code mismatch")
            return {"status": "error", "message": "Invalid verification code"}

        # Get registration data from Redis
        username = stored_data.get("username")
        safe_name = stored_data.get("safe_name")
        pw_bcrypt = stored_data.get("pw_bcrypt")
        pw_md5 = stored_data.get("pw_md5")
        country = stored_data.get("country")

        log(f"[EMAIL VERIFY] Registration data - username: {username}, email: {email}, country: {country}")

        if not all([username, safe_name, email, pw_bcrypt, pw_md5, country]):
            log(f"[EMAIL VERIFY] Missing registration data: username={username}, safe_name={safe_name}, email={email}, pw_bcrypt={bool(pw_bcrypt)}, pw_md5={bool(pw_md5)}, country={country}")
            return {"status": "error", "message": "Invalid registration data"}

        # Encode hashes back to bytes
        pw_bcrypt_bytes = pw_bcrypt.encode("utf-8")
        pw_md5_bytes = pw_md5.encode("utf-8")
        glob.cache["bcrypt"][pw_bcrypt_bytes] = pw_md5_bytes  # cache pw

        log(f"[EMAIL VERIFY] Creating user account in database...")
        
        # Create user account NOW (after email verification)
        # Set priv to Normal (1) only. Verified (2) will be added on first game login
        async with glob.db.pool.acquire() as conn:
            async with conn.cursor() as db_cursor:
                # add to `users` table with Normal privilege (1)
                # User must log in to game server to get Verified (2) flag
                await db_cursor.execute(
                    "INSERT INTO users "
                    "(name, safe_name, email, pw_bcrypt, country, priv, creation_time, latest_activity) "
                    "VALUES (%s, %s, %s, %s, %s, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP())",
                    [username, safe_name, email, pw_bcrypt_bytes, country],
                )
                user_id = db_cursor.lastrowid
                log(f"[EMAIL VERIFY] User created with ID: {user_id} (priv=1, needs game login to verify)")

                # add to `stats` table
                await db_cursor.executemany(
                    "INSERT INTO stats " "(id, mode) VALUES (%s, %s)",
                    [
                        (user_id, mode)
                        for mode in (
                            0,  # vn!std
                            1,  # vn!taiko
                            2,  # vn!catch
                            3,  # vn!mania
                            4,  # rx!std
                            5,  # rx!taiko
                            6,  # rx!catch
                            8,  # ap!std
                        )
                    ],
                )
                log(f"[EMAIL VERIFY] Stats entries created for user {user_id}")

        # Delete verification code from Redis
        await glob.redis.delete(redis_key)
        log(f"[EMAIL VERIFY] Deleted Redis key: {redis_key}")

        # Clear session
        session.pop("pending_verification_email", None)
        session.pop("pending_verification_username", None)
        log(f"[EMAIL VERIFY] Cleared session data")

        log(f"[EMAIL VERIFY] SUCCESS - Email verified and account created for user ID {user_id}: {username}")

        return {"status": "success", "message": "Email verified successfully"}
    
    except Exception as e:
        log(f"[EMAIL VERIFY] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Server error: {str(e)}"}


@frontend.route("/resend-verification", methods=["POST"])
async def resend_verification():
    """Resend verification code."""
    email = session.get("pending_verification_email")
    username = session.get("pending_verification_username")

    if not email or not username:
        return {"status": "error", "message": "No pending verification"}

    # Check if registration data exists in Redis
    redis_key = f"email_verification:registration:{email}"
    stored_data = await glob.redis.hgetall(redis_key)

    if not stored_data:
        return {"status": "error", "message": "Registration data expired"}

    # Generate new code
    verification_code = "".join(random.choices(string.digits, k=6))

    # Update only the code in Redis (keep other registration data)
    await glob.redis.hset(redis_key, "code", verification_code)
    await glob.redis.expire(redis_key, 600)  # Reset 10 minute expiry

    # Send email
    email_sent, error_msg = await send_verification_email(email, username, verification_code)

    if not email_sent:
        return {"status": "error", "message": error_msg or "Failed to send email"}

    if glob.config.debug:
        log(f"Resent verification code to {email}: {verification_code}")

    return {"status": "success", "message": "Verification code resent"}


@frontend.route("/reset-password")
async def reset_password_page():
    """Render password reset page."""
    code = request.args.get("code", type=str)

    if not code:
        return await flash("error", "Invalid reset link", "login")

    # Verify code exists in Redis
    redis_key = f"email_verification:password_reset:{code}"
    stored_data = await glob.redis.hgetall(redis_key)

    if not stored_data:
        return await flash("error", "Reset code expired or invalid", "login")

    return await render_template("reset_password.html")


@frontend.route("/reset-password", methods=["POST"])
async def reset_password_post():
    """Handle password reset."""
    form = await request.form
    code = form.get("code", type=str)
    new_password = form.get("password", type=str)

    if not code or not new_password:
        return {"status": "error", "message": "Missing parameters"}

    # Validate password
    if not 8 <= len(new_password) <= 32:
        return {"status": "error", "message": "Password must be 8-32 characters"}

    if len(set(new_password)) <= 3:
        return {
            "status": "error",
            "message": "Password must have more than 3 unique characters",
        }

    # Get reset data from Redis
    redis_key = f"email_verification:password_reset:{code}"
    stored_data = await glob.redis.hgetall(redis_key)

    if not stored_data:
        return {"status": "error", "message": "Reset code expired or invalid"}

    user_id = int(stored_data.get("user_id", 0))
    if not user_id:
        return {"status": "error", "message": "Invalid reset data"}

    # Hash new password
    pw_md5 = hashlib.md5(new_password.encode()).hexdigest().encode()
    pw_bcrypt = bcrypt.hashpw(pw_md5, bcrypt.gensalt())

    # Update password
    await glob.db.execute(
        "UPDATE users SET pw_bcrypt = %s WHERE id = %s",
        [pw_bcrypt, user_id],
    )

    # Delete reset code from Redis
    await glob.redis.delete(redis_key)

    if glob.config.debug:
        log(f"Password reset for user ID {user_id}")

    return {"status": "success", "message": "Password reset successfully"}


@frontend.route("/forgot")
async def forgot_redirect():
    """Redirect /forgot to /forgot/username by default."""
    return redirect("/forgot/username")


@frontend.route("/forgot/username")
async def forgot_username():
    """Render forgot username page."""
    if "authenticated" in session:
        return await flash("error", "You're already logged in!", "home")

    return await render_template("forgot_username.html")


@frontend.route("/forgot/username", methods=["POST"])
async def forgot_username_post():
    """Handle forgot username form submission."""
    if "authenticated" in session:
        return await flash("error", "You're already logged in!", "home")

    form = await request.form
    email = form.get("email", type=str)

    if email is None:
        return await flash("error", "Invalid parameters.", "forgot/username")

    # Validate email format
    if not regexes.email.match(email):
        return await flash("error", "Invalid email address.", "forgot/username")

    # Check if email exists in database
    user_info = await glob.db.fetch(
        "SELECT name FROM users WHERE email = %s AND id != 1",
        [email],
    )

    # Always show success message for security (don't reveal if email exists)
    if user_info:
        if glob.config.debug:
            log(f"Username recovery requested for {email}: {user_info['name']}")

        # Send email with username
        from objects.email_utils import send_email

        subject = "Your Inlayo Username"
        body_text = f"""Your Inlayo Username

Your Inlayo username is: {user_info['name']}

You can now log in with this username.

---
Inlayo Team"""

        email_sent, error_msg = await send_email(
            to_email=email,
            subject=subject,
            body_text=body_text,
            email_type="Username Recovery",
            username=user_info["name"],
            extra_info=f"Username: {user_info['name']}",
        )

        if not email_sent:
            if glob.config.debug:
                log(f"Failed to send username recovery email to {email}: {error_msg}")

    return await flash(
        "success",
        "If an account exists with that email, the username has been sent.",
        "login",
    )


@frontend.route("/forgot/password")
async def forgot_password():
    """Render forgot password page."""
    if "authenticated" in session:
        return await flash("error", "You're already logged in!", "home")

    return await render_template("forgot_password.html")


@frontend.route("/forgot/password", methods=["POST"])
async def forgot_password_post():
    """Handle forgot password form submission."""
    if "authenticated" in session:
        return await flash("error", "You're already logged in!", "home")

    form = await request.form
    username_or_email = form.get("username_or_email", type=str)

    if username_or_email is None:
        return await flash("error", "Invalid parameters.", "forgot/password")

    # Check if it's an email and validate format
    if "@" in username_or_email and not regexes.email.match(username_or_email):
        return await flash("error", "Invalid email address.", "forgot/password")

    # Check if username or email exists
    user_info = await glob.db.fetch(
        "SELECT id, name, email FROM users "
        "WHERE (safe_name = %s OR email = %s) AND id != 1",
        [utils.get_safe_name(username_or_email), username_or_email],
    )

    # Always show success message for security (don't reveal if user exists)
    if user_info:
        if glob.config.debug:
            log(
                f"Password reset requested for {user_info['name']} ({user_info['email']})",
            )

        # Generate reset token (6-digit code)
        reset_code = "".join(random.choices(string.digits, k=6))

        # Store reset token in Redis (expires in 1 hour)
        redis_key = f"email_verification:password_reset:{reset_code}"
        await glob.redis.hset(
            redis_key,
            mapping={
                "user_id": str(user_info["id"]),
                "email": user_info["email"],
                "username": user_info["name"],
            },
        )
        await glob.redis.expire(redis_key, 600)  # 10 minutes

        # Create reset link with code
        reset_link = f"https://{glob.config.domain}/reset-password?code={reset_code}"

        # Send password reset email
        email_sent, error_msg = await send_password_reset_email(
            to_email=user_info["email"],
            username=user_info["name"],
            reset_link=reset_link,
        )

        if not email_sent:
            if glob.config.debug:
                log(f"Failed to send password reset email to {user_info['email']}: {error_msg}")

    return await flash(
        "success",
        "If an account exists, a password reset link has been sent to your email.",
        "login",
    )


# social media redirections


@frontend.route("/github")
@frontend.route("/gh")
async def github_redirect():
    return redirect(glob.config.github)


@frontend.route("/discord")
async def discord_redirect():
    return redirect(glob.config.discord_server)


@frontend.route("/fruitbox")
async def fruitbox_redirect():
    return redirect(glob.config.fruitbox)


@frontend.route("/youtube")
@frontend.route("/yt")
async def youtube_redirect():
    return redirect(glob.config.youtube)


@frontend.route("/twitch")
@frontend.route("/tv")
async def twitch_redirect():
    return redirect(glob.config.twitch)


@frontend.route("/twitter")
@frontend.route("/x")
async def twitter_redirect():
    return redirect(glob.config.twitter)


@frontend.route("/instagram")
@frontend.route("/ig")
async def instagram_redirect():
    return redirect(glob.config.instagram)


@frontend.route("/skins")
@frontend.route("/skin")
async def skins_redirect():
    return redirect(glob.config.skins)


# profile customisation
BANNERS_PATH = Path.cwd() / ".data/banners"
BACKGROUND_PATH = Path.cwd() / ".data/backgrounds"


@frontend.route("/banners/<user_id>")
async def get_profile_banner(user_id: int):
    # Check if avatar exists
    for ext in ("jpg", "jpeg", "png", "gif"):
        path = BANNERS_PATH / f"{user_id}.{ext}"
        if path.exists():
            return await send_file(path)

    return b'{"status":404}'


@frontend.route("/backgrounds/<user_id>")
async def get_profile_background(user_id: int):
    # Check if avatar exists
    for ext in ("jpg", "jpeg", "png", "gif"):
        path = BACKGROUND_PATH / f"{user_id}.{ext}"
        if path.exists():
            return await send_file(path)

    return b'{"status":404}'


@frontend.route("/scores/<id>")
async def score_select(id):
    """Score page displaying detailed score information"""
    mods_mode_strs = {
        0: ("Vanilla Standard", "std", "vn"),
        1: ("Vanilla Taiko", "taiko", "vn"),
        2: ("Vanilla CTB", "catch", "vn"),
        3: ("Vanilla Mania", "mania", "vn"),
        4: ("Relax Standard", "std", "rx"),
        5: ("Relax Taiko", "taiko", "rx"),
        6: ("Relax Catch", "catch", "rx"),
        8: ("AutoPilot Standard", "std", "ap"),
    }

    # Get score data from database
    score_data = await glob.db.fetch(
        "SELECT pp, time_elapsed, play_time, score, grade, id, nmiss, n300, n100, n50, acc, userid, mods, max_combo, mode, map_md5 "
        "FROM scores WHERE id = %s",
        [id],
    )
    if not score_data:
        return await flash("error", "Score not found!", "home")

    # Get map data
    map_data = await glob.db.fetch(
        "SELECT id, total_length, set_id, diff, title, creator, version, artist, status, max_combo "
        "FROM maps WHERE md5 = %s",
        [score_data["map_md5"]],
    )
    if not map_data:
        return await flash("error", "Could not find the beatmap.", "home")

    # Get user data
    user_data = await glob.db.fetch(
        "SELECT name, country FROM users WHERE id = %s",
        [score_data["userid"]],
    )
    if not user_data:
        return await flash("error", "Could not find the user.", "home")

    # Score conversions
    score_data["acc"] = round(float(score_data["acc"]), 2)
    score_data["pp"] = round(float(score_data["pp"]), 2)
    score_data["score"] = "{:,}".format(int(score_data["score"]))
    score_data["grade"] = utils.get_color_formatted_grade(score_data["grade"])
    score_data["ptformatted"] = score_data["play_time"].strftime("%d %B %Y %H:%M:%S")
    if score_data["mods"] != 0:
        score_data["mods"] = utils.get_mods(score_data["mods"])
    score_data["mode_icon"] = utils.get_mode_icon(score_data["mode"])
    mods_mode_str, mode, mods = mods_mode_strs.get(
        score_data["mode"],
        ("Vanilla Standard", "std", "vn"),
    )

    # Calculate map progress for failed scores
    if score_data["grade"]["letter"] == "F":
        if map_data["total_length"] != 0:
            score_data["mapprogress"] = f"{(score_data['time_elapsed'] / (map_data['total_length'] * 1000)) * 100:.2f}%"
        else:
            score_data["mapprogress"] = "undefined"

    # Map conversions
    map_data["colordiff"] = utils.get_difficulty_colour_spectrum(map_data["diff"])
    map_data["diff"] = round(map_data["diff"], 2)

    # User customization
    user_data["customization"] = utils.has_profile_customizations(score_data["userid"])

    return await render_template(
        "score.html",
        score=score_data,
        mods_mode_str=mods_mode_str,
        map=map_data,
        mode=mode,
        mods=mods,
        userinfo=user_data,
        pp=int(score_data["pp"] + 0.5),
    )


@frontend.route("/b/<bid>")
@frontend.route("/beatmaps/<bid>")
async def beatmap(bid):
    """Beatmap page displaying beatmap info and leaderboard"""
    mode = request.args.get("mode", "std", type=str)
    mods = request.args.get("mods", "vn", type=str)

    # Validate parameters
    if (
        bid is None
        or not str(bid).lstrip("-").isdigit()
        or mode not in VALID_MODES
        or mods not in VALID_MODS
        or (mode == "mania" and mods == "rx")
        or (mods == "ap" and mode != "std")
    ):
        return await render_template("404.html"), 404

    bid = int(bid)

    # Get beatmap data from DB
    bmap = await glob.db.fetch("SELECT * FROM maps WHERE id = %s", [bid])
    
    # If not in DB, fetch from ppy.sh and save to DB
    if not bmap:
        if glob.config.debug:
            log(f"Beatmap {bid} not in DB, fetching from ppy.sh and saving...")
        
        try:
            # Get all difficulties in the set from ppy.sh API
            if glob.config.osu_api_key:
                metadata_url = "https://old.ppy.sh/api/get_beatmaps"
                metadata_params = {"b": bid, "k": glob.config.osu_api_key}
            else:
                metadata_url = "https://osu.direct/api/get_beatmaps"
                metadata_params = {"b": bid}
            
            async with glob.http.get(metadata_url, params=metadata_params) as resp:
                if resp.status != 200:
                    if glob.config.debug:
                        log(f"Failed to get metadata from ppy.sh: {resp.status}")
                    return await render_template("404.html"), 404
                
                metadata_result = await resp.json()
                if not metadata_result or len(metadata_result) == 0:
                    if glob.config.debug:
                        log(f"No data returned from ppy.sh for beatmap {bid}")
                    return await render_template("404.html"), 404
                
                beatmap_data = metadata_result[0]
                set_id = int(beatmap_data["beatmapset_id"])
                
                if glob.config.debug:
                    log(f"Found beatmap {bid} in set {set_id}, now fetching all difficulties...")
                
                # Fetch ALL difficulties in the set
                if glob.config.osu_api_key:
                    set_metadata_url = "https://old.ppy.sh/api/get_beatmaps"
                    set_metadata_params = {"s": set_id, "k": glob.config.osu_api_key}
                else:
                    set_metadata_url = "https://osu.direct/api/get_beatmaps"
                    set_metadata_params = {"s": set_id}
                
                async with glob.http.get(set_metadata_url, params=set_metadata_params) as set_resp:
                    if set_resp.status == 200:
                        all_diffs_data = await set_resp.json()
                        if all_diffs_data:
                            if glob.config.debug:
                                log(f"Found {len(all_diffs_data)} difficulties in set {set_id}, saving all...")
                            
                            # Save all difficulties to DB
                            for diff_data in all_diffs_data:
                                diff_bid = int(diff_data["beatmap_id"])
                                
                                # Convert last_update to datetime if it's a string
                                last_update = diff_data.get("last_update")
                                if isinstance(last_update, str):
                                    from datetime import datetime
                                    try:
                                        last_update = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
                                    except:
                                        last_update = None
                                
                                try:
                                    await glob.db.execute(
                                        "INSERT INTO maps ("
                                        "id, server, set_id, status, md5, artist, title, version, creator, "
                                        "filename, last_update, total_length, max_combo, frozen, plays, passes, "
                                        "mode, bpm, cs, od, ar, hp, diff"
                                        ") VALUES ("
                                        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
                                        ") AS new ON DUPLICATE KEY UPDATE "
                                        "status = new.status, md5 = new.md5, last_update = new.last_update",
                                        [
                                            diff_bid,
                                            "osu!",
                                            int(diff_data["beatmapset_id"]),
                                            int(diff_data["approved"]),
                                            diff_data["file_md5"],
                                            diff_data.get("artist", "Unknown"),
                                            diff_data.get("title", "Unknown"),
                                            diff_data.get("version", "Unknown"),
                                            diff_data.get("creator", "Unknown"),
                                            f"{diff_data.get('artist', 'Unknown')} - {diff_data.get('title', 'Unknown')} ({diff_data.get('creator', 'Unknown')}) [{diff_data.get('version', 'Unknown')}].osu",
                                            last_update,
                                            int(diff_data.get("total_length", 0)),
                                            int(diff_data["max_combo"]) if diff_data.get("max_combo") else 0,
                                            0,  # frozen
                                            0,  # plays
                                            0,  # passes
                                            int(diff_data.get("mode", 0)),
                                            float(diff_data["bpm"]) if diff_data.get("bpm") else 0.0,
                                            float(diff_data.get("diff_size", 5.0)),
                                            float(diff_data.get("diff_overall", 5.0)),
                                            float(diff_data.get("diff_approach", 5.0)),
                                            float(diff_data.get("diff_drain", 5.0)),
                                            float(diff_data.get("difficultyrating", 0.0)),
                                        ]
                                    )
                                except Exception as db_error:
                                    if glob.config.debug:
                                        log(f"DB error saving difficulty {diff_bid}: {db_error}")
                            
                            if glob.config.debug:
                                log(f"Successfully saved all {len(all_diffs_data)} difficulties to DB")
                
                # Now fetch the requested beatmap from DB
                bmap = await glob.db.fetch("SELECT * FROM maps WHERE id = %s", [bid])
                # Now fetch the requested beatmap from DB
                bmap = await glob.db.fetch("SELECT * FROM maps WHERE id = %s", [bid])
                
                if not bmap:
                    if glob.config.debug:
                        log(f"Failed to save/fetch beatmap {bid} from DB after API fetch")
                    return await render_template("404.html"), 404
                
        except Exception as e:
            if glob.config.debug:
                log(f"Error loading beatmap {bid}: {e}")
                import traceback
                traceback.print_exc()
            return await render_template("404.html"), 404

    # Get all difficulties in the set (should already be in DB now)
    bmapset = await glob.db.fetchall(
        "SELECT diff, status, version, id, mode FROM maps WHERE set_id = %s ORDER BY diff",
        [bmap["set_id"]],
    )
    
    # Ensure bmapset has at least the current beatmap
    if not bmapset:
        if glob.config.debug:
            log(f"Warning: No difficulties found for set {bmap['set_id']}, creating single entry")
        bmapset = [{
            "id": bmap["id"],
            "status": bmap.get("status", 0),
            "version": bmap.get("version", "Unknown"),
            "mode": bmap.get("mode", 0),
            "diff": bmap.get("diff", 0.0),
        }]

    # Mode string mapping
    _mode_str_dict = {
        0: "std",
        1: "taiko",
        2: "catch",
        3: "mania",
    }

    # Status string mapping
    _status_str_dict = {
        -2: "Graveyard",
        -1: "Not Submitted",
        0: "Pending",
        1: "Update Available",
        2: "Ranked",
        3: "Approved",
        4: "Qualified",
        5: "Loved",
    }

    # Process beatmap set
    for _bmap in bmapset:
        _bmap["diff"] = round(_bmap["diff"], 2)
        _bmap["modetext"] = _mode_str_dict.get(_bmap["mode"], "std")
        _bmap["diff_color"] = utils.get_difficulty_colour_spectrum(_bmap["diff"])
        _bmap["icon"] = utils.get_mode_icon(_bmap["mode"])
        _bmap["status"] = _status_str_dict.get(_bmap["status"], "Unknown")

    # Process current beatmap
    bmap["diff"] = round(bmap["diff"], 2)
    bmap["diff_color"] = utils.get_difficulty_colour_spectrum(bmap["diff"])
    status = _status_str_dict.get(bmap["status"], "Unknown")

    return await render_template(
        "beatmap.html",
        bmap=bmap,
        bmapset=bmapset,
        status=status,
        mode=mode,
        mods=mods,
    )

