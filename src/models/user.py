from src.database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    route = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    thresholds = db.Column(db.JSON, default=dict)