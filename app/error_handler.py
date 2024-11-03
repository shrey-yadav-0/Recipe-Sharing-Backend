import traceback

from app.response import Response


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(traceback.format_exc())
        error = dict()
        error["message"] = str(e)

        # Return response
        return Response(
            status="error",
            message="Internal Server Error",
            error=error,
            status_code=500
        ).send_response()

    return app
