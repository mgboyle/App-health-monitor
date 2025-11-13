"""
OAuth 2.0 authentication utilities for health monitoring
"""
from datetime import datetime, timedelta
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token


class OAuth2Manager:
    """Manage OAuth 2.0 authentication flows"""
    
    @staticmethod
    def is_token_expired(endpoint):
        """
        Check if the access token is expired
        
        Args:
            endpoint: Endpoint model instance
            
        Returns:
            bool: True if token is expired or missing
        """
        if not endpoint.oauth_access_token or not endpoint.oauth_token_expires_at:
            return True
        
        # Add 5 minute buffer before actual expiration
        buffer = timedelta(minutes=5)
        return datetime.utcnow() >= (endpoint.oauth_token_expires_at - buffer)
    
    @staticmethod
    def get_client_credentials_token(endpoint):
        """
        Get access token using OAuth 2.0 client credentials flow
        
        Args:
            endpoint: Endpoint model instance
            
        Returns:
            dict: Token response with access_token, token_type, expires_in, etc.
        """
        client = OAuth2Session(
            client_id=endpoint.oauth_client_id,
            client_secret=endpoint.oauth_client_secret,
            scope=endpoint.oauth_scope
        )
        
        token = client.fetch_token(
            url=endpoint.oauth_token_url,
            grant_type='client_credentials'
        )
        
        return token
    
    @staticmethod
    def refresh_access_token(endpoint):
        """
        Refresh access token using refresh token (for authorization code flow)
        
        Args:
            endpoint: Endpoint model instance
            
        Returns:
            dict: Token response with access_token, token_type, expires_in, etc.
        """
        if not endpoint.oauth_refresh_token:
            raise ValueError("No refresh token available")
        
        client = OAuth2Session(
            client_id=endpoint.oauth_client_id,
            client_secret=endpoint.oauth_client_secret,
            token={
                'access_token': endpoint.oauth_access_token or '',
                'refresh_token': endpoint.oauth_refresh_token,
                'token_type': 'Bearer',
                'expires_at': endpoint.oauth_token_expires_at.timestamp() if endpoint.oauth_token_expires_at else 0
            }
        )
        
        token = client.refresh_token(
            url=endpoint.oauth_token_url
        )
        
        return token
    
    @staticmethod
    def update_endpoint_token(endpoint, token_response):
        """
        Update endpoint with new token information
        
        Args:
            endpoint: Endpoint model instance
            token_response: Token response dict from OAuth provider
        """
        endpoint.oauth_access_token = token_response.get('access_token')
        
        # Handle refresh token (may not be present in all responses)
        if 'refresh_token' in token_response:
            endpoint.oauth_refresh_token = token_response.get('refresh_token')
        
        # Calculate token expiration
        expires_in = token_response.get('expires_in', 3600)  # Default to 1 hour
        endpoint.oauth_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    @staticmethod
    def get_valid_token(endpoint):
        """
        Get a valid access token, refreshing if necessary
        
        Args:
            endpoint: Endpoint model instance
            
        Returns:
            tuple: (access_token, needs_save) where needs_save indicates if endpoint needs to be saved
        """
        needs_save = False
        
        # Check if token needs refresh
        if OAuth2Manager.is_token_expired(endpoint):
            if endpoint.oauth_flow == 'client_credentials':
                # Get new token using client credentials
                token = OAuth2Manager.get_client_credentials_token(endpoint)
                OAuth2Manager.update_endpoint_token(endpoint, token)
                needs_save = True
            elif endpoint.oauth_flow == 'authorization_code' and endpoint.oauth_refresh_token:
                # Refresh using refresh token
                try:
                    token = OAuth2Manager.refresh_access_token(endpoint)
                    OAuth2Manager.update_endpoint_token(endpoint, token)
                    needs_save = True
                except Exception:
                    # If refresh fails, re-raise to be handled by caller
                    raise
            else:
                raise ValueError("Cannot refresh token: no refresh token available for authorization_code flow")
        
        return endpoint.oauth_access_token, needs_save


class AzureADHelper:
    """Helper functions for Azure AD OAuth 2.0"""
    
    @staticmethod
    def get_token_url(tenant_id):
        """
        Get Azure AD token endpoint URL
        
        Args:
            tenant_id: Azure AD tenant ID or 'common' for multi-tenant
            
        Returns:
            str: Token endpoint URL
        """
        return f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    @staticmethod
    def get_authorization_url(tenant_id):
        """
        Get Azure AD authorization endpoint URL
        
        Args:
            tenant_id: Azure AD tenant ID or 'common' for multi-tenant
            
        Returns:
            str: Authorization endpoint URL
        """
        return f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    
    @staticmethod
    def get_default_scope(resource_url=None):
        """
        Get default Azure AD scope
        
        Args:
            resource_url: Optional resource URL (e.g., 'https://api.example.com')
            
        Returns:
            str: Default scope
        """
        if resource_url:
            return f"{resource_url}/.default"
        return "https://graph.microsoft.com/.default"
