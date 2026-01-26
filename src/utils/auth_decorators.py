from functools import wraps
from flask import request, jsonify
from src.utils.jwt_manager import decode_token

# Para comprobar el rol del usuario (admin o user)
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            try:
                payload = decode_token(token)
            except:
                return jsonify({"error": "Invalid token"}), 401

            if payload.get("role") != required_role:
                return jsonify({"error": "Forbidden"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
