import os
import logging
from flask import Flask
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_session import Session
from .lib import utils


def create_app(config=None):
    from powerdnsadmin.lib.settings import AppSettings
    from . import models, routes, services
    from .assets import assets
    app = Flask(__name__)

    # Read log level from environment variable
    log_level_name = os.environ.get('PDNS_ADMIN_LOG_LEVEL', 'WARNING')
    log_level = logging.getLevelName(log_level_name.upper())
    # Setting logger
    logging.basicConfig(
       level=log_level,
        format=
        "[%(asctime)s] [%(filename)s:%(lineno)d] %(levelname)s - %(message)s")

    # If we use Docker + Gunicorn, adjust the
    # log handler
    if "GUNICORN_LOGLEVEL" in os.environ:
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # Proxy
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Load config from env variables if using docker
    if os.path.exists(os.path.join(app.root_path, 'docker_config.py')):
        app.config.from_object('powerdnsadmin.docker_config')
    else:
        # Load default configuration
        app.config.from_object('powerdnsadmin.default_config')

    # Load config file from FLASK_CONF env variable
    if 'FLASK_CONF' in os.environ:
        app.config.from_envvar('FLASK_CONF')

    # Load app specified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    # Load any settings defined with environment variables
    AppSettings.load_environment(app)

    # HSTS
    if app.config.get('HSTS_ENABLED'):
        from flask_sslify import SSLify
        _sslify = SSLify(app)  # lgtm [py/unused-local-variable]

    # Load app's database models first
    models.init_app(app)

    # Load Flask-Session
    app.config['SESSION_TYPE'] = app.config.get('SESSION_TYPE')
    if 'SESSION_TYPE' in os.environ:
        app.config['SESSION_TYPE'] = os.environ.get('SESSION_TYPE')

    if app.config.get('SESSION_TYPE') == 'sqlalchemy':
        app.config['SESSION_SQLALCHEMY'] = models.db
        try:
            import flask_session.sqlalchemy.sqlalchemy as fss_sqla

            def safe_create_session_model(db, table_name, schema=None, bind_key=None, sequence=None):
                table_args = {'extend_existing': True}
                if schema:
                    table_args['schema'] = schema

                class Session(db.Model):
                    __tablename__ = table_name
                    __table_args__ = table_args
                    __bind_key__ = bind_key

                    id = db.Column(db.Integer, primary_key=True)
                    session_id = db.Column(db.String(255), unique=True)
                    data = db.Column(db.BLOB)
                    expiry = db.Column(db.DateTime)

                    def __init__(self, session_id, data, expiry):
                        self.session_id = session_id
                        self.data = data
                        self.expiry = expiry

                return Session

            fss_sqla.create_session_model = safe_create_session_model
        except (ImportError, AttributeError):
            pass

    sess = Session(app)

    # create sessions table if using sqlalchemy backend
    if app.config.get('SESSION_TYPE') == 'sqlalchemy':
        with app.app_context():
            models.db.create_all()

    # SMTP
    app.mail = Mail(app)

    # Load app's components
    assets.init_app(app)
    routes.init_app(app)
    services.init_app(app)

    # Register filters
    app.jinja_env.filters['display_record_name'] = utils.display_record_name
    app.jinja_env.filters['display_master_name'] = utils.display_master_name
    app.jinja_env.filters['display_second_to_time'] = utils.display_time
    app.jinja_env.filters['display_setting_state'] = utils.display_setting_state
    app.jinja_env.filters['pretty_domain_name'] = utils.pretty_domain_name
    app.jinja_env.filters['format_datetime_local'] = utils.format_datetime
    app.jinja_env.filters['format_zone_type'] = utils.format_zone_type

    # Register context processors
    from .models.setting import Setting

    @app.context_processor
    def inject_sitename():
        setting = Setting().get('site_name')
        return dict(SITE_NAME=setting)

    @app.context_processor
    def inject_setting():
        setting = Setting()
        return dict(SETTING=setting)

    @app.context_processor
    def inject_pdns_version():
        setting = Setting().get('pdns_version')
        return dict(pdns_version=setting)

    return app
