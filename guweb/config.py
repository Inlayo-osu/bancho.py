from __future__ import annotations

import os

# app name
app_name = os.getenv("GUWEB_APP_NAME", "bancho.py")

# secret key
secret_key = os.getenv("GUWEB_SECRET_KEY", "changeme_secret_key_12345")

# hCaptcha settings:
hCaptcha_sitekey = os.getenv("GUWEB_HCAPTCHA_SITEKEY", "changeme")
hCaptcha_secret = os.getenv("GUWEB_HCAPTCHA_SECRET", "changeme")

# domain (used for api, avatar, etc)
domain = os.getenv("DOMAIN", "localhost")

# max image size for avatars, in megabytes
max_image_size = 5

# mysql credentials
mysql = {
    "db": os.getenv("DB_NAME", "bancho"),
    "host": os.getenv("DB_HOST", "mysql"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "changeme"),
}

# path to gulag/bancho.py root (must have leading and following slash)
path_to_gulag = "/srv/root/"

# enable debug (disable when in production to improve performance)
debug = os.getenv("GUWEB_DEBUG", "false").lower() in ("true", "1", "yes")

# disallowed names (hardcoded banned usernames)
disallowed_names = {"cookiezi", "rrtyui", "hvick225", "qsc20010"}

# disallowed passwords (hardcoded banned passwords)
disallowed_passwords = {"password", "minilamp"}

# enable registration
registration = os.getenv("GUWEB_REGISTRATION", "true").lower() in ("true", "1", "yes")

# social links (used throughout guweb)
github = "https://github.com/varkaria/guweb"
discord_server = "https://discord.com/invite/Y5uPvcNpD9"
youtube = "https://youtube.com/"
twitter = "https://twitter.com/"
instagram = "https://instagram.com/"
