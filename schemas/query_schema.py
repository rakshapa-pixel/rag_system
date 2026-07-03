from marshmallow import Schema, fields, validate


class QueryRequestSchema(Schema):
    question = fields.Str(
        required=True,
        validate=validate.Length(min=1, error="Question cannot be empty"),
    )


class QueryResponseSchema(Schema):
    answer = fields.Str()
    sources = fields.List(fields.Str())
    pages = fields.List(fields.Int())
