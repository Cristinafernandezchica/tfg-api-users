from flask import Blueprint, request, jsonify
from src.services.auth_service import register_user, login_user, update_user, delete_user
from src.utils.jwt_manager import decode_token

auth_bp = Blueprint("auth", __name__)


def get_user_id_from_header():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = decode_token(token)
        return payload["user_id"], None
    except:
        return None, "Invalid token"


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    user, error = register_user(data["email"], data["password"], data["name"])
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "User created"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    token, error = login_user(data["email"], data["password"])
    if error:
        return jsonify({"error": error}), 401
    return jsonify({"token": token})


@auth_bp.route("/me", methods=["GET"])
def me():
    user_id, error = get_user_id_from_header()
    if error:
        return jsonify({"error": error}), 401
    return jsonify({"user_id": user_id})


@auth_bp.route("/update", methods=["PUT"])
def update():
    user_id, error = get_user_id_from_header()
    if error:
        return jsonify({"error": error}), 401

    data = request.json
    user, error = update_user(
        user_id,
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password")
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "User updated"})


@auth_bp.route("/delete", methods=["DELETE"])
def delete():
    user_id, error = get_user_id_from_header()
    if error:
        return jsonify({"error": error}), 401

    _, error = delete_user(user_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "User deleted"})
