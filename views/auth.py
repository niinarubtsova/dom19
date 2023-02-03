import datetime
import calendar

import jwt
from flask import request
from flask_restx import Resource, Namespace

from constants import JWT_SECRET, JWT_ALGORITHM
from models import User
from setup_db import db

auth_ns = Namespace('auth')


def generate_tokens(data) -> dict:
    # 30 min access_token живет
    min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    data["exp"] = calendar.timegm(min30.timetuple())
    access_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # 130 days refresh_token живет
    days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
    data["exp"] = calendar.timegm(days130.timetuple())
    refresh_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_ns.route('/')
class AuthsView(Resource):
    def post(self):
        req_json = request.json
        username = req_json.get("username", None)
        password = req_json.get("password", None)
        if None in [username, password]:
            return "", 400

        user = db.session.query(User).filter(User.username == username).first()

        if user is None or not user.compare_passwords(password):
            return "no such user or wrong username and/or password", 404

        data = {
            "username": user.username,
            "password": user.password,
            "role": user.role
        }

        tokens = generate_tokens(data)

        return tokens, 201

    def put(self):
        req_json = request.json
        token = req_json.get("refresh_token")
        try:
            data = jwt.decode(jwt=token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
            username = data.get("username")
            password = data.get("password")

            user = db.session.query(User).filter(User.username == username).first()

            if user is None or user.password != password:
                return "no such user or wrong username and/or password", 404

            tokens = generate_tokens(data)
            return tokens, 201
        except jwt.ExpiredSignatureError as ex:
            return "token expired", 401
        except jwt.InvalidTokenError as ex:
            return "token is not valid", 401