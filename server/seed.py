"""Reset the database and fill it with demo users and notes.

Run from the server/ directory after migrating:  python seed.py
"""
from random import randint, seed as random_seed

from faker import Faker

from app import app
from config import db
from models import Note, User

DEMO_PASSWORD = "password123"

fake = Faker()
Faker.seed(42)
random_seed(42)


def create_users():
    usernames = ["demo", "alice", "bob"]
    users = []
    for username in usernames:
        user = User(username=username)
        user.password_hash = DEMO_PASSWORD
        users.append(user)
    db.session.add_all(users)
    db.session.commit()
    return users


def create_notes(users):
    notes = []
    for user in users:
        # demo gets enough notes to show off several pages of pagination
        count = 25 if user.username == "demo" else randint(5, 10)
        for _ in range(count):
            notes.append(Note(
                title=fake.sentence(nb_words=5).rstrip("."),
                content=fake.paragraph(nb_sentences=4),
                user=user,
            ))
    db.session.add_all(notes)
    db.session.commit()
    return notes


if __name__ == "__main__":
    with app.app_context():
        print("Clearing existing data...")
        Note.query.delete()
        User.query.delete()
        db.session.commit()

        print("Creating users...")
        users = create_users()

        print("Creating notes...")
        notes = create_notes(users)

        print(f"Seeded {len(users)} users and {len(notes)} notes.")
        print(f"Log in as any of: {', '.join(u.username for u in users)} "
              f"(password: {DEMO_PASSWORD})")