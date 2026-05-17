import sys
import os
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from src.database import db as _db
from src.models.user import User
from src.utils.password_hash import hash_password
from src.routes.auth_routes import auth_bp


@pytest.fixture(scope='session')
def app():
    """Fixture que crea una aplicación DE TESTS completamente aislada"""
    app = Flask(__name__)
    
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET'] = 'test-secret-key'
    
    _db.init_app(app)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Cliente de pruebas"""
    return app.test_client()


@pytest.fixture(scope='function')
def app_context(app):
    """Contexto de aplicación para pruebas que lo necesitan"""
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app):
    """Base de datos para tests"""
    with app.app_context():
        _db.session.rollback()
        meta = _db.metadata
        for table in reversed(meta.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
        yield _db
        _db.session.rollback()


@pytest.fixture(scope='function')
def test_user(db):
    """Crear un usuario de prueba real en BD"""
    user = User(
        email='test@example.com',
        password=hash_password('password123'),
        name='Test User',
        username='testuser',
        role='user',
        thresholds={}
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user


@pytest.fixture(scope='function')
def admin_user(db):
    """Crear un usuario administrador de prueba real en BD"""
    admin = User(
        email='admin@example.com',
        password=hash_password('admin123'),
        name='Admin User',
        username='admin',
        role='admin',
        thresholds={}
    )
    db.session.add(admin)
    db.session.commit()
    db.session.refresh(admin)
    return admin


@pytest.fixture(scope='function')
def user_token(client, test_user):
    """Token de autenticación para usuario normal"""
    response = client.post('/auth/login', json={
        'identifier': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    return response.json['token']


@pytest.fixture(scope='function')
def admin_token(client, admin_user):
    """Token de autenticación para administrador"""
    response = client.post('/auth/login', json={
        'identifier': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 200
    return response.json['token']


@pytest.fixture(scope='function')
def auth_headers(user_token):
    """Headers con autenticación para usuario normal"""
    return {'Authorization': f'Bearer {user_token}'}


@pytest.fixture(scope='function')
def admin_headers(admin_token):
    """Headers con autenticación para administrador"""
    return {'Authorization': f'Bearer {admin_token}'}


# ==================== MOCKS PARA TESTS DE SERVICIOS ====================

@pytest.fixture
def mock_user():
    """Mock de un usuario normal"""
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    user.username = "testuser"
    user.name = "Test User"
    user.password = "hashed_password_123"
    user.role = "user"
    user.thresholds = {}
    return user


@pytest.fixture
def mock_admin():
    """Mock de un usuario administrador"""
    admin = MagicMock()
    admin.id = 2
    admin.email = "admin@example.com"
    admin.username = "admin"
    admin.name = "Admin User"
    admin.password = "hashed_admin_password"
    admin.role = "admin"
    admin.thresholds = {}
    return admin