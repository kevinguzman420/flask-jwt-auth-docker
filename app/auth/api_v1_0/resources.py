from flask import request, current_app
from flask_restful import Api, Resource

from app.auth.models import User, BlacklistToken
from app.auth.api_v1_0 import auth_bp
from app.common.mail import send_email
from app import bcrypt

api = Api(auth_bp)


class Register(Resource):
    """User Registration Resource"""

    def post(self):
        post_data = request.get_json()
        user = User.query.filter_by(email=post_data.get("email")).first()
        if not user:
            try:
                user = User(
                    email=post_data.get("email"), password=post_data.get("password")
                )
                user.save()
                auth_token = user.encode_auth_token(user.id)
                responseObject = {
                    "status": "success",
                    "message": "Successfully registered.",
                    "auth_token": auth_token,
                }
                send_email(
                    subject="Bienvenid@! Felicidades por tu registro!",
                    sender=current_app.config["DONT_REPLY_FROM_EMAIL"],
                    recipients=[
                        post_data.get("email"),
                    ],
                    text_body=f'Hola {post_data.get("email")}, felicidades por tu registro! - text',
                    html_body=f'<p>Hola <strong>{post_data.get("email")}</strong>, bienvenid@!!! - html</p>',
                )
                return responseObject, 201
            except Exception as e:
                responseObject = {
                    "status": "fail",
                    "message": "Some error occurred. Please try again",
                }
                return responseObject, 401
        else:
            responseObject = {
                "status": "fail",
                "message": "User already exists. Please Log in.",
            }
            return responseObject, 202


api.add_resource(Register, "/auth/register/", endpoint="register")


class Login(Resource):
    """
    User Login Resource
    """

    def post(self):
        # get the post data
        data = request.get_json()
        try:
            # fetch the user data
            user = User.query.filter_by(email=data.get("email")).first()
            if user and bcrypt.check_password_hash(user.password, data.get("password")):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        "status": "success",
                        "message": "Successfully logged in.",
                        "auth_token": auth_token,
                    }
                    return responseObject, 200
            else:
                responseObject = {"status": "fail", "message": "User does not exist."}
                return responseObject, 404
        except Exception as e:
            print(e)
            responseObject = {"status": "fail", "message": "Try again"}
            return responseObject, 500


api.add_resource(Login, "/auth/login/", endpoint="login")


class UserApi(Resource):
    """User Resource"""

    def get(self):
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    "status": "fail",
                    "message": "Bearer token malformed.",
                }
                return responseObject, 401
        else:
            auth_token = None
        if auth_token is not None:
            resp = User.decode_auth_token(auth_token)  # receive user id as int
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                responseObject = {
                    "status": "success",
                    "data": {
                        "user_id": user.id,
                        "email": user.email,
                        "admin": user.admin,
                        "registered_on": user.registered_on.strftime(
                            "%m-%d-%Y %H:%M:%S"
                        ),
                    },
                }
                return responseObject, 200
            responseObject = {"status": "fail", "message": resp}
            return responseObject, 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return responseObject, 401


api.add_resource(UserApi, "/auth/status/", endpoint="get_user_data")


class Logout(Resource):
    """Logout Resource"""

    def post(self):
        # get auth token
        auth_header = request.headers.get("Authorization")
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = None
        if auth_token is not None:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    blacklist_token.save()
                    responseObject = {
                        "status": "success",
                        "message": "Successfully logged out.",
                    }
                    return responseObject, 200
                except Exception as e:
                    responseObject = {"status": "fail", "message": e}
                    return responseObject, 200
            else:
                responseObject = {"status": "fail", "message": resp}
                return responseObject, 401
        else:
            responseObject = {
                "status": "fail",
                "message": "Provide a valid auth token.",
            }
            return responseObject, 403


api.add_resource(Logout, "/auth/logout/", endpoint="logout")
