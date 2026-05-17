import pytest
from unittest.mock import patch, MagicMock

class TestThresholdsEndpoints:
    """Pruebas de endpoints de umbrales"""
    
    def test_get_thresholds_success(self, client, auth_headers, test_user):
        """Given token válido, when se obtienen umbrales, then retorna thresholds"""
        test_user.thresholds = {'room1': 5, 'room2': 10}
        from src.database import db
        db.session.commit()
        
        response = client.get('/auth/me/thresholds', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json == {'room1': 5, 'room2': 10}

    def test_get_thresholds_empty(self, client, auth_headers, test_user):
        """Given token válido sin umbrales, when se obtienen, then retorna dict vacío"""
        test_user.thresholds = {}
        from src.database import db
        db.session.commit()
        
        response = client.get('/auth/me/thresholds', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json == {}

    def test_get_thresholds_user_not_found(self, client):
        """Given token de usuario que no existe, when se obtienen umbrales, then retorna error 404"""
        with patch('src.routes.auth_routes.decode_token') as mock_decode:
            mock_decode.return_value = {"user_id": 999, "role": "user"}
            with patch('src.routes.auth_routes.User.query.get') as mock_get:
                mock_get.return_value = None
                response = client.get('/auth/me/thresholds', headers={'Authorization': 'Bearer token'})
        
        assert response.status_code == 404
        assert 'error' in response.json

    def test_get_thresholds_no_token(self, client):
        """Given sin token, when se obtienen umbrales, then retorna error 401"""
        response = client.get('/auth/me/thresholds')
        
        assert response.status_code == 401
        assert 'error' in response.json

    def test_update_thresholds_success(self, client, auth_headers, test_user):
        """Given token válido y thresholds válidos, when se actualizan, then retorna éxito"""
        response = client.put('/auth/me/thresholds', headers=auth_headers, json={
            'thresholds': {'room1': 3, 'room2': 8}
        })
        
        assert response.status_code == 200
        assert response.json == {'room1': 3, 'room2': 8}

    def test_update_thresholds_invalid_type(self, client, auth_headers):
        """Given thresholds no es dict, when se actualizan, then retorna error 400"""
        response = client.put('/auth/me/thresholds', headers=auth_headers, json={
            'thresholds': 'not a dict'
        })
        
        assert response.status_code == 400
        assert 'thresholds must be an object' in response.json['error']

    def test_update_thresholds_empty_dict(self, client, auth_headers, test_user):
        """Given thresholds vacío, when se actualizan, then retorna dict vacío"""
        response = client.put('/auth/me/thresholds', headers=auth_headers, json={
            'thresholds': {}
        })
        
        assert response.status_code == 200
        assert response.json == {}

    def test_update_thresholds_user_not_found(self, client):
        """Given usuario no existe, when se actualizan umbrales, then retorna error 400"""
        with patch('src.routes.auth_routes.decode_token') as mock_decode:
            mock_decode.return_value = {"user_id": 999, "role": "user"}
            with patch('src.routes.auth_routes.update_thresholds') as mock_update:
                mock_update.return_value = (None, "User not found")
                response = client.put('/auth/me/thresholds', headers={'Authorization': 'Bearer token'}, json={'thresholds': {}})
        
        assert response.status_code == 400
        assert 'error' in response.json

    def test_internal_get_thresholds_success(self, client, test_user):
        """Given user_id válido, when se obtienen umbrales internamente, then retorna thresholds"""
        test_user.thresholds = {'room1': 4}
        from src.database import db
        db.session.commit()
        
        response = client.get(f'/auth/internal/users/{test_user.id}/thresholds')
        
        assert response.status_code == 200
        assert response.json == {'room1': 4}

    def test_internal_get_thresholds_user_not_found(self, client):
        """Given user_id no existe, when se obtienen umbrales, then retorna error 404"""
        response = client.get('/auth/internal/users/99999/thresholds')
        
        assert response.status_code == 404
        assert 'error' in response.json

    def test_internal_low_occupancy_alert_success(self, client, test_user):
        """Given datos válidos, when se envía alerta, then retorna éxito"""
        test_user.thresholds = {'room1': 5}
        from src.database import db
        db.session.commit()
        
        response = client.post('/auth/internal/low_occupancy_alert', json={
            'user_id': test_user.id,
            'room_id': 'room1',
            'occupancy': 2
        })
        
        assert response.status_code == 200
        assert response.json['status'] == 'sent'

    def test_internal_alert_missing_user_id(self, client):
        """Given falta user_id, when se envía alerta, then retorna error 400"""
        response = client.post('/auth/internal/low_occupancy_alert', json={
            'room_id': 'room1',
            'occupancy': 2
        })
        
        assert response.status_code == 400
        assert 'required' in response.json['error']

    def test_internal_alert_missing_room_id(self, client):
        """Given falta room_id, when se envía alerta, then retorna error 400"""
        response = client.post('/auth/internal/low_occupancy_alert', json={
            'user_id': 1,
            'occupancy': 2
        })
        
        assert response.status_code == 400
        assert 'required' in response.json['error']

    def test_internal_alert_missing_occupancy(self, client):
        """Given falta occupancy, when se envía alerta, then retorna error 400"""
        response = client.post('/auth/internal/low_occupancy_alert', json={
            'user_id': 1,
            'room_id': 'room1'
        })
        
        assert response.status_code == 400
        assert 'required' in response.json['error']

    def test_internal_alert_user_not_found(self, client):
        """Given usuario no existe, when se envía alerta, then retorna error 404"""
        response = client.post('/auth/internal/low_occupancy_alert', json={
            'user_id': 99999,
            'room_id': 'room1',
            'occupancy': 2
        })
        
        assert response.status_code == 404
        assert 'error' in response.json