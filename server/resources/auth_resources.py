from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from auth import current_user
from config import db
from models import User
from schemas import user_schema

MIN_PASSWORD_LENGTH = 8


class Signup(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password") or ""
        confirmation = data.get("password_confirmation")

        errors = []
        if not username:
            errors.append("Username is required.")
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        # Confirmation is optional, but must match when the client sends it.
        if confirmation is not None and confirmation != password:
            errors.append("Password confirmation does not match.")
        if errors:
            return {"errors": errors}, 422

        try:
            user = User(username=username)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username is already taken."]}, 422

        session["user_id"] = user.id
        return user_schema.dump(user), 201


class Login(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        user = User.query.filter_by(username=username).first()
        # Same message for unknown user and wrong password, so usernames can't be probed.
        if user is None or not user.authenticate(password):
            return {"error": "Invalid username or password."}, 401

        session["user_id"] = user.id
        return user_schema.dump(user), 200


class CheckSession(Resource):
    def get(self):
        user = current_user()
        if user is None:
            return {"error": "Unauthorized. Please log in."}, 401
        return user_schema.dump(user), 200


class Logout(Resource):
    def delete(self):
        if current_user() is None:
            return {"error": "Unauthorized. Please log in."}, 401
        session.pop("user_id", None)
        return {}, 204