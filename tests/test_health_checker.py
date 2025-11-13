"""
Integration tests for health checker
"""
import pytest
from app.models import db, Endpoint, HealthCheck
from app.health_checker import HealthChecker
from unittest.mock import Mock, patch
import requests


class TestHealthChecker:
    """Test cases for HealthChecker"""
    
    def test_check_endpoint_success(self, app, db):
        """Test checking an endpoint that returns success"""
        with app.app_context():
            endpoint = Endpoint(
                name='Test API',
                url='https://httpbin.org/status/200',
                timeout=10
            )
            db.session.add(endpoint)
            db.session.commit()
            
            with patch('requests.get') as mock_get:
                # Mock a successful response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                health_check, needs_save = HealthChecker.check_endpoint(endpoint)
                
                assert health_check.status == 'success'
                assert health_check.status_code == 200
                assert health_check.response_time is not None
                assert health_check.response_time >= 0
                assert needs_save is False  # No OAuth token update
    
    def test_check_endpoint_failure(self, app, db):
        """Test checking an endpoint that returns failure"""
        with app.app_context():
            endpoint = Endpoint(
                name='Test API',
                url='https://httpbin.org/status/500',
                timeout=10
            )
            db.session.add(endpoint)
            db.session.commit()
            
            with patch('requests.get') as mock_get:
                # Mock a failed response
                mock_response = Mock()
                mock_response.status_code = 500
                mock_get.return_value = mock_response
                
                health_check, needs_save = HealthChecker.check_endpoint(endpoint)
                
                assert health_check.status == 'failure'
                assert health_check.status_code == 500
                assert 'HTTP 500' in health_check.error_message
    
    def test_check_endpoint_timeout(self, app, db):
        """Test checking an endpoint that times out"""
        with app.app_context():
            endpoint = Endpoint(
                name='Test API',
                url='https://httpbin.org/delay/10',
                timeout=1
            )
            db.session.add(endpoint)
            db.session.commit()
            
            with patch('requests.get') as mock_get:
                # Mock a timeout
                mock_get.side_effect = requests.exceptions.Timeout()
                
                health_check, needs_save = HealthChecker.check_endpoint(endpoint)
                
                assert health_check.status == 'timeout'
                assert 'timeout' in health_check.error_message.lower()
    
    def test_check_endpoint_connection_error(self, app, db):
        """Test checking an endpoint with connection error"""
        with app.app_context():
            endpoint = Endpoint(
                name='Test API',
                url='https://invalid-domain-that-does-not-exist.com',
                timeout=5
            )
            db.session.add(endpoint)
            db.session.commit()
            
            with patch('requests.get') as mock_get:
                # Mock a connection error
                mock_get.side_effect = requests.exceptions.ConnectionError('Connection failed')
                
                health_check, needs_save = HealthChecker.check_endpoint(endpoint)
                
                assert health_check.status == 'failure'
                assert health_check.error_message is not None
    
    def test_get_latest_status(self, app, db):
        """Test getting the latest health check status"""
        with app.app_context():
            endpoint = Endpoint(
                name='Test API',
                url='https://api.example.com/test'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            # Add multiple health checks
            check1 = HealthCheck(
                endpoint_id=endpoint.id,
                status='success',
                status_code=200
            )
            check2 = HealthCheck(
                endpoint_id=endpoint.id,
                status='failure',
                status_code=500
            )
            db.session.add_all([check1, check2])
            db.session.commit()
            
            # Get latest status
            latest = HealthChecker.get_latest_status(endpoint.id)
            
            assert latest is not None
            # The latest should be check2 since it was added last
            assert latest.id == check2.id
            assert latest.status == 'failure'
    
    def test_check_all_endpoints(self, app, db):
        """Test checking all enabled endpoints"""
        with app.app_context():
            # Create enabled and disabled endpoints
            endpoint1 = Endpoint(
                name='Enabled API',
                url='https://api.example.com/test1',
                enabled=True
            )
            endpoint2 = Endpoint(
                name='Disabled API',
                url='https://api.example.com/test2',
                enabled=False
            )
            db.session.add_all([endpoint1, endpoint2])
            db.session.commit()
            
            with patch('requests.get') as mock_get:
                # Mock successful responses
                mock_response = Mock()
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                HealthChecker.check_all_endpoints(app)
                
                # Only enabled endpoint should have a health check
                checks1 = HealthCheck.query.filter_by(endpoint_id=endpoint1.id).all()
                checks2 = HealthCheck.query.filter_by(endpoint_id=endpoint2.id).all()
                
                assert len(checks1) == 1
                assert len(checks2) == 0
