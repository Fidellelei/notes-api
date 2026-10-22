"""Session helpers and the login_required guard shared by protected resources."""
from functools import wraps

from flask import g, session

from config import db
from models import User


def current_user():
    """Return the logged-in User, or None. Clears stale ids (e.g. deleted users)."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    user = db.session.get(User, user_id)
    if user is None:
        session.pop("user_id", None)
    return user


def login_required(func):
    """Reject the request with 401 unless a user is logged in; exposes it as g.current_user."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return {"error": "Unauthorized. Please log in."}, 401
        g.current_user = user
        return func(*args, **kwargs)
    return wrapper