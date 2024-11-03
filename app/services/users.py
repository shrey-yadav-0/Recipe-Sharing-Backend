import time

from celery import shared_task
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import abort
from itsdangerous import URLSafeTimedSerializer

from app.extensions import bcrypt, mongo
from app.utils import get_current_time


def hash_password(password):
    password_hash = bcrypt.generate_password_hash(password)
    return password_hash


def validate_user_data(data, password):
    required_fields = ["username", "email", "first_name", "last_name"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if not password:
        missing_fields.append("password")
    if missing_fields:
        abort(400, message=f"Please provide all required fields: {', '.join(missing_fields)}.")

    user = mongo.db.users.find_one({"$or": [{"username": data["username"]}, {"email": data["email"]}]})
    if user and user.get("username") == data["username"]:
        abort(409, message="This username already exists")
    if user and user.get("email") == data["email"]:
        abort(409, message="This email already exists")


def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=current_app.config["EMAIL_VERIFICATION_SALT"])


def generate_jwt_tokens(username, refresh=True):
    tokens = {}
    access_token = create_access_token(identity=username)
    tokens.update({"access_token": access_token})
    if refresh is True:
        refresh_token = create_refresh_token(identity=username)
        tokens.update({"refresh_token": refresh_token})
    return tokens


def revoke_jwt_token(jti, ttype, username):
    user_id = str(mongo.db.users.find_one({"username": username}).get("_id"))
    data = {
        "jti": jti,
        "token_type": ttype,
        "user_id": user_id,
        "revoked_at": get_current_time()
    }
    mongo.db.blocklisted_tokens.insert_one(data)


@shared_task(ignore_result=False)
def add_together(a: int, b: int) -> int:
    try:
        print("SLEEPING FOR 20s")
        time.sleep(20)
        print(1/0)
        print(a + b)
        return a + b
    except Exception as e:
        print(e)
