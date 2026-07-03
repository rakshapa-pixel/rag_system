from marshmallow import Schema, fields, validate


class SignupSchema(Schema):
    username = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=80, error="Username is required"),
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters"),
    )


class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1, error="Name is required"))
    password = fields.Str(required=True, validate=validate.Length(min=1, error="Password is required"))
