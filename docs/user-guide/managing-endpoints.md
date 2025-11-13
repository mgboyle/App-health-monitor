# Managing Endpoints

This guide covers everything you need to know about adding, configuring, and managing endpoints in App Health Monitor.

## Endpoint Types

App Health Monitor supports multiple endpoint types:

### REST APIs

Standard REST/HTTP endpoints.

**Use for:**
- RESTful web services
- HTTP health check endpoints
- JSON APIs
- Simple HTTP GET/POST endpoints

**Example:**
```
URL: https://api.example.com/health
Type: REST
Method: GET (default)
```

### SOAP Web Services

SOAP/XML-based web services.

**Use for:**
- Legacy SOAP services
- WSDL-based services
- XML web services

**Example:**
```
URL: https://soap.example.com/service
Type: SOAP
SOAP Action: http://example.com/GetStatus
Payload: <soap:Envelope>...</soap:Envelope>
```

### WCF Services

Windows Communication Foundation services.

**Use for:**
- .NET WCF services
- Enterprise Windows services

**Example:**
```
URL: http://wcf.example.com/Service.svc
Type: WCF
```

### GraphQL APIs

GraphQL endpoints.

**Use for:**
- GraphQL APIs
- Flexible query-based services

**Example:**
```
URL: https://api.example.com/graphql
Type: GraphQL
Query: { health { status } }
```

## Adding Endpoints

### Via Web Interface

1. Navigate to the dashboard
2. Click **"Add Endpoint"**
3. Fill in the required fields
4. Configure optional settings
5. Click **"Add Endpoint"**

### Via API

```bash
curl -X POST http://localhost:5000/endpoints/add \
  -F "name=My API" \
  -F "url=https://api.example.com/health" \
  -F "endpoint_type=REST" \
  -F "check_interval=60" \
  -F "timeout=30" \
  -F "enabled=on"
```

## Configuration Options

### Basic Settings

#### Name
**Required**

A friendly, descriptive name for the endpoint.

**Best practices:**
- Use clear, specific names
- Include environment (PROD, STAGE, DEV)
- Indicate the service purpose

**Examples:**
- `[PROD] User Service API`
- `[STAGE] Payment Gateway`
- `Legacy Orders SOAP Service`

#### URL
**Required**

The full URL of the endpoint to monitor.

**Format:**
```
https://api.example.com/health
http://internal-service:8080/status
https://soap.example.com/Service.svc
```

