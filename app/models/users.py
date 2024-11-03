from flask_restful import abort

from app.extensions import mongo, bcrypt
from app.services.users import hash_password, validate_user_data, generate_verification_token
from app.utils import get_current_time


class UserModel:
    @staticmethod
    def create(data, password):
        validate_user_data(data, password)

        current_time = get_current_time()
        data["password"] = hash_password(password)
        data["profile_picture"] = None
        data["bio"] = None
        data["registration_date"] = current_time
        data["last_updated"] = current_time
        data["is_verified"] = False
        data["verification_token"] = generate_verification_token(data["email"])
        data["email_verified_at"] = None

        result = mongo.db.users.insert_one(data)
        user_id = str(result.inserted_id)
        return user_id

    @staticmethod
    def read(user_id=None, login_required=False, login_credentials=None):
        match_filter = {}
        if user_id:
            pass
        if login_required is True:
            match_filter.update({"$or": [{"username": login_credentials["username"]},
                                         {"email": login_credentials["email"]}]})

        project = {"_id": 0, "user_id": {"$toString": "$_id"}, "username": 1, "email": 1, "first_name": 1,
                   "last_name": 1, "profile_picture": 1, "bio": 1, "password": 1}

        user_data = mongo.db.users.find_one(match_filter, project)
        if not user_data:
            if login_required is True:
                message = "This username or email does not exist"
            else:
                message = "This user ID does not exist"
            abort(404, message=message)
        if login_required is True and not bcrypt.check_password_hash(user_data["password"],
                                                                     login_credentials["password"]):
            abort(401, message="Password is incorrect")

        user_data.pop("password")
        return user_data

    @staticmethod
    def update():
        pass
