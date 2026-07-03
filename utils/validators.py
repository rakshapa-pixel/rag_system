from flask import request, jsonify
from marshmallow import ValidationError


def parse_request(schema):
    """Validate request JSON against a marshmallow schema.

    Returns (data, None) on success, or (None, error_response) on failure.
    """
    try:
        data = schema.load(request.get_json() or {})
        return data, None
    except ValidationError as err:
        first_msg = next(iter(err.messages.values()))[0]
        return None, (jsonify({"error": first_msg}), 400)
