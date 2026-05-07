import pytest
from src.models.user import User
from src.database import db

class TestAuthEndpoints:
    """Tests para endpoints de autenticación"""
    
    def test_register_success(self, client, db):
        """Test registro exitoso de usuario"""
        response = client.post('/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'name': 'New User',
            'username': 'newuser'
        })
        
        assert response.status_code == 201
        assert 'token' in response.json
        
        # Verificar que el usuario fue creado en la BD
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.name == 'New User'
        assert user.username == 'newuser'
        assert user.role == 'user'
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registro con email ya existente"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Another User',
            'username': 'anotheruser'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json
        assert 'Email ya registrado' in response.json['error']
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registro con username ya existente"""
        response = client.post('/auth/register', json={
            'email': 'unique@example.com',
            'password': 'password123',
            'name': 'Another User',
            'username': 'testuser'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json
        assert 'Nombre de usuario ya registrado' in response.json['error']
    
    def test_register_missing_fields(self, client):
        """Test registro con campos faltantes - debería dar error 400"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': '123456'
        })
        
        assert response.status_code == 400
    
    def test_login_with_email(self, client, test_user):
        """Test login usando email"""
        response = client.post('/auth/login', json={
            'identifier': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert 'token' in response.json
    
    def test_login_with_username(self, client, test_user):
        """Test login usando username"""
        response = client.post('/auth/login', json={
            'identifier': 'testuser',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert 'token' in response.json
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login con credenciales inválidas"""
        response = client.post('/auth/login', json={
            'identifier': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert 'error' in response.json
        # Change this line:
        assert 'Usuario o clave incorrectos' in response.json['error']
    
    def test_login_nonexistent_user(self, client):
        """Test login con usuario inexistente"""
        response = client.post('/auth/login', json={
            'identifier': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        assert 'error' in response.json


class TestUserProfile:
    """Tests para perfil de usuario"""
    
    def test_get_me_success(self, client, auth_headers, test_user):
        """Test obtener información del usuario autenticado"""
        response = client.get('/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['id'] == test_user.id
        assert response.json['email'] == test_user.email
        assert response.json['name'] == test_user.name
        assert response.json['username'] == test_user.username
        assert response.json['role'] == test_user.role
    
    def test_get_me_unauthenticated(self, client):
        """Test obtener información sin token"""
        response = client.get('/auth/me')
        
        assert response.status_code == 401
        assert 'error' in response.json
    
    def test_get_me_invalid_token(self, client):
        """Test obtener información con token inválido"""
        response = client.get('/auth/me', headers={'Authorization': 'Bearer invalidtoken'})
        
        assert response.status_code == 401
    
    def test_update_user_success(self, client, auth_headers, test_user):
        """Test actualizar información del usuario"""
        response = client.put('/auth/update', headers=auth_headers, json={
            'name': 'Updated Name',
            'email': 'updated@example.com'
        })
        
        assert response.status_code == 200
        assert response.json['message'] == 'User updated'
        
        # Verificar cambios en BD
        updated_user = User.query.get(test_user.id)
        assert updated_user.name == 'Updated Name'
        assert updated_user.email == 'updated@example.com'
    
    def test_update_user_password(self, client, auth_headers, test_user):
        """Test actualizar contraseña"""
        response = client.put('/auth/update', headers=auth_headers, json={
            'password': 'newpassword123'
        })
        
        assert response.status_code == 200
        
        # Verificar que puede iniciar sesión con nueva contraseña
        login_response = client.post('/auth/login', json={
            'identifier': test_user.username,
            'password': 'newpassword123'
        })
        assert login_response.status_code == 200
    
    # tests/test_auth.py - Actualiza este test

    def test_update_user_duplicate_email(self, client, auth_headers, test_user, db):
        """Test actualizar a email ya existente"""
        from src.utils.password_hash import hash_password
        
        # Crear otro usuario
        other_user = User(
            email='other@example.com',
            password=hash_password('password'),
            name='Other User',
            username='otheruser'
        )
        db.session.add(other_user)
        db.session.commit()
        
        # Intentar actualizar test_user con el email de other_user
        response = client.put('/auth/update', headers=auth_headers, json={
            'email': 'other@example.com'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json
        assert 'Email ya registrado' in response.json['error']
    
    def test_delete_user_success(self, client, auth_headers, test_user, db):
        """Test eliminar usuario propio"""
        response = client.delete('/auth/delete', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['message'] == 'User deleted'
        
        # Verificar que fue eliminado
        deleted_user = User.query.get(test_user.id)
        assert deleted_user is None