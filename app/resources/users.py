from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_restful import Api, Resource

from app.models.users import UserModel
from app.response import Response
from app.services.users import generate_jwt_tokens, revoke_jwt_token, add_together

users_bp = Blueprint("users", __name__, url_prefix="/users")
users_api = Api(users_bp)


class Users(Resource):
    @jwt_required()
    def get(self, user_id):
        user_data = UserModel.read(user_id=user_id)

        add_together.delay(3, 5)

        return Response(
            status="success",
            message="User data retrieval successful",
            data=user_data,
            status_code=200
        ).send_response()

    def post(self):
        """This method is used for new user registration"""

        request_data = request.get_json()
        data = {
            "username": request_data["username"],
            "email": request_data["email"],
            "first_name": request_data["first_name"],
            "last_name": request_data["last_name"],
        }
        password = request_data["password"]

        user_id = UserModel.create(data, password)

        response_data = {
            "user_id": user_id
        }
        return Response(
            status="success",
            message="Registration successful",
            data=response_data,
            status_code=201
        ).send_response()

    def put(self, user_id):
        pass


class Login(Resource):
    def post(self):
        request_data = request.get_json()
        login_credentials = {
            "username": request_data.get("username"),
            "email": request_data.get("email"),
            "password": request_data.get("password")
        }

        user_data = UserModel.read(login_required=True, login_credentials=login_credentials)
        tokens = generate_jwt_tokens(user_data["username"])

        response_data = {
            **tokens,
            "user": user_data
        }
        return Response(
            status="success",
            message="Login successful",
            data=response_data,
            status_code=200
        ).send_response()


class Logout(Resource):
    @jwt_required(verify_type=False)
    def delete(self):
        token = get_jwt()
        jti = token["jti"]
        ttype = token["type"]
        username = get_jwt_identity()

        revoke_jwt_token(jti, ttype, username)

        return Response(
            status="success",
            message=f"{ttype.capitalize()} token successfully revoked"
        ).send_response()


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()

        token = generate_jwt_tokens(username=identity, refresh=False)

        return Response(
            status="success",
            message=f"Access token successfully regenerated",
            data=token
        ).send_response()


users_api.add_resource(Users, "/", "/<user_id>")
users_api.add_resource(Login, "/auth/login")
users_api.add_resource(Logout, "/auth/logout")
users_api.add_resource(TokenRefresh, "/auth/token-refresh")
