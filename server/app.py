from config import app
import models  # noqa: F401  (registers models so migrations can see them)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
