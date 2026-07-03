from marshmallow import Schema, fields


class DocumentResponseSchema(Schema):
    id = fields.Int(dump_default=None)
    filename = fields.Str()
    chunks = fields.Int()
    uploaded_at = fields.Str()


class IngestResponseSchema(Schema):
    message = fields.Str()
    filename = fields.Str()
    chunks = fields.Int()
    document_id = fields.Int()
