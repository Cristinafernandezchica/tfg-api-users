import pytest
from unittest.mock import patch, MagicMock

class TestAuthService:
    """Pruebas de auth_service.py con contexto de aplicación"""
    
    def test_register_user_success(self, app_context):
        """Given datos válidos, when se registra usuario, then crea usuario y retorna token"""
        from src.services.auth_service import register_user
        
        with patch('src.services.auth_service.User') as MockUser:
            MockUser.query.filter_by.return_value.first.side_effect = [None, None]
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.role = "user"
            MockUser.return_value = mock_user
            
            with patch('src.services.auth_service.db.session.add'):
                with patch('src.services.auth_service.db.session.commit'):
                    with patch('src.services.auth_service.create_token') as mock_token:
                        mock_token.return_value = "jwt_token"
                        
                        token, error = register_user(
                            email="new@example.com",
                            password="password123",
                            name="New User",
                            username="newuser"
                        )
                        
                        assert token == "jwt_token"
                        assert error is None

    def test_register_user_duplicate_email(self, app_context):
        """Given email ya registrado, when se registra, then retorna error"""
        from src.services.auth_service import register_user
        
        with patch('src.services.auth_service.User') as MockUser:
            MockUser.query.filter_by.return_value.first.return_value = MagicMock()
            
            token, error = register_user(
                email="existing@example.com",
                password="password123",
                name="New User",
                username="newuser"
            )
            
            assert token is None
            assert error == "Email ya registrado"

    def test_register_user_duplicate_username(self, app_context):
        """Given username ya registrado, when se registra, then retorna error"""
        from src.services.auth_service import register_user
        
        with patch('src.services.auth_service.User') as MockUser:
            mock_query_email = MagicMock()
            mock_query_email.first.return_value = None
            
            mock_query_username = MagicMock()
            mock_query_username.first.return_value = MagicMock()
            
            MockUser.query.filter_by.side_effect = [mock_query_email, mock_query_username]
            
            token, error = register_user(
                email="new@example.com",
                password="password123",
                name="New User",
                username="existinguser"
            )
            
            assert token is None
            assert error == "Nombre de usuario ya registrado"

    def test_login_user_success(self, app_context):
        """Given credenciales correctas, when se inicia sesión, then retorna token"""
        from src.services.auth_service import login_user
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.role = "user"
        mock_user.password = "hashed_password"
        
        with patch('src.services.auth_service.User') as MockUser:
            MockUser.query.filter.return_value.first.return_value = mock_user
            
            with patch('src.services.auth_service.verify_password') as mock_verify:
                mock_verify.return_value = True
                
                with patch('src.services.auth_service.create_token') as mock_token:
                    mock_token.return_value = "jwt_token"
                    
                    token, error = login_user("testuser", "password123")
                    
                    assert token == "jwt_token"
                    assert error is None

    def test_login_user_not_found(self, app_context):
        """Given usuario no existe, when se inicia sesión, then retorna error"""
        from src.services.auth_service import login_user
        
        with patch('src.services.auth_service.User') as MockUser:
            MockUser.query.filter.return_value.first.return_value = None
            
            token, error = login_user("nonexistent", "password123")
            
            assert token is None
            assert error == "Usuario o clave incorrectos"

    def test_login_user_wrong_password(self, app_context):
        """Given password incorrecto, when se inicia sesión, then retorna error"""
        from src.services.auth_service import login_user
        
        mock_user = MagicMock()
        mock_user.password = "hashed_password"
        
        with patch('src.services.auth_service.User') as MockUser:
            MockUser.query.filter.return_value.first.return_value = mock_user
            
            with patch('src.services.auth_service.verify_password') as mock_verify:
                mock_verify.return_value = False
                
                token, error = login_user("testuser", "wrongpassword")
                
                assert token is None
                assert error == "Usuario o clave incorrectos"

    def test_update_user_success(self, app):
        """Given datos válidos, when se actualiza usuario, then actualiza campos"""
        from src.services.auth_service import update_user
        
        with app.app_context():
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user.email = "old@example.com"
            mock_user.name = "Old Name"
            
            with patch('src.services.auth_service.User') as MockUser:
                MockUser.query.get.return_value = mock_user
                
                mock_filter = MagicMock()
                mock_filter.first.return_value = None
                MockUser.query.filter.return_value = mock_filter
                
                with patch('src.services.auth_service.db.session.commit'):
                    user, error = update_user(1, name="New Name", email="new@example.com")
                    
                    assert error is None
                    assert user is not None
                    assert user.name == "New Name"
                    assert user.email == "new@example.com"

    def test_update_user_password(self, app):
        """Given nueva contraseña, when se actualiza usuario, then hashea la contraseña"""
        from src.services.auth_service import update_user
        
        with app.app_context():
            mock_user = MagicMock()
            mock_user.id = 1
            
            with patch('src.services.auth_service.User') as MockUser:
                MockUser.query.get.return_value = mock_user
                
                with patch('src.services.auth_service.hash_password') as mock_hash:
                    mock_hash.return_value = "new_hashed_password"
                    with patch('src.services.auth_service.db.session.commit'):
                        user, error = update_user(1, password="newpassword123")
                        
                        assert error is None
                        assert user is not None
                        assert user.password == "new_hashed_password"

    def test_update_user_duplicate_email(self, app):
        """Given email ya usado por otro usuario, when se actualiza, then retorna error"""
        from src.services.auth_service import update_user
        
        with app.app_context():
            mock_user = MagicMock()
            mock_user.id = 1
            
            mock_existing_user = MagicMock()
            mock_existing_user.id = 2
            
            with patch('src.services.auth_service.User') as MockUser:
                MockUser.query.get.return_value = mock_user
                
                # Mock para filter cuando se busca por email
                mock_filter = MagicMock()
                mock_filter.first.return_value = mock_existing_user
                MockUser.query.filter.return_value = mock_filter
                
                user, error = update_user(1, email="existing@example.com")
                
                assert user is None
                assert error == "Email ya registrado"
    
    def test_update_user_not_found(self, app):
        """Given usuario no existe, when se actualiza, then retorna error"""
        from src.services.auth_service import update_user
        
        with app.app_context():
            with patch('src.services.auth_service.User') as MockUser:
                MockUser.query.get.return_value = None
                
                user, error = update_user(999, name="New Name")
                
                assert user is None
                assert error == "Usuario no encontrado"


    def test_delete_user_success(self, app):
        """Given usuario existe, when se elimina, then retorna éxito"""
        from src.services.auth_service import delete_user
        
        with app.app_context():
            mock_user = MagicMock()
            
            with patch('src.services.auth_service.User') as MockUser:
                MockUser.query.get.return_value = mock_user
                
                with patch('src.services.auth_service.db.session.delete') as mock_delete:
                    with patch('src.services.auth_service.db.session.commit'):
                        result, error = delete_user(1)
                        
                        assert result is True
                        assert error is None
                        mock_delete.assert_called_once_with(mock_user)

    def test_delete_user_not_found(self, app):
        """Given usuario no existe, when se elimina, then retorna error"""
        from src.services.auth_service import delete_user
        
        with app.app_context():
            with patch('src.services.auth_service.User') as MockUser:
                MockUser.query.get.return_value = None
                
                result, error = delete_user(999)
                
                assert result is None
                assert error == "Usuario no encontrado"


