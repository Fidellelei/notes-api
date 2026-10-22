from config import api, app
from resources.auth_resources import CheckSession, Login, Logout, Signup
from resources.note_resources import NoteDetail, NoteList

api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Logout, "/logout", endpoint="logout")

api.add_resource(NoteList, "/notes", endpoint="notes")
api.add_resource(NoteDetail, "/notes/<int:id>", endpoint="note")


if __name__ == "__main__":
    app.run(port=5555, debug=True)