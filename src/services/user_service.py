from src.models.user import User
from src.database import db

# Actualizar los umbrales de baja ocupación de un usuario
def update_thresholds(user_id, thresholds: dict):
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    # Opcional: validar que thresholds es dict {room_id: int}
    user.thresholds = thresholds
    db.session.commit()
    return user.thresholds, None
