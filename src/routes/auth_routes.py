from flask import Blueprint, request, jsonify
from src.models.user import User
from src.services.user_service import update_thresholds
from src.services.auth_service import register_user, login_user, update_user, delete_user
from src.utils.jwt_manager import decode_token
from src.services.admin_service import admin_change_role, admin_delete_user, admin_reset_password
from src.utils.auth_decorators import require_role


auth_bp = Blueprint("auth", __name__)


def get_user_id_from_header():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = decode_token(token)
        return payload["user_id"], None
    except:
        return None, "Invalid token"

# Registrar un usuario nuevo
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    token, error = register_user(data["email"], data["password"], data["name"], data["username"])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"token": token}), 201

# Iniciar sesión
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    token, error = login_user(data["identifier"], data["password"])
    if error:
        return jsonify({"error": error}), 401
    return jsonify({"token": token})

# Información del usuario actual
@auth_bp.route("/me", methods=["GET"])
def me():
    user_id, error = get_user_id_from_header()
    if error:
        return jsonify({"error": error}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "thresholds": user.thresholds
    }), 200


# Actualizar información del usuario (nombre, email, contraseña)
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

# Eliminar usuario
@auth_bp.route("/delete", methods=["DELETE"])
def delete():
    user_id, error = get_user_id_from_header()
    if error:
        return jsonify({"error": error}), 401

    _, error = delete_user(user_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "User deleted"})

# Eliminar usuario (admin)
@auth_bp.route("/admin/delete/<int:user_id>", methods=["DELETE"])
@require_role("admin")
def admin_delete_user_route(user_id):
    _, error = admin_delete_user(user_id)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "User deleted"})


# Resetear contraseña de un usuario (admin)
@auth_bp.route("/admin/reset-password/<int:user_id>", methods=["PUT"])
@require_role("admin")
def admin_reset_password_route(user_id):
    data = request.json
    new_password = data.get("password")

    if not new_password:
        return jsonify({"error": "Password required"}), 400

    _, error = admin_reset_password(user_id, new_password)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Password reset successfully"})


# Cambiar rol de un usuario (admin)
@auth_bp.route("/admin/change-role/<int:user_id>", methods=["PUT"])
@require_role("admin")
def admin_change_role_route(user_id):
    data = request.json
    new_role = data.get("role")

    _, error = admin_change_role(user_id, new_role)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": f"Role updated to '{new_role}'"})


# Obtener umbrales del usuario actual (para avisos de baja ocupación)
@auth_bp.route("/me/thresholds", methods=["GET"])
def get_my_thresholds():
    user_id, error = get_user_id_from_header()
    if error:
        return jsonify({"error": error}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.thresholds or {}), 200

# Actualizar umbrales de baja ocupación del usuario actual
@auth_bp.route("/me/thresholds", methods=["PUT"])
def set_my_thresholds():
    user_id, error = get_user_id_from_header()
    if error:
        return jsonify({"error": error}), 401

    data = request.get_json() or {}
    thresholds = data.get("thresholds")

    if not isinstance(thresholds, dict):
        return jsonify({"error": "thresholds must be an object"}), 400

    updated, error = update_thresholds(user_id, thresholds)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(updated), 200

# Endpoint interno para las alertas de baja ocupación
# Falta toda la lógica de envío de email
@auth_bp.route("/internal/low_occupancy_alert", methods=["POST"])
def internal_low_occupancy_alert():
    """
    Endpoint interno que la API de posicionamiento llama
    cuando detecta baja ocupación para un usuario.
    NO requiere autenticación de usuario final (podrías
    protegerlo con API key si quieres).
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    room_id = data.get("room_id")
    occupancy = data.get("occupancy")

    if not user_id or not room_id or occupancy is None:
        return jsonify({"error": "user_id, room_id and occupancy are required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    email = user.email

    # Aquí llamas a tu integración SMTP (Google) ya existente
    subject = f"Baja ocupación en {room_id}"
    body = (
        f"La estancia {room_id} ha bajado a {occupancy} personas.\n\n"
        f"Umbrales configurados: {user.thresholds or {}}"
    )
    # send_email(email, subject, body)  # TODO: FUNCIÓN PARA MANDAR LOS EMAILS

    return jsonify({"status": "sent"}), 200

# Endpoint interno para obtener umbrales de un usuario por su ID
@auth_bp.route("/internal/users/<int:user_id>/thresholds", methods=["GET"])
def internal_get_user_thresholds(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.thresholds or {}), 200

'''
@auth_bp.route("/users", methods=["GET"])
@require_role("admin")
def list_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "username": u.username,
            "role": u.role
        }
        for u in users
    ]), 200
'''


@auth_bp.route("/users", methods=["GET"])
@require_role("admin")
def list_users():
    query = request.args.get("q", "").lower()

    users = User.query.all()

    if query:
        users = [
            u for u in users
            if query in u.name.lower()
            or query in u.email.lower()
            or query in u.username.lower()
        ]

    return jsonify([
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "username": u.username,
            "role": u.role
        }
        for u in users
    ]), 200
