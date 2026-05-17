import pytest
from unittest.mock import patch, MagicMock

class TestJWTManager:
    """Pruebas de jwt_manager.py"""
    
    def test_create_token(self):
        """Given user_id y role, when se crea token, then retorna JWT válido"""
        from src.utils.jwt_manager import create_token
        
        with patch('src.utils.jwt_manager.jwt.encode') as mock_encode:
            mock_encode.return_value = "encoded_token"
            
            token = create_token(1, "user")
            
            assert token == "encoded_token"
            mock_encode.assert_called_once()
            call_args = mock_encode.call_args[0][0]
            assert call_args["user_id"] == 1
            assert call_args["role"] == "user"
            assert "exp" in call_args

    def test_decode_token_success(self):
        """Given token válido, when se decodifica, then retorna payload"""
        from src.utils.jwt_manager import decode_token
        
        with patch('src.utils.jwt_manager.jwt.decode') as mock_decode:
            mock_decode.return_value = {"user_id": 1, "role": "user", "exp": 1234567890}
            
            payload = decode_token("valid_token")
            
            assert payload["user_id"] == 1
            assert payload["role"] == "user"

    def test_decode_token_invalid(self):
        """Given token inválido, when se decodifica, then lanza excepción"""
        from src.utils.jwt_manager import decode_token
        
        with patch('src.utils.jwt_manager.jwt.decode') as mock_decode:
            mock_decode.side_effect = Exception("Invalid token")
            
            with pytest.raises(Exception):
                decode_token("invalid_token")


class TestPasswordHash:
    """Pruebas de password_hash.py"""
    
    def test_hash_password(self):
        """Given password, when se hashea, then retorna hash diferente"""
        from src.utils.password_hash import hash_password
        
        with patch('src.utils.password_hash.generate_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            result = hash_password("mypassword")
            
            assert result == "hashed_password"
            mock_hash.assert_called_once_with("mypassword")

    def test_verify_password_success(self):
        """Given password correcto, when se verifica, then retorna True"""
        from src.utils.password_hash import verify_password
        
        with patch('src.utils.password_hash.check_password_hash') as mock_check:
            mock_check.return_value = True
            
            result = verify_password("password", "hashed")
            
            assert result is True

    def test_verify_password_failure(self):
        """Given password incorrecto, when se verifica, then retorna False"""
        from src.utils.password_hash import verify_password
        
        with patch('src.utils.password_hash.check_password_hash') as mock_check:
            mock_check.return_value = False
            
            result = verify_password("wrong", "hashed")
            
            assert result is False


class TestAuthDecorators:
    """Pruebas de auth_decorators.py"""
    
    def test_require_role_admin_success(self):
        """Given token con rol admin, when se requiere admin, then ejecuta función"""
        from src.utils.auth_decorators import require_role
        from flask import Flask
        
        app = Flask(__name__)
        
        with app.test_request_context(headers={'Authorization': 'Bearer admin_token'}):
            with patch('src.utils.auth_decorators.decode_token') as mock_decode:
                mock_decode.return_value = {"user_id": 2, "role": "admin"}
                
                mock_function = MagicMock()
                mock_function.return_value = {"status": "ok"}
                
                decorator = require_role("admin")
                wrapped = decorator(mock_function)
                result = wrapped()
                
                assert result == {"status": "ok"}
                mock_function.assert_called_once()

    def test_require_role_unauthorized(self):
        """Given token con rol user, when se requiere admin, then retorna error 403"""
        from src.utils.auth_decorators import require_role
        from flask import Flask
        
        app = Flask(__name__)
        
        with app.test_request_context(headers={'Authorization': 'Bearer user_token'}):
            with patch('src.utils.auth_decorators.decode_token') as mock_decode:
                mock_decode.return_value = {"user_id": 1, "role": "user"}
                
                mock_function = MagicMock()
                
                decorator = require_role("admin")
                wrapped = decorator(mock_function)
                result = wrapped()
                
                assert result[1] == 403
                assert 'Forbidden' in result[0].json['error']
                mock_function.assert_not_called()

    def test_require_role_invalid_token(self):
        """Given token inválido, when se requiere admin, then retorna error 401"""
        from src.utils.auth_decorators import require_role
        from flask import Flask
        
        app = Flask(__name__)
        
        with app.test_request_context(headers={'Authorization': 'Bearer invalid'}):
            with patch('src.utils.auth_decorators.decode_token') as mock_decode:
                mock_decode.side_effect = Exception("Invalid token")
                
                mock_function = MagicMock()
                
                decorator = require_role("admin")
                wrapped = decorator(mock_function)
                result = wrapped()
                
                assert result[1] == 401
                assert 'Invalid token' in result[0].json['error']
                mock_function.assert_not_called()

    def test_require_role_no_token(self):
        """Given sin token, when se requiere admin, then retorna error 401"""
        from src.utils.auth_decorators import require_role
        from flask import Flask
        
        app = Flask(__name__)
        
        with app.test_request_context():
            with patch('src.utils.auth_decorators.decode_token') as mock_decode:
                mock_decode.side_effect = Exception("No token")
                
                mock_function = MagicMock()
                
                decorator = require_role("admin")
                wrapped = decorator(mock_function)
                result = wrapped()
                
                assert result[1] == 401
                assert 'Invalid token' in result[0].json['error']