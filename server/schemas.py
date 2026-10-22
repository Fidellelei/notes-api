"""Marshmallow schemas: serialize models to JSON and validate request bodies."""
from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate


def not_blank(value):
    if not value.strip():
        raise ValidationError("Cannot be blank.")


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)


class NoteSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # ignore fields like id/user_id sent by the client

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=[validate.Length(min=1, max=100), not_blank])
    content = fields.Str(required=True, validate=[validate.Length(min=1), not_blank])
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)


user_schema = UserSchema()
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)