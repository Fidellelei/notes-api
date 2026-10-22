from sqlalchemy.orm import validates

from config import bcrypt, db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)

    notes = db.relationship("Note", back_populates="user", cascade="all, delete-orphan")

    @property
    def password_hash(self):
        """The hash is write-only so it can never leak through the model."""
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        """Accepts a plain-text password and stores only its bcrypt hash."""
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, username):
        username = (username or "").strip()
        if not 3 <= len(username) <= 30:
            raise ValueError("Username must be between 3 and 30 characters.")
        return username

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="notes")

    @validates("title", "content")
    def validate_not_blank(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"{key.capitalize()} cannot be blank.")
        if key == "title" and len(value) > 100:
            raise ValueError("Title must be 100 characters or fewer.")
        return value

    def __repr__(self):
        return f"<Note {self.id}: {self.title}>"