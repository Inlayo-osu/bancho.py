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
path_to_gulag = "/srv/root/"

# enable debug (disable when in production to improve performance)
debug = os.getenv("GUWEB_DEBUG", "false").lower() == "true"

# disallowed names (hardcoded banned usernames)
disallowed_names = {
    "cookiezi",
    "rrtyui",
    "hvick225",
    "qsc20010",
    "peppy",
    "osz",
    "osz2",
    "admin",
    "administrator",
}

# disallowed passwords (hardcoded banned passwords)
disallowed_passwords = {
    "password",
    "123456",
    "123456789",
    "qwerty",
    "password123",
    "1234567890",
    "minilamp",
}

# enable registration
registration = True

# social links (used throughout guweb)
github = os.getenv("GUWEB_GITHUB", "https://github.com/osuAkatsuki/bancho.py")
discord_server = os.getenv("GUWEB_DISCORD", "https://discord.gg/ShEQgUx")
youtube = os.getenv("GUWEB_YOUTUBE", "https://youtube.com/")
twitter = os.getenv("GUWEB_TWITTER", "https://twitter.com/")
instagram = os.getenv("GUWEB_INSTAGRAM", "https://instagram.com/")
