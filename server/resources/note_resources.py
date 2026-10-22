from flask import g, request
from flask_restful import Resource
from marshmallow import ValidationError

from auth import login_required
from config import db
from models import Note
from schemas import note_schema, notes_schema

DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 50


def _positive_int_arg(name, default):
    """Read a positive integer query param; returns (value, error_message)."""
    raw = request.args.get(name)
    if raw is None:
        return default, None
    try:
        value = int(raw)
    except ValueError:
        return None, f"'{name}' must be an integer."
    if value < 1:
        return None, f"'{name}' must be 1 or greater."
    return value, None


def _get_owned_note(note_id):
    """Fetch a note and confirm the current user owns it; returns (note, error_response)."""
    note = db.session.get(Note, note_id)
    if note is None:
        return None, ({"error": "Note not found."}, 404)
    if note.user_id != g.current_user.id:
        return None, ({"error": "Forbidden. You do not have access to this note."}, 403)
    return note, None


class NoteList(Resource):
    method_decorators = [login_required]

    def get(self):
        """List the current user's notes, newest first. Query params: page, per_page."""
        page, error = _positive_int_arg("page", 1)
        if error:
            return {"error": error}, 400
        per_page, error = _positive_int_arg("per_page", DEFAULT_PER_PAGE)
        if error:
            return {"error": error}, 400
        per_page = min(per_page, MAX_PER_PAGE)

        pagination = (
            Note.query.filter_by(user_id=g.current_user.id)
            .order_by(Note.created_at.desc(), Note.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            "notes": notes_schema.dump(pagination.items),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }, 200

    def post(self):
        try:
            data = note_schema.load(request.get_json(silent=True) or {})
        except ValidationError as e:
            return {"errors": e.messages}, 422

        note = Note(title=data["title"], content=data["content"], user_id=g.current_user.id)
        db.session.add(note)
        db.session.commit()
        return note_schema.dump(note), 201


class NoteDetail(Resource):
    method_decorators = [login_required]

    def get(self, id):
        note, error = _get_owned_note(id)
        if error:
            return error
        return note_schema.dump(note), 200

    def patch(self, id):
        note, error = _get_owned_note(id)
        if error:
            return error

        try:
            data = note_schema.load(request.get_json(silent=True) or {}, partial=True)
        except ValidationError as e:
            return {"errors": e.messages}, 422
        if not data:
            return {"errors": ["Provide a title and/or content to update."]}, 422

        for field, value in data.items():
            setattr(note, field, value)
        db.session.commit()
        return note_schema.dump(note), 200

    def delete(self, id):
        note, error = _get_owned_note(id)
        if error:
            return error
        db.session.delete(note)
        db.session.commit()
        return {}, 204