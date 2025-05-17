from os import environ

API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", ""))

# Admins as a list of integers
ADMINS = environ.get("ADMINS", "")
ADMINS = [int(admin_id) for admin_id in ADMINS.split() if admin_id.strip()]

# MongoDB config
DB_URI = environ.get("DB_URI", "")
DB_NAME = environ.get("DB_NAME", "autoacceptbot")

# Feature toggles
NEW_REQ_MODE = environ.get('NEW_REQ_MODE', 'True').lower() in ("true", "1", "yes")
IS_FSUB = environ.get("FSUB", "True").lower() in ("true", "1", "yes")

# Authorized channels as a list of integers
AUTH_CHANNELS = environ.get("AUTH_CHANNEL", "")
AUTH_CHANNELS = [int(channel_id.strip()) for channel_id in AUTH_CHANNELS.split(",") if channel_id.strip()]
