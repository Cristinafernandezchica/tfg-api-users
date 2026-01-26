from src.models.user import User
from src.database import db
from src.utils.password_hash import hash_password

# Borrar un usuario
def admin_delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    db.session.delete(user)
    db.session.commit()
    return True, None

# Resetear la contraseña de un usuario
def admin_reset_password(user_id, new_password):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    user.password = hash_password(new_password)
    db.session.commit()
    return True, None

# Cambiar el rol de un usuario
def admin_change_role(user_id, new_role):
    if new_role not in ["user", "admin"]:
        return None, "Invalid role"

    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    user.role = new_role
    db.session.commit()
    return True, None
