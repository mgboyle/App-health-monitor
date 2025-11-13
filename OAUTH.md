# OAuth 2.0 Authentication Guide

This guide explains how to configure OAuth 2.0 authentication for monitoring protected API endpoints.

## Overview

The App Health Monitor supports OAuth 2.0 authentication for monitoring endpoints that require OAuth tokens. Two OAuth flows are supported:

1. **Client Credentials Flow** - For service-to-service authentication (most common for API monitoring)
2. **Authorization Code Flow** - For user-delegated access (requires manual setup)

## Supported OAuth 2.0 Flows

### Client Credentials Flow (Recommended)

The client credentials flow is ideal for monitoring APIs where your monitoring application acts as a client directly authenticating with the OAuth provider.

**Use Cases:**
- Monitoring internal APIs protected by OAuth
- Service-to-service authentication
- APIs that don't require user context

**Configuration:**
- OAuth Flow: `client_credentials`
- Client ID: Your application's client ID
- Client Secret: Your application's client secret
- Token URL: OAuth token endpoint
- Scope: Required OAuth scopes (space-separated)

**How it works:**
1. The health monitor requests an access token using client credentials
2. The token is cached and reused for subsequent health checks
3. When the token expires, a new token is automatically requested
4. The token is included as a Bearer token in the Authorization header

### Authorization Code Flow

The authorization code flow is used when monitoring APIs that require user-delegated access.

**Use Cases:**
- APIs requiring user consent
- APIs that need specific user permissions

**Configuration:**
- OAuth Flow: `authorization_code`
- Client ID: Your application's client ID
- Client Secret: Your application's client secret
- Token URL: OAuth token endpoint
- Authorization URL: OAuth authorization endpoint
- Scope: Required OAuth scopes (space-separated)
- Refresh Token: Must be obtained manually and configured

**Note:** The authorization code flow requires you to manually obtain an initial access token and refresh token through the OAuth authorization process. The health monitor will then use the refresh token to obtain new access tokens as needed.

## Azure AD Configuration

The health monitor includes helper utilities for Azure AD OAuth 2.0 configuration.

### Azure AD Client Credentials

For Azure AD service principal authentication:

1. **Register an Application** in Azure AD:
   - Go to Azure Portal → Azure Active Directory → App registrations
   - Click "New registration"
   - Note the Application (client) ID and Directory (tenant) ID

