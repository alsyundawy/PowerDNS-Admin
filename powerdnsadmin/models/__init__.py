from flask_migrate import Migrate

from .base import db
from .user import User
from .role import Role
from .account import Account
from .account_user import AccountUser
from .server import Server
from .history import History
from .api_key import ApiKey
from .api_key_account import ApiKeyAccount
from .setting import Setting
from .domain import Domain
from .domain_setting import DomainSetting
from .domain_user import DomainUser
from .domain_template import DomainTemplate
from .domain_template_record import DomainTemplateRecord
from .record import Record
from .record_entry import RecordEntry

__all__ = [
    "db",
    "User",
    "Role",
    "Account",
    "AccountUser",
    "Server",
    "History",
    "ApiKey",
    "ApiKeyAccount",
    "Setting",
    "Domain",
    "DomainSetting",
    "DomainUser",
    "DomainTemplate",
    "DomainTemplateRecord",
    "Record",
    "RecordEntry",
    "init_app",
]


def init_app(app):
    db.init_app(app)
    _migrate = Migrate(app, db)  # lgtm [py/unused-local-variable]
