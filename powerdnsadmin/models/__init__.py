from flask_migrate import Migrate

from .account import Account
from .account_user import AccountUser
from .api_key import ApiKey
from .api_key_account import ApiKeyAccount
from .base import db
from .domain import Domain
from .domain_setting import DomainSetting
from .domain_template import DomainTemplate
from .domain_template_record import DomainTemplateRecord
from .domain_user import DomainUser
from .history import History
from .record import Record
from .record_entry import RecordEntry
from .role import Role
from .server import Server
from .setting import Setting
from .user import User

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
    Migrate(app, db)
