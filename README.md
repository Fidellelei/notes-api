# Notes API: Full Auth Flask Backend

A secure RESTful Flask API for a personal notes productivity app. Users can sign up, log in, and create, read, update and delete their own notes. Authentication uses **server-side sessions** (signed, HttpOnly cookies), passwords are hashed with **bcrypt**, and every notes endpoint is protected so users can only ever see or change their own notes. The notes index is **paginated**.

Built to work with the provided **Sessions** frontend client.

## Tech Stack

- Flask 2.2 and Flask-RESTful
- Flask-SQLAlchemy and SQLite
- Flask-Migrate (Alembic) for migrations
- Flask-Bcrypt for password hashing
- Marshmallow for serialization and input validation
- Faker for seed data
- Pytest for tests

## Project Structure

```
notes-api/
├── Pipfile
├── README.md
└── server/
    ├── app.py                 # Entry point: registers routes, runs the server
    ├── config.py              # App config and shared extensions (db, bcrypt, api, migrate)
    ├── models.py              # User and Note models
    ├── schemas.py             # Marshmallow schemas (JSON output and input validation)
    ├── auth.py                # current_user() helper and @login_required guard
    ├── seed.py                # Resets and seeds the database
    ├── resources/
    │   ├── auth_resources.py  # /signup, /login, /check_session, /logout
    │   └── note_resources.py  # /notes CRUD with pagination and ownership checks
    ├── migrations/            # Flask-Migrate migration history
    └── tests/                 # Pytest suite
```

## Installation

Requires Python 3.12 (or edit `python_version` in the `Pipfile` to match your version) and [pipenv](https://pipenv.pypa.io/).

```bash
git clone <your-repo-url>
cd notes-api
pipenv install
pipenv shell
```

Set up the database and add sample data:

```bash
cd server
flask db upgrade
python seed.py
```

`seed.py` creates three users, **demo**, **alice** and **bob**, all with the password `password123`. `demo` has 25 notes, so pagination is easy to see.

## Running the App

From the `server/` directory:

```bash
python app.py
```

The API runs at **http://localhost:5555**. To use it with the Sessions frontend client, point the client's proxy at `http://localhost:5555`.

Optionally, set a secret key for signing session cookies (recommended outside local development):

```bash
export SECRET_KEY="a-long-random-string"
```

## Running Tests

From the `server/` directory:

```bash
pytest -v
```

Tests use an in-memory database, so they never touch `app.db`.

## API Endpoints

All request and response bodies are JSON. Session cookies are set on signup/login and must be sent with later requests.

### Authentication

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| POST | `/signup` | Create an account and log in. Body: `username`, `password` (min 8 chars), optional `password_confirmation`. | `201` user | `422` invalid input or username taken |
| POST | `/login` | Log in. Body: `username`, `password`. | `200` user | `401` invalid credentials |
| GET | `/check_session` | Return the logged-in user (keeps users logged in on refresh). | `200` user | `401` not logged in |
| DELETE | `/logout` | Log out and clear the session. | `204` | `401` not logged in |

A user is returned as `{ "id": 1, "username": "demo" }`. The password hash is never returned.

### Notes (login required)

Every notes endpoint returns `401` if nobody is logged in.

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/notes?page=1&per_page=10` | Paginated list of **your** notes, newest first. `per_page` defaults to 10, max 50. | `200` | `400` invalid page params |
| POST | `/notes` | Create a note. Body: `title` (1–100 chars), `content`. | `201` note | `422` validation errors |
| GET | `/notes/<id>` | Get one of your notes. | `200` note | `403` not yours, `404` not found |
| PATCH | `/notes/<id>` | Update `title` and/or `content` of your note. | `200` note | `403`, `404`, `422` |
| DELETE | `/notes/<id>` | Delete your note. | `204` | `403`, `404` |

A note looks like:

```json
{
  "id": 1,
  "title": "Grocery list",
  "content": "Milk, eggs, bread",
  "created_at": "2026-10-22T12:48:45",
  "updated_at": "2026-10-22T12:48:45",
  "user_id": 1
}
```

The paginated index response:

```json
{
  "notes": [ ... ],
  "page": 1,
  "per_page": 10,
  "total": 25,
  "pages": 3,
  "has_next": true,
  "has_prev": false
}
```

## Security Notes

- Passwords are stored only as bcrypt hashes. The `password_hash` property is write-only.
- Usernames are unique, enforced by a database constraint.
- Note ownership is always taken from the session, never from the request body.
- Users get `403 Forbidden` when trying to read, edit or delete another user's note.