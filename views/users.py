from flask import request
from flask_restx import Resource, Namespace

from models import User, UserSchema
from setup_db import db

user_ns = Namespace('users')


@user_ns.route('/')
class UsersView(Resource):
    def get(self):
        rs = db.session.query(User).all()
        res = UserSchema(many=True).dump(rs)
        return res, 200

    def post(self):
        req_json = request.json
        ent = User(**req_json)

        db.session.add(ent)
        db.session.commit()
        return "", 201, {"location": f"/users/{ent.id}"}


@user_ns.route('/<int:rid>')
class UserView(Resource):
    def get(self, rid):
        r = db.session.query(User).get(rid)
        sm_d = UserSchema().dump(r)
        return sm_d, 200

    def put(self, rid):
        user = db.session.query(User).get(rid)
        req_json = request.json
        user.name = req_json.get("name")
        user.password = req_json.get("password")
        user.password = user.get_hash()
        user.role = req_json.get("role")

        db.session.add(user)
        db.session.commit()
        return "", 204

    def delete(self, rid):
        user = db.session.query(User).get(rid)

        db.session.delete(user)
        db.session.commit()
        return "", 204