2. **Create a Client Secret**:
   - In your app registration, go to Certificates & secrets
   - Create a new client secret
   - Note the secret value (it won't be shown again)

3. **Configure API Permissions**:
   - Add the required API permissions for the API you're monitoring
   - Grant admin consent if required

4. **Configure the Endpoint**:
   ```
   Auth Type: oauth
   OAuth Flow: client_credentials
   Client ID: <your-application-client-id>
   Client Secret: <your-client-secret>
   Token URL: https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token
   Scope: <resource-url>/.default
   ```

**Example Scopes:**
- `https://graph.microsoft.com/.default` - For Microsoft Graph API
- `https://management.azure.com/.default` - For Azure Resource Manager
- `api://<app-id>/.default` - For custom APIs

### Finding Azure AD URLs

**Token URL:**
```
https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token
```

**Authorization URL:**
```
https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize
```

Replace `{tenant-id}` with:
- Your Azure AD tenant ID (GUID)
- `common` for multi-tenant applications
- `organizations` for any organizational account
- `consumers` for Microsoft personal accounts

## Configuration Examples

### Example 1: Azure AD Protected API

```
Name: Production API
URL: https://api.example.com/health
Auth Type: oauth
OAuth Flow: client_credentials
Client ID: 12345678-1234-1234-1234-123456789012
Client Secret: your-secret-here
Token URL: https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/token
Scope: api://your-api-id/.default
```

### Example 2: Generic OAuth 2.0 API

```
Name: External API
URL: https://external-api.com/v1/status
Auth Type: oauth
OAuth Flow: client_credentials
Client ID: my-client-id
Client Secret: my-client-secret
Token URL: https://oauth-provider.com/token
Scope: read:health write:logs
```

### Example 3: OAuth with Cached Token

For authorization code flow, you must first obtain tokens manually:

```python
# One-time setup to get initial tokens
from authlib.integrations.requests_client import OAuth2Session

client = OAuth2Session(
    client_id='your-client-id',
    client_secret='your-client-secret',
    redirect_uri='http://localhost:5000/callback',
    scope='required scopes'
)

# Get authorization URL
authorization_url, state = client.create_authorization_url(
    'https://provider.com/authorize'
)
# Visit this URL in browser and authorize

# After authorization, exchange code for token
token = client.fetch_token(
    'https://provider.com/token',
    authorization_response='full_callback_url_with_code'
)

print(f"Access Token: {token['access_token']}")
print(f"Refresh Token: {token['refresh_token']}")
```

Then configure the endpoint:
```
Name: User API
URL: https://user-api.com/status
Auth Type: oauth
OAuth Flow: authorization_code
Client ID: your-client-id
Client Secret: your-client-secret
Token URL: https://provider.com/token
Authorization URL: https://provider.com/authorize
Scope: required scopes
Refresh Token: <refresh-token-from-manual-setup>
```

## Token Management

### Automatic Token Refresh

The health monitor automatically manages OAuth tokens:

- **Token Caching**: Valid tokens are cached in the database
- **Automatic Refresh**: Tokens are refreshed 5 minutes before expiration
- **Error Handling**: Authentication failures are logged in health check results

### Token Expiration Buffer

Tokens are refreshed 5 minutes before actual expiration to prevent race conditions and ensure continuous monitoring.

### Token Storage

OAuth tokens are stored in the database:
- `oauth_access_token` - Current access token
- `oauth_refresh_token` - Refresh token (for authorization code flow)
- `oauth_token_expires_at` - Token expiration timestamp

**Security Note:** In production environments, consider encrypting these values at rest.

## Troubleshooting

### Common Issues

**Issue: "OAuth authentication failed: No refresh token available"**
- Solution: For authorization code flow, ensure you've configured a valid refresh token

**Issue: "OAuth authentication failed: invalid_client"**
- Solution: Verify client ID and client secret are correct
- For Azure AD, ensure the app registration has the correct API permissions

**Issue: "OAuth authentication failed: invalid_scope"**
- Solution: Check that the requested scopes are valid for the API
- For Azure AD, ensure you're using the correct scope format (e.g., `api://app-id/.default`)

**Issue: "OAuth authentication failed: unauthorized_client"**
- Solution: For Azure AD, ensure admin consent has been granted for the required API permissions

### Debugging OAuth Issues

1. **Check Token URL**: Ensure the token endpoint URL is correct
2. **Verify Credentials**: Confirm client ID and secret are valid
3. **Review Scopes**: Ensure requested scopes match what the API expects
4. **Check Health Logs**: View the endpoint logs for detailed error messages
5. **Test Manually**: Use a tool like Postman to test OAuth flow independently

## Security Best Practices

1. **Protect Secrets**: 
   - Use environment variables for sensitive OAuth credentials in production
   - Consider using secret management services (HashiCorp Vault, AWS Secrets Manager)

2. **Scope Minimization**:
   - Request only the minimum required scopes
   - Use read-only scopes when possible

3. **Token Security**:
   - Tokens are stored in the database - ensure database is properly secured
   - Consider implementing encryption at rest for production deployments

4. **Monitor Token Usage**:
   - Review health check logs regularly
   - Monitor for authentication failures

5. **Rotate Secrets**:
   - Periodically rotate client secrets
   - Update endpoint configuration after rotation

## Migration

If you have an existing database, run the migration script to add OAuth fields:

```bash
python migrate_oauth.py
```

This adds the following fields to the endpoints table:
- `oauth_flow`
- `oauth_client_id`
- `oauth_client_secret`
- `oauth_token_url`
- `oauth_authorization_url`
- `oauth_scope`
- `oauth_access_token`
- `oauth_refresh_token`
- `oauth_token_expires_at`

## API Reference

### OAuth Utility Classes

**OAuth2Manager**
- `is_token_expired(endpoint)` - Check if token needs refresh
- `get_client_credentials_token(endpoint)` - Get token via client credentials
- `refresh_access_token(endpoint)` - Refresh token using refresh token
- `update_endpoint_token(endpoint, token_response)` - Update endpoint with new token
- `get_valid_token(endpoint)` - Get valid token, refreshing if needed

**AzureADHelper**
- `get_token_url(tenant_id)` - Get Azure AD token endpoint
- `get_authorization_url(tenant_id)` - Get Azure AD authorization endpoint
- `get_default_scope(resource_url)` - Get default Azure AD scope

## Additional Resources

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [Azure AD OAuth 2.0 Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
