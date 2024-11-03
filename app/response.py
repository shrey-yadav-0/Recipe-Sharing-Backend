from flask import jsonify, make_response


class Response:
    def __init__(self, status, message=None, data=None, error=None, status_code=200):
        self.status = status
        self.message = message
        self.data = data
        self.error = error
        self.status_code = status_code

    def send_response(self):
        response_body = {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "error": self.error
        }
        # Remove keys with `None` values for a cleaner response
        response_body = {k: v for k, v in response_body.items() if v is not None}
        return make_response(jsonify(response_body), self.status_code)
