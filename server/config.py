"""Application configuration and shared extension instances.

Extensions live here (instead of app.py) so models, resources and seed.py
can import them without creating circular imports.
"""
import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Signs the session cookie. Always set SECRET_KEY in any real deployment.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret-change-me")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Named constraints let Alembic generate migrations SQLite can apply (batch mode).
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})

db = SQLAlchemy(metadata=metadata)
db.init_app(app)

migrate = Migrate(app, db, render_as_batch=True)
bcrypt = Bcrypt(app)
api = Api(app)