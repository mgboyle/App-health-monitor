"""
Tests for web routes
"""
import pytest
from app.models import db, Endpoint, HealthCheck


class TestRoutes:
    """Test cases for web routes"""
    
    def test_index_route(self, client, app, db):
        """Test the index/dashboard route"""
        with app.app_context():
            response = client.get('/')
            assert response.status_code == 200
            assert b'Endpoint Dashboard' in response.data
    
    def test_add_endpoint_get(self, client):
        """Test GET request to add endpoint form"""
        response = client.get('/endpoints/add')
        assert response.status_code == 200
        assert b'Add New Endpoint' in response.data
    
    def test_add_endpoint_post(self, client, app, db):
        """Test POST request to add endpoint"""
        with app.app_context():
            response = client.post('/endpoints/add', data={
                'name': 'Test Endpoint',
                'url': 'https://api.example.com/test',
                'endpoint_type': 'REST',
                'check_interval': 60,
                'timeout': 30,
                'enabled': 'on'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify endpoint was created
            endpoint = Endpoint.query.filter_by(name='Test Endpoint').first()
            assert endpoint is not None
            assert endpoint.url == 'https://api.example.com/test'
            assert endpoint.enabled is True
    
    def test_edit_endpoint(self, client, app, db):
        """Test editing an endpoint"""
        with app.app_context():
            # Create an endpoint first
            endpoint = Endpoint(
                name='Original Name',
                url='https://api.example.com/original'
            )
            db.session.add(endpoint)
            db.session.commit()
            endpoint_id = endpoint.id
            
            # Test GET
            response = client.get(f'/endpoints/{endpoint_id}/edit')
            assert response.status_code == 200
            assert b'Edit Endpoint' in response.data
            
            # Test POST
            response = client.post(f'/endpoints/{endpoint_id}/edit', data={
                'name': 'Updated Name',
                'url': 'https://api.example.com/updated',
                'endpoint_type': 'REST',
                'check_interval': 120,
                'timeout': 45,
                'enabled': 'on'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify endpoint was updated
            db.session.refresh(endpoint)
            assert endpoint.name == 'Updated Name'
            assert endpoint.url == 'https://api.example.com/updated'
            assert endpoint.check_interval == 120
    
    def test_delete_endpoint(self, client, app, db):
        """Test deleting an endpoint"""
        with app.app_context():
            # Create an endpoint
            endpoint = Endpoint(
                name='To Delete',
                url='https://api.example.com/delete'
            )
            db.session.add(endpoint)
            db.session.commit()
            endpoint_id = endpoint.id
            
            # Delete it
            response = client.post(f'/endpoints/{endpoint_id}/delete', follow_redirects=True)
            assert response.status_code == 200
            
            # Verify it's gone
            endpoint = Endpoint.query.get(endpoint_id)
            assert endpoint is None
    
    def test_endpoint_logs(self, client, app, db):
        """Test viewing endpoint logs"""
        with app.app_context():
            # Create endpoint and health checks
            endpoint = Endpoint(
                name='Test Endpoint',
                url='https://api.example.com/test'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            health_check = HealthCheck(
                endpoint_id=endpoint.id,
                status='success',
                status_code=200,
                response_time=123.45
            )
            db.session.add(health_check)
            db.session.commit()
            
            response = client.get(f'/endpoints/{endpoint.id}/logs')
            assert response.status_code == 200
            assert b'Health Check Logs' in response.data
    
    def test_all_logs(self, client):
        """Test viewing all logs"""
        response = client.get('/logs')
        assert response.status_code == 200
        assert b'All Health Check Logs' in response.data
    
    def test_health_api(self, client, app, db):
        """Test the /api/health endpoint"""
        with app.app_context():
            # Create endpoint and health check
            endpoint = Endpoint(
                name='Test API',
                url='https://api.example.com/test',
                enabled=True
            )
            db.session.add(endpoint)
            db.session.commit()
            
            health_check = HealthCheck(
                endpoint_id=endpoint.id,
                status='success',
                status_code=200,
                response_time=100.0
            )
            db.session.add(health_check)
            db.session.commit()
            
            response = client.get('/api/health')
            assert response.status_code == 200
            
            data = response.get_json()
            assert 'status' in data
            assert 'endpoints' in data
            assert len(data['endpoints']) > 0
            assert data['endpoints'][0]['name'] == 'Test API'
    
    def test_api_endpoints(self, client, app, db):
        """Test the /api/endpoints endpoint"""
        with app.app_context():
            # Create an endpoint
            endpoint = Endpoint(
                name='Test API',
                url='https://api.example.com/test'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            response = client.get('/api/endpoints')
            assert response.status_code == 200
            
            data = response.get_json()
            assert 'endpoints' in data
            assert len(data['endpoints']) == 1
            assert data['endpoints'][0]['name'] == 'Test API'
    
    def test_api_endpoint_checks(self, client, app, db):
        """Test the /api/endpoints/<id>/checks endpoint"""
        with app.app_context():
            # Create endpoint and health checks
            endpoint = Endpoint(
                name='Test API',
                url='https://api.example.com/test'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            health_check = HealthCheck(
                endpoint_id=endpoint.id,
                status='success',
                status_code=200
            )
            db.session.add(health_check)
            db.session.commit()
            
            response = client.get(f'/api/endpoints/{endpoint.id}/checks')
            assert response.status_code == 200
            
            data = response.get_json()
            assert 'endpoint' in data
            assert 'checks' in data
            assert len(data['checks']) == 1
            assert data['checks'][0]['status'] == 'success'
