"""Shared pytest fixtures. Uses an in-memory SQLite database per test."""
import os
import sys

# Must be set before config.py is imported so the app uses the test database.
os.environ["DATABASE_URL"] = "sqlite://"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from app import app  # noqa: E402
from config import db  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()