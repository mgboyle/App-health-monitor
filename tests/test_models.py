"""
Tests for database models
"""
import pytest
from app.models import db, Endpoint, HealthCheck
from datetime import datetime


class TestEndpointModel:
    """Test cases for Endpoint model"""
    
    def test_create_endpoint(self, app, db):
        """Test creating an endpoint"""
        with app.app_context():
            endpoint = Endpoint(
                name='Test API',
                url='https://api.example.com/health',
                endpoint_type='REST',
                check_interval=60,
                timeout=30,
                enabled=True
            )
            db.session.add(endpoint)
            db.session.commit()
            
            assert endpoint.id is not None
            assert endpoint.name == 'Test API'
            assert endpoint.url == 'https://api.example.com/health'
            assert endpoint.endpoint_type == 'REST'
            assert endpoint.check_interval == 60
            assert endpoint.timeout == 30
            assert endpoint.enabled is True
    
    def test_endpoint_to_dict(self, app, db):
        """Test endpoint to_dict method"""
        with app.app_context():
            endpoint = Endpoint(
                name='Test API',
                url='https://api.example.com/health',
                endpoint_type='REST'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            data = endpoint.to_dict()
            assert data['name'] == 'Test API'
            assert data['url'] == 'https://api.example.com/health'
            assert data['endpoint_type'] == 'REST'
            assert 'id' in data
            assert 'created_at' in data


class TestHealthCheckModel:
    """Test cases for HealthCheck model"""
    
    def test_create_health_check(self, app, db):
        """Test creating a health check"""
        with app.app_context():
            endpoint = Endpoint(
                name='Test API',
                url='https://api.example.com/health'
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
            
            assert health_check.id is not None
            assert health_check.endpoint_id == endpoint.id
            assert health_check.status == 'success'
            assert health_check.status_code == 200
            assert health_check.response_time == 123.45
    
    def test_health_check_relationship(self, app, db):
        """Test relationship between endpoint and health checks"""
        with app.app_context():
            endpoint = Endpoint(
                name='Test API',
                url='https://api.example.com/health'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            health_check1 = HealthCheck(
                endpoint_id=endpoint.id,
                status='success',
                status_code=200
            )
            health_check2 = HealthCheck(
                endpoint_id=endpoint.id,
                status='failure',
                status_code=500
            )
            db.session.add_all([health_check1, health_check2])
            db.session.commit()
            
            assert len(endpoint.health_checks) == 2
