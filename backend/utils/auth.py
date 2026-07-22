from functools import wraps

from flask import request, jsonify, current_app


def admin_required(fn):
    """Protects admin-only routes with a simple API key check.
    The dashboard must send: X-Admin-Key: <ADMIN_API_KEY>"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        provided_key = request.headers.get("X-Admin-Key")
        expected_key = current_app.config.get("ADMIN_API_KEY")
        if not provided_key or provided_key != expected_key:
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper
