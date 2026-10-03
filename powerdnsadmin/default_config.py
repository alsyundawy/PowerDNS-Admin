import os

basedir = os.path.abspath(os.path.dirname(__file__))

BIND_ADDRESS = os.getenv("BIND_ADDRESS", "127.0.0.1")
CAPTCHA_ENABLE = True
CAPTCHA_HEIGHT = 60
CAPTCHA_LENGTH = 6
CAPTCHA_SESSION_KEY = "captcha_image"
CAPTCHA_WIDTH = 160
CSRF_COOKIE_HTTPONLY = True
HSTS_ENABLED = False
PORT = 9191
SALT = os.getenv("SALT", "$2b$12$yLUMTIfl21FKJQpTkRQXCu")
SAML_ASSERTION_ENCRYPTED = True
SAML_ENABLED = False
SECRET_KEY = os.getenv("SECRET_KEY", "default-powerdnsadmin-secret-key-32")
SERVER_EXTERNAL_SSL = os.getenv("SERVER_EXTERNAL_SSL", True)
SESSION_CLEANUP_N_REQUESTS = 100
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_TYPE = "sqlalchemy"
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "pdns.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