class TestAdminService:
    """Pruebas de admin_service.py con contexto de aplicación"""
    
    def test_admin_delete_user_success(self, app):
        """Given usuario existe, when admin elimina, then retorna éxito"""
        from src.services.admin_service import admin_delete_user
        
        with app.app_context():
            mock_user = MagicMock()
            
            with patch('src.services.admin_service.User') as MockUser:
                MockUser.query.get.return_value = mock_user
                
                with patch('src.services.admin_service.db.session.delete'):
                    with patch('src.services.admin_service.db.session.commit'):
                        result, error = admin_delete_user(1)
                        
                        assert result is True
                        assert error is None

    def test_admin_delete_user_not_found(self, app):
        """Given usuario no existe, when admin elimina, then retorna error"""
        from src.services.admin_service import admin_delete_user
        
        with app.app_context():
            with patch('src.services.admin_service.User') as MockUser:
                MockUser.query.get.return_value = None
                
                result, error = admin_delete_user(999)
                
                assert result is None
                assert error == "User not found"

    def test_admin_reset_password_success(self, app):
        """Given usuario existe, when admin resetea password, then actualiza contraseña"""
        from src.services.admin_service import admin_reset_password
        
        with app.app_context():
            mock_user = MagicMock()
            
            with patch('src.services.admin_service.User') as MockUser:
                MockUser.query.get.return_value = mock_user
                
                with patch('src.services.admin_service.hash_password') as mock_hash:
                    mock_hash.return_value = "new_hashed"
                    with patch('src.services.admin_service.db.session.commit'):
                        result, error = admin_reset_password(1, "newpassword")
                        
                        assert result is True
                        assert error is None
                        assert mock_user.password == "new_hashed"

    def test_admin_reset_password_user_not_found(self, app):
        """Given usuario no existe, when admin resetea password, then retorna error"""
        from src.services.admin_service import admin_reset_password
        
        with app.app_context():
            with patch('src.services.admin_service.User') as MockUser:
                MockUser.query.get.return_value = None
                
                result, error = admin_reset_password(999, "newpass")
                
                assert result is None
                assert error == "User not found"

    def test_admin_change_role_success(self, app):
        """Given usuario existe y rol válido, when admin cambia rol, then actualiza"""
        from src.services.admin_service import admin_change_role
        
        with app.app_context():
            mock_user = MagicMock()
            mock_user.role = "user"
            
            with patch('src.services.admin_service.User') as MockUser:
                MockUser.query.get.return_value = mock_user
                
                with patch('src.services.admin_service.db.session.commit'):
                    result, error = admin_change_role(1, "admin")
                    
                    assert result is True
                    assert error is None
                    assert mock_user.role == "admin"

    def test_admin_change_role_invalid(self, app):
        """Given rol inválido, when admin cambia rol, then retorna error"""
        from src.services.admin_service import admin_change_role
        
        result, error = admin_change_role(1, "superadmin")
        
        assert result is None
        assert error == "Invalid role"

    def test_admin_change_role_user_not_found(self, app):
        """Given usuario no existe, when admin cambia rol, then retorna error"""
        from src.services.admin_service import admin_change_role
        
        with app.app_context():
            with patch('src.services.admin_service.User') as MockUser:
                MockUser.query.get.return_value = None
                
                result, error = admin_change_role(999, "admin")
                
                assert result is None
                assert error == "User not found"


class TestUserService:
    """Pruebas de user_service.py con contexto de aplicación"""
    
    def test_update_thresholds_success(self, app):
        """Given usuario existe y thresholds válidos, when se actualizan, then guarda"""
        from src.services.user_service import update_thresholds
        
        with app.app_context():
            mock_user = MagicMock()
            mock_user.thresholds = {}
            
            with patch('src.services.user_service.User') as MockUser:
                MockUser.query.get.return_value = mock_user
                
                with patch('src.services.user_service.db.session.commit'):
                    thresholds, error = update_thresholds(1, {'room1': 5})
                    
                    assert error is None
                    assert mock_user.thresholds == {'room1': 5}
                    assert thresholds == {'room1': 5}

    def test_update_thresholds_user_not_found(self, app):
        """Given usuario no existe, when se actualizan umbrales, then retorna error"""
        from src.services.user_service import update_thresholds
        
        with app.app_context():
            with patch('src.services.user_service.User') as MockUser:
                MockUser.query.get.return_value = None
                
                thresholds, error = update_thresholds(999, {'room1': 5})
                
                assert thresholds is None
                assert error == "User not found"