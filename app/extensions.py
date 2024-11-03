from celery import Celery, Task
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_pymongo import PyMongo

mongo = PyMongo()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()
mail = Mail()


def init_extensions(app):
    # Initialize PyMongo extension for Flask app
    mongo.init_app(app)

    # Initialize Bcrypt extension for Flask app
    bcrypt.init_app(app)

    # Initialize JWT extension for Flask app and set callbacks
    jwt.init_app(app)
    set_jwt_callbacks()

    # Initialize CORS extension for Flask app
    cors.init_app(app)

    # Initialize Mail extension for Flask app
    mail.init_app(app)

    # Initialize Celery for Flask app
    celery_init_app(app)


def set_jwt_callbacks():
    # Callback function to check if a JWT exists in the database blocklist
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = mongo.db.blocklisted_tokens.find_one({"jti": jti})

        return token is not None


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
