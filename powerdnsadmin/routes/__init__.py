from .admin import admin_bp
from .api import api_bp, apilist_bp
from .base import (
    captcha,
    csrf,
    handle_access_forbidden,
    handle_bad_request,
    handle_internal_server_error,
    handle_page_not_found,
    handle_unauthorized_access,
    login_manager,
)
from .dashboard import dashboard_bp
from .domain import domain_bp
from .index import index_bp
from .user import user_bp


def init_app(app):
    login_manager.init_app(app)
    csrf.init_app(app)
    captcha.init_app(app)

    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(domain_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(apilist_bp)

    app.register_error_handler(400, handle_bad_request)
    app.register_error_handler(401, handle_unauthorized_access)
    app.register_error_handler(403, handle_access_forbidden)
    app.register_error_handler(404, handle_page_not_found)
    app.register_error_handler(500, handle_internal_server_error)
