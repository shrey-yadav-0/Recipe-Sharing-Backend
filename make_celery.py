import os

from dotenv import load_dotenv

from app import create_app

load_dotenv()

environment = os.getenv("ENVIRONMENT")
print(f"Environment: {environment.upper()}")

flask_app = None

if environment == "development":
    from app.config import DevelopmentConfig
    flask_app = create_app(DevelopmentConfig)

elif environment == "testing":
    from app.config import TestingConfig
    flask_app = create_app(TestingConfig)

elif environment in ["staging", "production"]:
    from app.config import ProductionConfig
    flask_app = create_app(ProductionConfig)

celery_app = flask_app.extensions["celery"]
