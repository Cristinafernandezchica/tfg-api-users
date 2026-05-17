import pytest
from unittest.mock import patch, MagicMock

class TestAdminDeleteUser:
    """Pruebas del endpoint /auth/admin/delete/<user_id>"""
    
    def test_admin_delete_user_success(self, client, admin_headers, test_user):
        """Given admin token y usuario existente, when se elimina usuario, then retorna éxito"""
        response = client.delete(f'/auth/admin/delete/{test_user.id}', headers=admin_headers)
        
        assert response.status_code == 200
        assert response.json['message'] == 'User deleted'

    def test_admin_delete_user_not_found(self, client, admin_headers):
        """Given admin token pero usuario no existe, when se elimina, then retorna error 400"""
        response = client.delete('/auth/admin/delete/99999', headers=admin_headers)
        
        assert response.status_code == 400
        assert 'error' in response.json

    def test_admin_delete_user_unauthorized(self, client, auth_headers, test_user):
        """Given token de usuario normal, when se intenta eliminar usuario, then retorna error 403"""
        response = client.delete(f'/auth/admin/delete/{test_user.id}', headers=auth_headers)
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json['error']

    def test_admin_delete_user_invalid_token(self, client):
        """Given token inválido, when se intenta eliminar usuario, then retorna error 401"""
        response = client.delete('/auth/admin/delete/1', headers={'Authorization': 'Bearer invalid_token'})
        
        assert response.status_code == 401
        assert 'error' in response.json


class TestAdminResetPassword:
    """Pruebas del endpoint /auth/admin/reset-password/<user_id>"""
    
    def test_admin_reset_password_success(self, client, admin_headers, test_user):
        """Given admin token y nueva contraseña, when se resetea password, then retorna éxito"""
        response = client.put(f'/auth/admin/reset-password/{test_user.id}',
                             headers=admin_headers,
                             json={'password': 'newpassword123'})
        
        assert response.status_code == 200
        assert response.json['message'] == 'Password reset successfully'

    def test_admin_reset_password_missing_password(self, client, admin_headers, test_user):
        """Given admin token sin contraseña, when se resetea password, then retorna error 400"""
        response = client.put(f'/auth/admin/reset-password/{test_user.id}',
                             headers=admin_headers,
                             json={})
        
        assert response.status_code == 400
        assert 'error' in response.json

    def test_admin_reset_password_user_not_found(self, client, admin_headers):
        """Given admin token pero usuario no existe, when se resetea, then retorna error 400"""
        response = client.put('/auth/admin/reset-password/99999',
                             headers=admin_headers,
                             json={'password': 'newpass'})
        
        assert response.status_code == 400
        assert 'error' in response.json


class TestAdminChangeRole:
    """Pruebas del endpoint /auth/admin/change-role/<user_id>"""
    
    def test_admin_change_role_to_admin(self, client, admin_headers, test_user):
        """Given admin token, when se cambia rol a admin, then retorna éxito"""
        response = client.put(f'/auth/admin/change-role/{test_user.id}',
                             headers=admin_headers,
                             json={'role': 'admin'})
        
        assert response.status_code == 200
        assert 'Role updated' in response.json['message']

    def test_admin_change_role_to_user(self, client, admin_headers, admin_user):
        """Given admin token, when se cambia rol a user, then retorna éxito"""
        response = client.put(f'/auth/admin/change-role/{admin_user.id}',
                             headers=admin_headers,
                             json={'role': 'user'})
        
        assert response.status_code == 200

    def test_admin_change_role_invalid_role(self, client, admin_headers, test_user):
        """Given rol inválido, when se cambia rol, then retorna error 400"""
        response = client.put(f'/auth/admin/change-role/{test_user.id}',
                             headers=admin_headers,
                             json={'role': 'superadmin'})
        
        assert response.status_code == 400
        assert 'Invalid role' in response.json['error']

    def test_admin_change_role_unauthorized(self, client, auth_headers, test_user):
        """Given token de usuario normal, when se intenta cambiar rol, then retorna error 403"""
        response = client.put(f'/auth/admin/change-role/{test_user.id}',
                             headers=auth_headers,
                             json={'role': 'admin'})
        
        assert response.status_code == 403


class TestListUsers:
    """Pruebas del endpoint /auth/users"""
    
    def test_list_users_success(self, client, admin_headers, test_user, admin_user):
        """Given admin token, when se listan usuarios, then retorna lista completa"""
        response = client.get('/auth/users', headers=admin_headers)
        
        assert response.status_code == 200
        assert len(response.json) >= 2
        assert 'id' in response.json[0]
        assert 'email' in response.json[0]

    def test_list_users_with_search(self, client, admin_headers, test_user):
        """Given admin token y query de búsqueda, when se listan usuarios, then filtra resultados"""
        response = client.get('/auth/users?q=test', headers=admin_headers)
        
        assert response.status_code == 200
        # Debe incluir al menos el usuario test
        assert len(response.json) >= 1

    def test_list_users_unauthorized(self, client, auth_headers):
        """Given token de usuario normal, when se intenta listar usuarios, then retorna error 403"""
        response = client.get('/auth/users', headers=auth_headers)
        
        assert response.status_code == 403