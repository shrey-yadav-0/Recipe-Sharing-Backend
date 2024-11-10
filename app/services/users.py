import os

from celery import shared_task
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_mail import Message
from flask_restful import abort
from itsdangerous import URLSafeTimedSerializer

from app.extensions import bcrypt, mongo, mail
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
def send_verification_email(name, email, verification_token):
    subject = "Verify Email"
    recipients = [email]
    body = f"""Hello {name},\nThank you for registering on Recipe Sharing Platform. Please click on the following 
    link to verify your email:\n\nhttp://192.168.1.10:5000/users/email-verification/{verification_token}"""
    sender = os.getenv("MAIL_USERNAME")

    message = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        sender=sender
    )
    mail.send(message)


def verify_email(verification_token):
    user_data = mongo.db.users.find_one({"verification_token": verification_token})
    if user_data:
        current_time = get_current_time()
        mongo.db.users.update_one({"email": user_data["email"]},
                                  {"$set": {"is_verified": True, "email_verified_at": current_time}})
    else:
        abort(400, message="Invalid token")
