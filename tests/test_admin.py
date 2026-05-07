import pytest
from src.models.user import User
from src.utils.password_hash import hash_password

class TestAdminEndpoints:
    """Tests para endpoints administrativos"""
    
    def test_admin_delete_user(self, client, admin_headers, test_user, db):
        """Test administrador elimina usuario"""
        user_id = test_user.id
        response = client.delete(f'/auth/admin/delete/{user_id}', headers=admin_headers)
        
        assert response.status_code == 200
        assert response.json['message'] == 'User deleted'
        
        # Verificar que el usuario fue eliminado
        deleted_user = User.query.get(user_id)
        assert deleted_user is None
    
    def test_admin_delete_nonexistent_user(self, client, admin_headers):
        """Test administrador intenta eliminar usuario inexistente"""
        response = client.delete('/auth/admin/delete/99999', headers=admin_headers)
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_admin_reset_password(self, client, admin_headers, test_user):
        """Test administrador resetea contraseña"""
        response = client.put(f'/auth/admin/reset-password/{test_user.id}', 
                             headers=admin_headers,
                             json={'password': 'newadminpass'})
        
        assert response.status_code == 200
        assert response.json['message'] == 'Password reset successfully'
        
        # Verificar que puede iniciar sesión con nueva contraseña
        login_response = client.post('/auth/login', json={
            'identifier': test_user.username,
            'password': 'newadminpass'
        })
        assert login_response.status_code == 200
    
    def test_admin_reset_password_missing_password(self, client, admin_headers, test_user):
        """Test reset password sin proporcionar contraseña"""
        response = client.put(f'/auth/admin/reset-password/{test_user.id}', 
                             headers=admin_headers,
                             json={})
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_admin_change_role_to_admin(self, client, admin_headers, test_user, db):
        """Test cambiar rol de usuario a admin"""
        response = client.put(f'/auth/admin/change-role/{test_user.id}',
                             headers=admin_headers,
                             json={'role': 'admin'})
        
        assert response.status_code == 200
        assert 'Role updated' in response.json['message']
        
        # Verificar cambio en BD
        db.session.refresh(test_user)
        assert test_user.role == 'admin'
    
    def test_admin_change_role_to_user(self, client, admin_headers, admin_user, db):
        """Test cambiar rol de admin a user"""
        response = client.put(f'/auth/admin/change-role/{admin_user.id}',
                             headers=admin_headers,
                             json={'role': 'user'})
        
        assert response.status_code == 200
        
        db.session.refresh(admin_user)
        assert admin_user.role == 'user'
    
    def test_admin_change_role_invalid(self, client, admin_headers, test_user):
        """Test cambiar rol a valor inválido"""
        response = client.put(f'/auth/admin/change-role/{test_user.id}',
                             headers=admin_headers,
                             json={'role': 'superadmin'})
        
        assert response.status_code == 400
        assert 'Invalid role' in response.json['error']
    
    def test_list_users_empty_search(self, client, admin_headers, test_user, admin_user):
        """Test listar todos los usuarios"""
        response = client.get('/auth/users', headers=admin_headers)
        
        assert response.status_code == 200
        assert len(response.json) >= 2
        # Verificar estructura
        assert 'id' in response.json[0]
        assert 'name' in response.json[0]
        assert 'email' in response.json[0]
        assert 'username' in response.json[0]
        assert 'role' in response.json[0]
    
    def test_list_users_with_search(self, client, admin_headers, test_user, admin_user):
        """Test listar usuarios con búsqueda"""
        response = client.get('/auth/users?q=test', headers=admin_headers)
        
        assert response.status_code == 200
        assert len(response.json) >= 1
        assert any('test' in user['email'].lower() for user in response.json)
    
    def test_unauthorized_user_cannot_access_admin(self, client, auth_headers, test_user):
        """Test usuario normal no puede acceder a endpoints admin"""
        response = client.delete(f'/auth/admin/delete/{test_user.id}', headers=auth_headers)
        
        assert response.status_code == 403
        assert 'Forbidden' in response.json['error']
    
    def test_list_users_requires_admin(self, client, auth_headers):
        """Test listar usuarios requiere admin"""
        response = client.get('/auth/users', headers=auth_headers)
        
        assert response.status_code == 403