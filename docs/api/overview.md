# API Overview

App Health Monitor provides a REST API for programmatic access to health check data and endpoint management.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API does not require authentication.

!!! warning "Production Deployment"
    Authentication and authorization should be implemented for production deployments. See [Roadmap](../../ROADMAP.md#-user-management) for planned features.

## Response Format

All API responses are in JSON format:

```json
{
    "status": "success",
    "data": { ... },
    "message": "Optional message"
}
```

### Success Response

```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00",
    "endpoints": [ ... ]
}
```

### Error Response

```json
{
    "error": "Error message",
    "status_code": 400
}
```

## Rate Limiting

!!! note "Future Feature"
    Rate limiting is not currently implemented. See [Roadmap](../../ROADMAP.md#-api-protection) for planned rate limiting features.

## Endpoints

### Health Status

Get overall health status of all monitored endpoints.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00",
    "endpoints": [
        {
            "name": "Production API",
            "url": "https://api.example.com/health",
            "type": "REST",
            "status": "success",
            "status_code": 200,
            "response_time_ms": 123.45,
            "last_checked": "2024-01-01T12:00:00",
            "error_message": null
        }
    ]
}
```

### List Endpoints

Get all configured endpoints.

**Endpoint:** `GET /api/endpoints`

**Response:**
```json
{
    "endpoints": [
        {
            "id": 1,
            "name": "Production API",
            "url": "https://api.example.com/health",
            "endpoint_type": "REST",
            "check_interval": 60,
            "timeout": 30,
            "enabled": true,
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T10:00:00"
        }
    ]
}
```

### Endpoint Health Checks

Get health check history for a specific endpoint.

**Endpoint:** `GET /api/endpoints/{id}/checks`

**Query Parameters:**
- `limit` (optional) - Number of results (default: 100)
- `page` (optional) - Page number (default: 1)

**Response:**
```json
{
    "endpoint_id": 1,
    "checks": [
        {
            "id": 1001,
            "status": "success",
            "status_code": 200,
            "response_time": 123.45,
            "error_message": null,
            "checked_at": "2024-01-01T12:00:00"
        }
    ],
    "statistics": {
        "total_checks": 1000,
        "successful_checks": 985,
        "uptime_percent": 98.5,
        "average_response_time": 145.67
    }
}
```

### SOAP WSDL Operations

Fetch available operations from a WSDL URL.

**Endpoint:** `POST /api/wsdl/operations`

**Request Body:**
```json
{
    "wsdl_url": "http://example.com/service.wsdl"
}
```

**Response:**
```json
{
    "operations": [
        {
            "name": "GetStatus",
            "soap_action": "http://example.com/GetStatus"
        }
    ]
}
```

### SOAP Sample Payload

Generate sample SOAP payload for an operation.

**Endpoint:** `POST /api/wsdl/sample-payload`

**Request Body:**
```json
{
    "wsdl_url": "http://example.com/service.wsdl",
    "operation_name": "GetStatus"
}
```

**Response:**
```json
{
    "payload": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope>...</soap:Envelope>"
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

## Examples

### cURL

```bash
# Get health status
curl http://localhost:5000/api/health

# List endpoints
curl http://localhost:5000/api/endpoints

# Get endpoint checks
curl http://localhost:5000/api/endpoints/1/checks?limit=50
```

### Python

```python
import requests

# Get health status
response = requests.get('http://localhost:5000/api/health')
data = response.json()
print(f"Status: {data['status']}")

# List endpoints
response = requests.get('http://localhost:5000/api/endpoints')
endpoints = response.json()['endpoints']
for endpoint in endpoints:
    print(f"{endpoint['name']}: {endpoint['url']}")
```

### JavaScript

```javascript
// Get health status
fetch('http://localhost:5000/api/health')
    .then(response => response.json())
    .then(data => {
        console.log('Status:', data.status);
        data.endpoints.forEach(endpoint => {
            console.log(`${endpoint.name}: ${endpoint.status}`);
        });
    });
```

## Next Steps

- [REST API Reference](rest-api.md) - Detailed API documentation
- [OpenAPI Specification](openapi.md) - OpenAPI/Swagger spec
