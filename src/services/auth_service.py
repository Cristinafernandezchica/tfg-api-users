from src.models.user import User
from src.database import db
from src.utils.password_hash import hash_password, verify_password
from src.utils.jwt_manager import create_token

# Registrar un nuevo usuario
from src.utils.jwt_manager import create_token

def register_user(email, password, name, username):
    if User.query.filter_by(email=email).first():
        return None, "Email ya registrado"
    
    if User.query.filter_by(username=username).first():
        return None, "Nombre de usuario ya registrado"

    user = User(
        email=email,
        password=hash_password(password),
        name=name,
        username=username
    )
    db.session.add(user)
    db.session.commit()

    token = create_token(user.id, user.role)

    return token, None


# Iniciar sesión
def login_user(identifier, password):
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()

    if not user or not verify_password(password, user.password):
        return None, "Usuario o clave incorrectos"

    token = create_token(user.id, user.role)
    return token, None


# Actualizar información del usuario
def update_user(user_id, name=None, email=None, password=None):
    user = User.query.get(user_id)
    if not user:
        return None, "Usuario no encontrado"

    if name:
        user.name = name
    
    if email:
        existing = User.query.filter(User.email == email).first()
        if existing and existing.id != user_id:
            return None, "Email ya registrado"
        user.email = email

    if password:
        user.password = hash_password(password)

    db.session.commit()
    return user, None

# Borrar usuario
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "Usuario no encontrado"

    db.session.delete(user)
    db.session.commit()
    return True, None
