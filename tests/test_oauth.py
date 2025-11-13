"""
Tests for OAuth 2.0 authentication functionality
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.models import db, Endpoint, HealthCheck
from app.health_checker import HealthChecker
from app.oauth_utils import OAuth2Manager, AzureADHelper
import requests


class TestOAuth2Manager:
    """Test cases for OAuth2Manager"""
    
    def test_is_token_expired_no_token(self, app, db):
        """Test token expiration check when no token exists"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='client_credentials'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            assert OAuth2Manager.is_token_expired(endpoint) is True
    
    def test_is_token_expired_expired_token(self, app, db):
        """Test token expiration check with expired token"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='client_credentials',
                oauth_access_token='old_token',
                oauth_token_expires_at=datetime.utcnow() - timedelta(hours=1)
            )
            db.session.add(endpoint)
            db.session.commit()
            
            assert OAuth2Manager.is_token_expired(endpoint) is True
    
    def test_is_token_expired_valid_token(self, app, db):
        """Test token expiration check with valid token"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='client_credentials',
                oauth_access_token='valid_token',
                oauth_token_expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            db.session.add(endpoint)
            db.session.commit()
            
            assert OAuth2Manager.is_token_expired(endpoint) is False
    
    def test_is_token_expired_buffer(self, app, db):
        """Test token expiration with 5 minute buffer"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='client_credentials',
                oauth_access_token='token_near_expiry',
                # Token expires in 3 minutes (less than 5 minute buffer)
                oauth_token_expires_at=datetime.utcnow() + timedelta(minutes=3)
            )
            db.session.add(endpoint)
            db.session.commit()
            
            # Should be considered expired due to 5 minute buffer
            assert OAuth2Manager.is_token_expired(endpoint) is True
    
    @patch('app.oauth_utils.OAuth2Session')
    def test_get_client_credentials_token(self, mock_oauth_session, app, db):
        """Test getting token using client credentials flow"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='client_credentials',
                oauth_client_id='test_client_id',
                oauth_client_secret='test_client_secret',
                oauth_token_url='https://auth.example.com/token',
                oauth_scope='api.read api.write'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            # Mock OAuth2Session
            mock_client = MagicMock()
            mock_client.fetch_token.return_value = {
                'access_token': 'new_access_token',
                'token_type': 'Bearer',
                'expires_in': 3600
            }
            mock_oauth_session.return_value = mock_client
            
            token = OAuth2Manager.get_client_credentials_token(endpoint)
            
            assert token['access_token'] == 'new_access_token'
            assert token['token_type'] == 'Bearer'
            assert token['expires_in'] == 3600
            
            # Verify OAuth2Session was initialized correctly
            mock_oauth_session.assert_called_once_with(
                client_id='test_client_id',
                client_secret='test_client_secret',
                scope='api.read api.write'
            )
            
            # Verify fetch_token was called correctly
            mock_client.fetch_token.assert_called_once_with(
                url='https://auth.example.com/token',
                grant_type='client_credentials'
            )
    
    @patch('app.oauth_utils.OAuth2Session')
    def test_refresh_access_token(self, mock_oauth_session, app, db):
        """Test refreshing access token using refresh token"""
        with app.app_context():
            expires_at = datetime.utcnow() + timedelta(hours=1)
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='authorization_code',
                oauth_client_id='test_client_id',
                oauth_client_secret='test_client_secret',
                oauth_token_url='https://auth.example.com/token',
                oauth_access_token='old_token',
                oauth_refresh_token='refresh_token',
                oauth_token_expires_at=expires_at
            )
            db.session.add(endpoint)
            db.session.commit()
            
            # Mock OAuth2Session
            mock_client = MagicMock()
            mock_client.refresh_token.return_value = {
                'access_token': 'refreshed_access_token',
                'token_type': 'Bearer',
                'expires_in': 3600,
                'refresh_token': 'new_refresh_token'
            }
            mock_oauth_session.return_value = mock_client
            
            token = OAuth2Manager.refresh_access_token(endpoint)
            
            assert token['access_token'] == 'refreshed_access_token'
            assert token['refresh_token'] == 'new_refresh_token'
    
    def test_refresh_access_token_no_refresh_token(self, app, db):
        """Test refreshing access token without refresh token raises error"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='authorization_code',
                oauth_access_token='token'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            with pytest.raises(ValueError, match="No refresh token available"):
                OAuth2Manager.refresh_access_token(endpoint)
    
    def test_update_endpoint_token(self, app, db):
        """Test updating endpoint with new token information"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='client_credentials'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            token_response = {
                'access_token': 'new_token_value',
                'token_type': 'Bearer',
                'expires_in': 3600,
                'refresh_token': 'new_refresh_token'
            }
            
            before_time = datetime.utcnow()
            OAuth2Manager.update_endpoint_token(endpoint, token_response)
            after_time = datetime.utcnow() + timedelta(seconds=3600)
            
            assert endpoint.oauth_access_token == 'new_token_value'
            assert endpoint.oauth_refresh_token == 'new_refresh_token'
            assert endpoint.oauth_token_expires_at is not None
            assert before_time <= endpoint.oauth_token_expires_at <= after_time
    
    @patch('app.oauth_utils.OAuth2Session')
    def test_get_valid_token_client_credentials_expired(self, mock_oauth_session, app, db):
        """Test getting valid token with client credentials when token is expired"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='client_credentials',
                oauth_client_id='test_client_id',
                oauth_client_secret='test_client_secret',
                oauth_token_url='https://auth.example.com/token',
                oauth_scope='api.read'
            )
            db.session.add(endpoint)
            db.session.commit()
            
            # Mock OAuth2Session
            mock_client = MagicMock()
            mock_client.fetch_token.return_value = {
                'access_token': 'fresh_token',
                'token_type': 'Bearer',
                'expires_in': 3600
            }
            mock_oauth_session.return_value = mock_client
            
            token, needs_save = OAuth2Manager.get_valid_token(endpoint)
            
            assert token == 'fresh_token'
            assert needs_save is True
            assert endpoint.oauth_access_token == 'fresh_token'
    
    def test_get_valid_token_still_valid(self, app, db):
        """Test getting valid token when current token is still valid"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth API',
                url='https://api.example.com/data',
                auth_type='oauth',
                oauth_flow='client_credentials',
                oauth_access_token='still_valid_token',
                oauth_token_expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            db.session.add(endpoint)
            db.session.commit()
            
            token, needs_save = OAuth2Manager.get_valid_token(endpoint)
            
            assert token == 'still_valid_token'
            assert needs_save is False


