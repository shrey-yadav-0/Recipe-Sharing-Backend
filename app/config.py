import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    # Flask App
    SECRET_KEY = os.getenv("SECRET_KEY")
    EMAIL_VERIFICATION_SALT = os.getenv("EMAIL_VERIFICATION_SALT").encode()

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY").encode()

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # Celery
    CELERY = dict(
        broker_url=os.getenv("CELERY_BROKER_URL"),
        result_backend=os.getenv("CELERY_RESULT_BACKEND"),
        task_ignore_result=True,
        broker_connection_retry_on_startup=True
    )


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
