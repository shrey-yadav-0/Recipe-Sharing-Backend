from app.resources.status import status_bp
from app.resources.users import users_bp


def register_blueprints(app):
    app.register_blueprint(status_bp)
    app.register_blueprint(users_bp)