**Notes:**
- Must include protocol (http:// or https://)
- Can include port numbers
- Should point to a health check or status endpoint when available

#### Type
**Required**

The protocol type of the endpoint.

**Options:**
- REST
- SOAP
- WCF
- GraphQL

### Health Check Settings

#### Check Interval

How often to perform health checks (in seconds).

**Default:** 60 seconds

**Recommendations:**
- **Critical production:** 30-60 seconds
- **Standard services:** 300 seconds (5 minutes)
- **Low priority:** 900+ seconds (15+ minutes)

**Example:**
```
60    # Check every minute
300   # Check every 5 minutes
3600  # Check every hour
```

#### Timeout

Maximum time to wait for a response (in seconds).

**Default:** 30 seconds

**Recommendations:**
- **Fast APIs:** 10-15 seconds
- **Standard:** 30 seconds
- **Slow services:** 60-120 seconds

**Notes:**
- Should be less than check_interval
- Longer timeouts use more resources

#### Enabled

Whether to actively monitor this endpoint.

**Default:** Enabled

**Use cases for disabling:**
- Temporary maintenance
- Service is down for known reasons
- Testing new configuration

### Authentication

App Health Monitor supports multiple authentication methods.

#### No Authentication

For public endpoints that don't require authentication.

```python
auth_type: None
```

#### Basic Authentication

Username and password authentication.

```python
auth_type: "Basic"
auth_username: "api_user"
auth_password: "api_password"
```

**Example:**
```bash
curl -X POST http://localhost:5000/endpoints/add \
  -F "name=Authenticated API" \
  -F "url=https://api.example.com/secure" \
  -F "endpoint_type=REST" \
  -F "auth_type=Basic" \
  -F "auth_username=user123" \
  -F "auth_password=pass456"
```

!!! warning "Password Storage"
    Passwords are currently stored in plaintext in the database. Use service accounts with limited permissions. See [Security Hardening](../deployment/security.md) for best practices.

#### Windows Authentication

For Windows-integrated services.

```python
auth_type: "Windows"
```

**Requirements:**
- Kerberos configured
- `requests-kerberos` installed

#### Kerberos Authentication

For Kerberos-authenticated services.

```python
auth_type: "Kerberos"
```

**Requirements:**
- Kerberos tickets configured
- `requests-kerberos` installed

### Response Validation

Validate that endpoints not only respond, but respond correctly.

#### Enable Validation

```python
validation_enabled: True
validation_type: "contains"  # or "equals", "regex", "json_path"
expected_content: "healthy"
```

#### Validation Types

##### Contains

Check if the response contains specific text.

**Example:**
```
validation_type: "contains"
expected_content: "status: ok"
```

**Use cases:**
- Simple text-based health checks
- HTML page contains specific content
- Log file contains success message

##### Equals

Check if the response exactly matches expected content.

**Example:**
```
validation_type: "equals"
expected_content: "OK"
```

**Use cases:**
- Simple OK/FAIL responses
- Fixed response format
- Binary health indicators

##### Regex

Match response against a regular expression.

**Example:**
```
validation_type: "regex"
expected_content: "^status:\\s*(ok|healthy)$"
```

**Use cases:**
- Pattern matching
- Multiple valid responses
- Complex text validation

##### JSON Path

Validate specific JSON fields.

**Example:**
```
validation_type: "json_path"
expected_content: "$.status=healthy"
```

**Format:** `jsonpath=expected_value`

**Examples:**
```
$.status=healthy
$.data.health=ok
$.errors.length=0
```

**Use cases:**
- JSON API responses
- Validate specific fields
- Check nested values

### SOAP-Specific Configuration

For SOAP endpoints, additional fields are available:

#### SOAP Action

The SOAP action/method to call.

**Example:**
```
soap_action: "http://example.com/GetStatus"
```

#### SOAP Payload

The XML request body.

**Example:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetStatus xmlns="http://example.com/">
      <ServiceId>12345</ServiceId>
    </GetStatus>
  </soap:Body>
</soap:Envelope>
```

**Helper Tools:**

The UI provides tools to help generate SOAP payloads:

1. **Fetch Operations** - Parse WSDL to list available operations
2. **Generate Payload** - Create sample SOAP envelope for an operation

## Editing Endpoints

### Via Web Interface

1. Click **"Edit"** on the endpoint card
2. Modify the desired fields
3. Click **"Update Endpoint"**

### Via API

```bash
curl -X POST http://localhost:5000/endpoints/1/edit \
  -F "name=Updated Name" \
  -F "check_interval=300"
```

## Deleting Endpoints

### Via Web Interface

1. Click **"Delete"** on the endpoint card
2. Confirm the deletion

### Via API

```bash
curl -X POST http://localhost:5000/endpoints/1/delete
```

!!! danger "Permanent Deletion"
    Deleting an endpoint removes all health check history. This cannot be undone.

## Temporarily Disabling Endpoints

Instead of deleting, you can disable endpoints:

1. Edit the endpoint
2. Uncheck **"Enabled"**
3. Save changes

Disabled endpoints:
- Stop scheduling health checks
- Remain in the dashboard (grayed out)
- Preserve historical data
- Can be re-enabled later

## Manual Health Checks

Trigger an immediate health check:

### Via Web Interface

Click **"Check Now"** on the endpoint card.

### Via API

```bash
curl -X POST http://localhost:5000/endpoints/1/check
```

**Use cases:**
- Test new configuration
- Verify fix after incident
- Force immediate status update

## Best Practices

### 1. Start with Longer Intervals

Begin with 5-minute intervals and adjust based on needs:

```
check_interval: 300  # Start here
```

Increase frequency only for critical endpoints.

### 2. Set Realistic Timeouts

Match timeout to expected response time:

```
# Fast API
timeout: 15

# Slow service
timeout: 120
```

### 3. Use Validation for Critical Endpoints

Don't just check HTTP status - validate the response:

```
validation_enabled: True
validation_type: "json_path"
expected_content: "$.status=operational"
```

### 4. Organize with Naming Conventions

Use consistent naming:

```
[ENV] Service Name - Component
```

Examples:
- `[PROD] Payment API - Checkout`
- `[STAGE] User Service - Auth`

### 5. Monitor the Right Endpoints

Point to dedicated health check endpoints when available:

✅ Good:
- `https://api.example.com/health`
- `https://api.example.com/status`
- `https://api.example.com/v1/healthz`

❌ Avoid:
- Resource endpoints that perform operations
- Endpoints that modify data
- User-facing pages

### 6. Use Service Accounts

For authenticated endpoints, create dedicated monitoring accounts with:

- Read-only access
- Minimal permissions
- Separate from user accounts

## Common Patterns

### Pattern 1: Simple REST Health Check

```json
{
  "name": "[PROD] API Health",
  "url": "https://api.example.com/health",
  "endpoint_type": "REST",
  "check_interval": 60,
  "timeout": 10,
  "validation_enabled": true,
  "validation_type": "json_path",
  "expected_content": "$.status=ok"
}
```

### Pattern 2: Authenticated API

```json
{
  "name": "[PROD] Secure API",
  "url": "https://api.example.com/secure/health",
  "endpoint_type": "REST",
  "auth_type": "Basic",
  "auth_username": "monitor",
  "auth_password": "secret",
  "check_interval": 120,
  "timeout": 30
}
```

### Pattern 3: SOAP Service

```json
{
  "name": "Legacy Order Service",
  "url": "https://soap.example.com/OrderService.svc",
  "endpoint_type": "SOAP",
  "soap_action": "http://example.com/GetServiceStatus",
  "soap_payload": "<?xml version='1.0'?>...",
  "check_interval": 300,
  "timeout": 60
}
```

### Pattern 4: GraphQL API

```json
{
  "name": "[PROD] GraphQL API",
  "url": "https://api.example.com/graphql",
  "endpoint_type": "GraphQL",
  "check_interval": 60,
  "timeout": 30,
  "validation_enabled": true,
  "validation_type": "contains",
  "expected_content": "\"healthy\""
}
```

## Troubleshooting

### Endpoint Always Failing

**Check:**
1. URL is correct and accessible
2. Authentication credentials are valid
3. Timeout is sufficient
4. Validation rules are correct
5. Network connectivity

**Debug:**
```bash
# Test manually with curl
curl -v https://api.example.com/health

# Check with auth
curl -v -u username:password https://api.example.com/health
```

### Timeout Issues

**Solutions:**
1. Increase timeout value
2. Check network latency
3. Verify endpoint performance
4. Consider if endpoint is too slow for monitoring

### Validation Failures

**Check:**
1. Response format matches expected
2. JSON path is correct
3. Regex pattern is valid
4. Case sensitivity

**Debug:**
View the actual response in logs to see what was returned.

## Next Steps

- [Viewing Logs](logs.md) - Review health check history
- [API Reference](../api/rest-api.md) - Programmatic endpoint management
- [Troubleshooting](troubleshooting.md) - Solve common issues