class TestAzureADHelper:
    """Test cases for AzureADHelper"""
    
    def test_get_token_url(self):
        """Test getting Azure AD token endpoint URL"""
        tenant_id = '12345678-1234-1234-1234-123456789012'
        url = AzureADHelper.get_token_url(tenant_id)
        
        assert url == f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    
    def test_get_token_url_common(self):
        """Test getting Azure AD token endpoint URL for multi-tenant"""
        url = AzureADHelper.get_token_url('common')
        
        assert url == 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    
    def test_get_authorization_url(self):
        """Test getting Azure AD authorization endpoint URL"""
        tenant_id = '12345678-1234-1234-1234-123456789012'
        url = AzureADHelper.get_authorization_url(tenant_id)
        
        assert url == f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize'
    
    def test_get_default_scope_with_resource(self):
        """Test getting default Azure AD scope with resource URL"""
        resource_url = 'https://api.example.com'
        scope = AzureADHelper.get_default_scope(resource_url)
        
        assert scope == 'https://api.example.com/.default'
    
    def test_get_default_scope_without_resource(self):
        """Test getting default Azure AD scope without resource URL"""
        scope = AzureADHelper.get_default_scope()
        
        assert scope == 'https://graph.microsoft.com/.default'


class TestHealthCheckerOAuth:
    """Test OAuth integration with HealthChecker"""
    
    @patch('app.oauth_utils.OAuth2Session')
    @patch('requests.get')
    def test_check_endpoint_with_oauth_client_credentials(self, mock_get, mock_oauth_session, app, db):
        """Test health check with OAuth 2.0 client credentials flow"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth Protected API',
                url='https://api.example.com/health',
                auth_type='oauth',
                oauth_flow='client_credentials',
                oauth_client_id='test_client',
                oauth_client_secret='test_secret',
                oauth_token_url='https://auth.example.com/token',
                oauth_scope='api.read',
                timeout=10
            )
            db.session.add(endpoint)
            db.session.commit()
            
            # Mock OAuth2Session for token fetching
            mock_client = MagicMock()
            mock_client.fetch_token.return_value = {
                'access_token': 'test_access_token',
                'token_type': 'Bearer',
                'expires_in': 3600
            }
            mock_oauth_session.return_value = mock_client
            
            # Mock HTTP response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = 'OK'
            mock_get.return_value = mock_response
            
            health_check, needs_save = HealthChecker.check_endpoint(endpoint)
            
            # Verify health check succeeded
            assert health_check.status == 'success'
            assert health_check.status_code == 200
            
            # Verify endpoint was updated with token
            assert needs_save is True
            assert endpoint.oauth_access_token == 'test_access_token'
            assert endpoint.oauth_token_expires_at is not None
            
            # Verify request was made with Bearer token
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert 'headers' in call_kwargs
            assert call_kwargs['headers']['Authorization'] == 'Bearer test_access_token'
    
    @patch('requests.get')
    def test_check_endpoint_with_oauth_cached_token(self, mock_get, app, db):
        """Test health check with OAuth using cached valid token"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth Protected API',
                url='https://api.example.com/health',
                auth_type='oauth',
                oauth_flow='client_credentials',
                oauth_client_id='test_client',
                oauth_client_secret='test_secret',
                oauth_access_token='cached_valid_token',
                oauth_token_expires_at=datetime.utcnow() + timedelta(hours=1),
                timeout=10
            )
            db.session.add(endpoint)
            db.session.commit()
            
            # Mock HTTP response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = 'OK'
            mock_get.return_value = mock_response
            
            health_check, needs_save = HealthChecker.check_endpoint(endpoint)
            
            # Verify health check succeeded
            assert health_check.status == 'success'
            assert health_check.status_code == 200
            
            # Verify token was not refreshed (still valid)
            assert needs_save is False
            assert endpoint.oauth_access_token == 'cached_valid_token'
            
            # Verify request was made with cached Bearer token
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert 'headers' in call_kwargs
            assert call_kwargs['headers']['Authorization'] == 'Bearer cached_valid_token'
    
    def test_check_endpoint_with_oauth_invalid_config(self, app, db):
        """Test health check with invalid OAuth configuration"""
        with app.app_context():
            endpoint = Endpoint(
                name='OAuth Protected API',
                url='https://api.example.com/health',
                auth_type='oauth',
                oauth_flow='client_credentials',
                # Missing required OAuth fields
                timeout=10
            )
            db.session.add(endpoint)
            db.session.commit()
            
            health_check, needs_save = HealthChecker.check_endpoint(endpoint)
            
            # Should fail with error
            assert health_check.status == 'failure'
            assert 'OAuth authentication failed' in health_check.error_message
