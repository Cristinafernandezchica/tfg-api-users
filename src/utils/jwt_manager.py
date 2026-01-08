import jwt
from datetime import datetime, timedelta
from config import Config

def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
