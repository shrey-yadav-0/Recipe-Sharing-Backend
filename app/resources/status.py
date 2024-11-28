import os

from celery.result import AsyncResult
from flask import Blueprint
from app.extensions import mongo

status_bp = Blueprint("status", __name__)


@status_bp.route('/application-status')
def application_status():
    return "Recipe Sharing Backend application is running successfully."


@status_bp.route('/database-connection-status')
def database_connection_status():
    try:
        database_list = mongo.cx.list_database_names()
        database_name = os.getenv("MONGO_URI").split('/')[-1]
        database_name = database_name.split('?')[0]
        if database_name in database_list:
            status = f"{database_name} is connected.", 200
        else:
            status = f"{database_name} is not connected.", 500
    except Exception as e:
        status = f"Database connection failed: {str(e)}", 500
    return status


@status_bp.get("/celery/result/<task_id>")
def task_result(task_id: str) -> dict[str, object]:
    result = AsyncResult(task_id)
    return {
        "ready": result.ready(),
        "successful": result.successful(),
        "value": result.result if result.ready() else None,
    }
