from config import api, app
from resources.auth_resources import CheckSession, Login, Logout, Signup

api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Logout, "/logout", endpoint="logout")


if __name__ == "__main__":
    app.run(port=5555, debug=True)