import os

basedir = os.path.abspath(os.path.dirname(__file__))

### BASIC APP CONFIG
SALT = os.getenv("SALT", "$2b$12$yLUMTIfl21FKJQpTkRQXCu")
SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key-32chars")
BIND_ADDRESS = os.getenv("BIND_ADDRESS", "127.0.0.1")
PORT = int(os.getenv("PORT", "9191"))
SERVER_EXTERNAL_SSL = os.getenv("SERVER_EXTERNAL_SSL", None)

### DATABASE CONFIG
SQLA_DB_USER = os.getenv("SQLA_DB_USER", "pda")
SQLA_DB_PASSWORD = os.getenv("SQLA_DB_PASSWORD", "")
SQLA_DB_HOST = os.getenv("SQLA_DB_HOST", "127.0.0.1")
SQLA_DB_NAME = os.getenv("SQLA_DB_NAME", "pda")
SQLALCHEMY_TRACK_MODIFICATIONS = True

# CAPTCHA Config
CAPTCHA_ENABLE = True
CAPTCHA_LENGTH = 6
CAPTCHA_WIDTH = 160
CAPTCHA_HEIGHT = 60
CAPTCHA_SESSION_KEY = "captcha_image"

# Server side sessions tracking
SESSION_TYPE = "sqlalchemy"

# Database URI (Defaults to SQLite for local development)
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///" + os.path.join(basedir, "pdns.db"))

# SAML Authentication
SAML_ENABLED = False
