from __future__ import annotations

import os
from urllib.parse import quote

# app name
app_name = os.getenv("GUWEB_APP_NAME")

# secret key
secret_key = os.getenv("GUWEB_SECRET_KEY")

# hCaptcha settings:
hCaptcha_sitekey = os.getenv("GUWEB_HCAPTCHA_SITEKEY")
hCaptcha_secret = os.getenv("GUWEB_HCAPTCHA_SECRET")
# domain (used for api, avatar, etc)
domain = os.getenv("DOMAIN")

# osu! API key (for fetching beatmap data)
osu_api_key = os.getenv("OSU_API_KEY")

# max image size for avatars, in megabytes
max_image_size = 5

# mysql credentials
mysql = {
    "db": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
}

# redis credentials
redis = {
    "host": os.getenv("REDIS_HOST", "redis"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "db": int(os.getenv("REDIS_DB", "0")),
    "password": os.getenv("REDIS_PASS", ""),
}

# path to gulag/bancho.py root (must have leading and following slash)
path_to_gulag = "/home/ubuntu/bancho.py/"

# enable debug (disable when in production to improve performance)
debug = os.getenv("DEBUG", "false").lower() == "true"

# disallowed names (hardcoded banned usernames)
disallowed_names = set(os.getenv("DISALLOWED_NAMES").split(","))

# disallowed passwords (hardcoded banned passwords)
disallowed_passwords = set(os.getenv("DISALLOWED_PASSWORDS").split(","))

# enable registration
registration = os.getenv("GUWEB_REGISTRATION", "true").lower() in ("true", "1", "yes")

# social links (used throughout guweb)
github = "https://github.com/Inlayo-osu"
discord_server = "https://discord.com/invite/FeCUQNphyh"
youtube = "https://youtube.com/@Inlayo123"
twitter = "https://twitter.com/@Inlayo123"
instagram = "https://instagram.com/@Inlayo123"
skins = "https://github.com/Inlayo/Inlayo-skins"
fruitbox = "https://discord.gg/6PskvYDkpQ"
twitch = "https://twitch.tv/Inlayo"
