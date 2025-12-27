from __future__ import annotations

import os

# app name
app_name = os.getenv("GUWEB_APP_NAME", "bancho.py")

# secret key
secret_key = os.getenv("GUWEB_SECRET_KEY", "changeme")

# hCaptcha settings:
hCaptcha_sitekey = os.getenv("GUWEB_HCAPTCHA_SITEKEY", "changeme")
hCaptcha_secret = os.getenv("GUWEB_HCAPTCHA_SECRET", "changeme")

# domain (used for api, avatar, etc)
domain = os.getenv("DOMAIN", "localhost")

# max image size for avatars, in megabytes
max_image_size = int(os.getenv("GUWEB_MAX_IMAGE_SIZE", "5"))

# mysql credentials
mysql = {
    "db": os.getenv("DB_NAME", "bancho"),
    "host": os.getenv("DB_HOST", "mysql"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
}

# path to bancho.py root (for API access)
# Since guweb is in the same container/network, it can access bancho via service name
path_to_gulag = "/home/ubuntu/bancho.py/"

# enable debug (disable when in production to improve performance)
debug = os.getenv("GUWEB_DEBUG", "false").lower() == "true"

# disallowed names (hardcoded banned usernames)
disallowed_names = {
    "BanchoBot",
    "Guest",
}

# disallowed passwords (hardcoded banned passwords)
disallowed_passwords = {
    "password",
}

# enable registration
registration = True

# redis credentials
redis = {
    "host": os.getenv("REDIS_HOST", "redis"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "db": int(os.getenv("REDIS_DB", "0")),
}

# Email settings for verification
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@example.com")
SENDER_EMAIL_PASSWORD = os.getenv("SENDER_EMAIL_PASSWORD", "")
SenderEmail = SENDER_EMAIL  # alias for templates

# SMTP and IMAP server settings (Daum Mail)
SMTP_SERVER_INFO = {
    "host": os.getenv("SMTP_HOST", "smtp.daum.net"),
    "port": int(os.getenv("SMTP_PORT", "465")),
}

IMAP_SERVER_INFO = {
    "host": os.getenv("IMAP_HOST", "imap.daum.net"),
    "port": int(os.getenv("IMAP_PORT", "993")),
}

# Email verification settings
EmailVerifyKeyLength = int(os.getenv("EMAIL_VERIFY_KEY_LENGTH", "32"))
SentEmailTimeout = int(os.getenv("SENT_EMAIL_TIMEOUT", "300"))  # 5 minutes in seconds

# Discord webhook for email logs
DISCORD_EMAIL_LOG_WEBHOOK = os.getenv("DISCORD_EMAIL_LOG_WEBHOOK", "")

# social links (used throughout guweb)
github = os.getenv("GUWEB_GITHUB", "https://github.com/changeme")
discord = os.getenv("GUWEB_DISCORD", "https://discord.gg/changeme")
youtube = os.getenv("GUWEB_YOUTUBE", "https://youtube.com/@changeme")
twitter = os.getenv("GUWEB_TWITTER", "https://twitter.com/changeme")
instagram = os.getenv("GUWEB_INSTAGRAM", "https://instagram.com/changeme")
twitch = os.getenv("GUWEB_TWITCH", "https://twitch.tv/changeme")
osuserver = os.getenv("GUWEB_OSUSERVER", "https://osu-server-list.com/server/changeme")
fruitbox = os.getenv("GUWEB_FRUITBOX", "https://gamesaien.com/game/fruit_box_a/")
hwahong = os.getenv("GUWEB_HWAHONG", "https://hwahong.com")
skins = os.getenv("GUWEB_SKINS", "https://skins.com")
