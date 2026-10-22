from app import app
from models import User


def signup(client, username="alice", password="password123"):
    return client.post("/signup", json={
        "username": username,
        "password": password,
        "password_confirmation": password,
    })


def create_note(client, title="My note", content="Some content"):
    return client.post("/notes", json={"title": title, "content": content})


class TestAuth:
    def test_signup_creates_user_and_logs_in(self, client):
        res = signup(client)
        assert res.status_code == 201
        body = res.get_json()
        assert body["username"] == "alice"
        assert "password_hash" not in body and "_password_hash" not in body
        assert client.get("/check_session").status_code == 200

    def test_password_is_stored_as_bcrypt_hash(self, client):
        signup(client)
        user = User.query.filter_by(username="alice").first()
        assert user._password_hash != "password123"
        assert user._password_hash.startswith("$2b$")

    def test_signup_rejects_duplicate_username(self, client):
        signup(client)
        res = signup(app.test_client())
        assert res.status_code == 422

    def test_signup_rejects_short_or_mismatched_password(self, client):
        assert signup(client, password="short").status_code == 422
        res = client.post("/signup", json={
            "username": "bob", "password": "password123", "password_confirmation": "different1",
        })
        assert res.status_code == 422

    def test_login_logout_and_check_session(self, client):
        signup(client)
        assert client.delete("/logout").status_code == 204
        assert client.get("/check_session").status_code == 401

        bad = client.post("/login", json={"username": "alice", "password": "wrongpass1"})
        assert bad.status_code == 401

        good = client.post("/login", json={"username": "alice", "password": "password123"})
        assert good.status_code == 200
        assert client.get("/check_session").get_json()["username"] == "alice"

    def test_logout_requires_login(self, client):
        assert client.delete("/logout").status_code == 401


class TestNotes:
    def test_all_note_routes_require_login(self, client):
        assert client.get("/notes").status_code == 401
        assert create_note(client).status_code == 401
        assert client.get("/notes/1").status_code == 401
        assert client.patch("/notes/1", json={"title": "x"}).status_code == 401
        assert client.delete("/notes/1").status_code == 401

    def test_crud(self, client):
        signup(client)

        created = create_note(client)
        assert created.status_code == 201
        note_id = created.get_json()["id"]

        assert client.get(f"/notes/{note_id}").status_code == 200

        updated = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
        assert updated.status_code == 200
        assert updated.get_json()["title"] == "Updated"
        assert updated.get_json()["content"] == "Some content"

        assert client.delete(f"/notes/{note_id}").status_code == 204
        assert client.get(f"/notes/{note_id}").status_code == 404

    def test_validation_errors(self, client):
        signup(client)
        assert create_note(client, title="", content="").status_code == 422
        assert create_note(client, title="x" * 101).status_code == 422
        note_id = create_note(client).get_json()["id"]
        assert client.patch(f"/notes/{note_id}", json={"title": "   "}).status_code == 422
        assert client.patch(f"/notes/{note_id}", json={}).status_code == 422

    def test_pagination(self, client):
        signup(client)
        for i in range(12):
            create_note(client, title=f"Note {i}")

        body = client.get("/notes?page=3&per_page=5").get_json()
        assert len(body["notes"]) == 2
        assert body["total"] == 12
        assert body["pages"] == 3
        assert body["has_next"] is False
        assert body["has_prev"] is True

        assert client.get("/notes?page=0").status_code == 400
        assert client.get("/notes?page=abc").status_code == 400

    def test_users_cannot_access_each_others_notes(self, client):
        signup(client, "alice")
        note_id = create_note(client).get_json()["id"]

        other = app.test_client()
        signup(other, "mallory")

        assert other.get("/notes").get_json()["total"] == 0
        assert other.get(f"/notes/{note_id}").status_code == 403
        assert other.patch(f"/notes/{note_id}", json={"title": "hacked"}).status_code == 403
        assert other.delete(f"/notes/{note_id}").status_code == 403

        # alice's note is untouched
        assert client.get(f"/notes/{note_id}").get_json()["title"] == "My note"
