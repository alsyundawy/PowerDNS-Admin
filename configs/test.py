import os

basedir = os.path.abspath(os.path.dirname(__file__))

### BASIC APP CONFIG
SALT = os.getenv("SALT", "$2b$12$yLUMTIfl21FKJQpTkRQXCu")
SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key-32chars-powerdns")
BIND_ADDRESS = os.getenv("BIND_ADDRESS", "127.0.0.1")
PORT = int(os.getenv("PORT", "9191"))
HSTS_ENABLED = False

### DATABASE - SQLite
TEST_DB_LOCATION = os.getenv("TEST_DB_LOCATION", os.path.join(basedir, "testing.sqlite"))
SQLALCHEMY_DATABASE_URI = "sqlite:///{0}".format(TEST_DB_LOCATION)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# SAML Authentication
SAML_ENABLED = False

# TEST SAMPLE DATA
TEST_USER = os.getenv("TEST_USER", "test")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "test")
TEST_ADMIN_USER = os.getenv("TEST_ADMIN_USER", "admin")
TEST_ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "admin")
TEST_USER_APIKEY = os.getenv("TEST_USER_APIKEY", "wewdsfewrfsfsdf")
TEST_ADMIN_APIKEY = os.getenv("TEST_ADMIN_APIKEY", "nghnbnhtghrtert")
