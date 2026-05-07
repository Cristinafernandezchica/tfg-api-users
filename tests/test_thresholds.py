from src.models.user import User

class TestThresholds:
    """Tests para umbrales de ocupación"""
    
    def test_get_thresholds_success(self, client, auth_headers, test_user):
        """Test obtener umbrales del usuario"""
        # Configurar umbrales primero
        test_user.thresholds = {'room1': 5, 'room2': 10}
        db = test_user._sa_instance_state.session
        db.commit()
        
        response = client.get('/auth/me/thresholds', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json == {'room1': 5, 'room2': 10}
    
    def test_get_thresholds_empty(self, client, auth_headers, test_user):
        """Test obtener umbrales cuando no existen"""
        test_user.thresholds = {}
        db = test_user._sa_instance_state.session
        db.commit()
        
        response = client.get('/auth/me/thresholds', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json == {}
    
    def test_update_thresholds_success(self, client, auth_headers, test_user):
        """Test actualizar umbrales"""
        response = client.put('/auth/me/thresholds', headers=auth_headers, json={
            'thresholds': {'room1': 3, 'room2': 8, 'room3': 15}
        })
        
        assert response.status_code == 200
        assert response.json == {'room1': 3, 'room2': 8, 'room3': 15}
        
        # Verificar en BD
        updated_user = User.query.get(test_user.id)
        assert updated_user.thresholds == {'room1': 3, 'room2': 8, 'room3': 15}
    
    def test_update_thresholds_partial(self, client, auth_headers, test_user):
        """Test actualizar solo algunos umbrales"""
        # Umbrales iniciales
        test_user.thresholds = {'room1': 5, 'room2': 10}
        db = test_user._sa_instance_state.session
        db.commit()
        
        response = client.put('/auth/me/thresholds', headers=auth_headers, json={
            'thresholds': {'room1': 7}
        })
        
        assert response.status_code == 200
        assert response.json == {'room1': 7}
    
    def test_update_thresholds_invalid_type(self, client, auth_headers):
        """Test actualizar con formato inválido"""
        response = client.put('/auth/me/thresholds', headers=auth_headers, json={
            'thresholds': 'not a dict'
        })
        
        assert response.status_code == 400
        assert 'thresholds must be an object' in response.json['error']
    
    def test_update_thresholds_empty(self, client, auth_headers, test_user):
        """Test actualizar con umbrales vacíos"""
        response = client.put('/auth/me/thresholds', headers=auth_headers, json={
            'thresholds': {}
        })
        
        assert response.status_code == 200
        assert response.json == {}
    
    def test_internal_get_thresholds(self, client, test_user):
        """Test endpoint interno para obtener umbrales"""
        test_user.thresholds = {'room1': 4}
        db = test_user._sa_instance_state.session
        db.commit()
        
        response = client.get(f'/auth/internal/users/{test_user.id}/thresholds')
        
        assert response.status_code == 200
        assert response.json == {'room1': 4}
    
    def test_internal_get_thresholds_user_not_found(self, client):
        """Test endpoint interno con usuario inexistente"""
        response = client.get('/auth/internal/users/99999/thresholds')
        
        assert response.status_code == 404
        assert 'error' in response.json
    
    def test_internal_low_occupancy_alert(self, client, test_user):
        """Test endpoint interno de alerta de baja ocupación"""
        test_user.thresholds = {'room1': 5}
        db = test_user._sa_instance_state.session
        db.commit()
        
        response = client.post('/auth/internal/low_occupancy_alert', json={
            'user_id': test_user.id,
            'room_id': 'room1',
            'occupancy': 2
        })
        
        assert response.status_code == 200
        assert response.json['status'] == 'sent'
    
    def test_internal_alert_missing_fields(self, client):
        """Test alerta con campos faltantes"""
        response = client.post('/auth/internal/low_occupancy_alert', json={
            'user_id': 1
        })
        
        assert response.status_code == 400
        assert 'required' in response.json['error']
    
    def test_internal_alert_user_not_found(self, client):
        """Test alerta con usuario inexistente"""
        response = client.post('/auth/internal/low_occupancy_alert', json={
            'user_id': 99999,
            'room_id': 'room1',
            'occupancy': 2
        })
        
        assert response.status_code == 404