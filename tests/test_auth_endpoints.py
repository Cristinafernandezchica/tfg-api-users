import pytest
from unittest.mock import patch, MagicMock

from src.models.user import User

class TestRegisterEndpoint:
    """Pruebas del endpoint /auth/register"""
    
    def test_register_success(self, client, db):
        """Given datos de registro válidos, when se registra usuario, then retorna token 201"""
        response = client.post('/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'name': 'New User',
            'username': 'newuser'
        })
        
        assert response.status_code == 201
        assert 'token' in response.json

    def test_register_missing_fields(self, client):
        """Given datos incompletos, when se registra usuario, then retorna error 400"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': '123456'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json

    def test_register_duplicate_email(self, client, test_user):
        """Given email ya registrado, when se registra usuario, then retorna error 400"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Another User',
            'username': 'anotheruser'
        })
        
        assert response.status_code == 400
        assert 'Email ya registrado' in response.json['error']

    def test_register_duplicate_username(self, client, test_user):
        """Given username ya registrado, when se registra usuario, then retorna error 400"""
        response = client.post('/auth/register', json={
            'email': 'unique@example.com',
            'password': 'password123',
            'name': 'Another User',
            'username': 'testuser'
        })
        
        assert response.status_code == 400
        assert 'Nombre de usuario ya registrado' in response.json['error']

    def test_register_no_data(self, client):
        """Given sin datos, when se registra usuario, then retorna error 400"""
        response = client.post('/auth/register', json={})
        
        assert response.status_code == 400
        assert 'error' in response.json


class TestLoginEndpoint:
    """Pruebas del endpoint /auth/login"""
    
    def test_login_with_email_success(self, client, test_user):
        """Given email y password correctos, when se inicia sesión, then retorna token"""
        response = client.post('/auth/login', json={
            'identifier': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert 'token' in response.json

    def test_login_with_username_success(self, client, test_user):
        """Given username y password correctos, when se inicia sesión, then retorna token"""
        response = client.post('/auth/login', json={
            'identifier': 'testuser',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert 'token' in response.json

    def test_login_invalid_credentials(self, client, test_user):
        """Given credenciales incorrectas, when se inicia sesión, then retorna error 401"""
        response = client.post('/auth/login', json={
            'identifier': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert 'error' in response.json
        assert 'Usuario o clave incorrectos' in response.json['error']

    def test_login_missing_identifier(self, client):
        """Given sin identifier, when se inicia sesión, then retorna error 400"""
        response = client.post('/auth/login', json={'password': 'password123'})
        
        assert response.status_code == 400
        assert 'identifier and password are required' in response.json['error']

    def test_login_empty_data(self, client):
        """Given datos vacíos, when se inicia sesión, then retorna error 400"""
        response = client.post('/auth/login', json={})
        
        assert response.status_code == 400
        assert 'No data provided' in response.json['error']


class TestMeEndpoint:
    """Pruebas del endpoint /auth/me"""
    
    def test_get_me_success(self, client, auth_headers, test_user):
        """Given token válido, when se obtiene perfil, then retorna datos del usuario"""
        response = client.get('/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['id'] == test_user.id
        assert response.json['email'] == test_user.email

    def test_get_me_no_token(self, client):
        """Given sin token, when se obtiene perfil, then retorna error 401"""
        response = client.get('/auth/me')
        
        assert response.status_code == 401
        assert 'error' in response.json

    def test_get_me_invalid_token(self, client):
        """Given token inválido, when se obtiene perfil, then retorna error 401"""
        response = client.get('/auth/me', headers={'Authorization': 'Bearer invalid_token'})
        
        assert response.status_code == 401
        assert 'error' in response.json

    def test_get_me_user_not_found(self, client):
        """Given token de usuario que no existe, when se obtiene perfil, then retorna error 404"""
        with patch('src.routes.auth_routes.decode_token') as mock_decode:
            mock_decode.return_value = {"user_id": 999, "role": "user"}
            with patch('src.routes.auth_routes.User.query.get') as mock_get:
                mock_get.return_value = None
                response = client.get('/auth/me', headers={'Authorization': 'Bearer token'})
        
        assert response.status_code == 404
        assert 'error' in response.json


class TestUpdateEndpoint:
    """Pruebas del endpoint /auth/update"""
    
    def test_update_user_success(self, client, auth_headers, test_user):
        """Given token válido y datos válidos, when se actualiza usuario, then retorna éxito"""
        response = client.put('/auth/update', headers=auth_headers, json={
            'name': 'Updated Name',
            'email': 'updated@example.com'
        })
        
        assert response.status_code == 200
        assert response.json['message'] == 'User updated'

    def test_update_user_password_only(self, client, auth_headers, test_user):
        """Given solo contraseña nueva, when se actualiza usuario, then actualiza password"""
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

    def test_update_user_duplicate_email(self, client, auth_headers, test_user, db):
        """Given email ya existente, when se actualiza usuario, then retorna error 400"""
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
        
        response = client.put('/auth/update', headers=auth_headers, json={
            'email': 'other@example.com'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json

    def test_update_user_no_token(self, client):
        """Given sin token, when se actualiza usuario, then retorna error 401"""
        response = client.put('/auth/update', json={'name': 'New Name'})
        
        assert response.status_code == 401
        assert 'error' in response.json


class TestDeleteEndpoint:
    """Pruebas del endpoint /auth/delete"""
    
    def test_delete_user_success(self, client, auth_headers, test_user):
        """Given token válido, when se elimina usuario, then retorna éxito"""
        response = client.delete('/auth/delete', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['message'] == 'User deleted'

    def test_delete_user_not_found(self, client):
        """Given token de usuario que no existe, when se elimina, then retorna error 400"""
        with patch('src.routes.auth_routes.decode_token') as mock_decode:
            mock_decode.return_value = {"user_id": 999, "role": "user"}
            with patch('src.routes.auth_routes.delete_user') as mock_delete:
                mock_delete.return_value = (None, "Usuario no encontrado")
                response = client.delete('/auth/delete', headers={'Authorization': 'Bearer token'})
        
        assert response.status_code == 400
        assert 'error' in response.json

    def test_delete_user_no_token(self, client):
        """Given sin token, when se elimina usuario, then retorna error 401"""
        response = client.delete('/auth/delete')
        
        assert response.status_code == 401
        assert 'error' in response.json