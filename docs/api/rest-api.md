# REST API Reference

Complete reference for the App Health Monitor REST API.

## Base URL

```
http://localhost:5000/api
```

Replace `localhost:5000` with your server address in production.

## API Endpoints

### GET /api/health

Get overall health status of all monitored endpoints.

**Description:** Returns the current status of all enabled endpoints with their latest health check results.

**Parameters:** None

**Response:**

```json
{
    "status": "healthy" | "degraded" | "unhealthy",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "endpoints": [
        {
            "id": 1,
            "name": "Production API",
            "url": "https://api.example.com/health",
            "type": "REST",
            "status": "success" | "failure" | "timeout" | "validation_failed",
            "status_code": 200,
            "response_time_ms": 123.45,
            "last_checked": "2024-01-01T12:00:00.000Z",
            "error_message": null | "Error details"
        }
    ]
}
```

**Status Calculation:**
- `healthy` - All endpoints successful
- `degraded` - Some endpoints failing
- `unhealthy` - All endpoints failing

**Example:**

```bash
curl http://localhost:5000/api/health
```

---

### GET /api/endpoints

List all configured endpoints.

**Description:** Returns all endpoints with their configuration (passwords excluded).

**Parameters:** None

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
            "validation_enabled": false,
            "validation_type": null,
            "expected_content": null,
            "auth_type": null,
            "auth_username": null,
            "created_at": "2024-01-01T10:00:00.000Z",
            "updated_at": "2024-01-01T10:00:00.000Z"
        }
    ]
}
```

**Example:**

```bash
curl http://localhost:5000/api/endpoints
```

---

### GET /api/endpoints/{id}/checks

Get health check history for a specific endpoint.

**Description:** Returns paginated health check results for an endpoint with statistics.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `limit` | integer | No | 100 | Number of results to return (max: 1000) |
| `page` | integer | No | 1 | Page number for pagination |

**Response:**

```json
{
    "endpoint_id": 1,
    "endpoint_name": "Production API",
    "checks": [
        {
            "id": 1001,
            "status": "success",
            "status_code": 200,
            "response_time": 123.45,
            "error_message": null,
            "validation_error": null,
            "checked_at": "2024-01-01T12:00:00.000Z"
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 100,
        "total": 1000
    },
    "statistics": {
        "total_checks": 1000,
        "successful_checks": 985,
        "failed_checks": 15,
        "uptime_percent": 98.5,
        "average_response_time": 145.67
    }
}
```

**Example:**

```bash
# Get last 50 checks
curl http://localhost:5000/api/endpoints/1/checks?limit=50

# Get page 2
curl http://localhost:5000/api/endpoints/1/checks?limit=100&page=2
```

---

### POST /api/wsdl/operations

Fetch available operations from a WSDL URL.

**Description:** Parses a WSDL file and returns available SOAP operations.

**Request Body:**

```json
{
    "wsdl_url": "http://webservices.example.com/Service.wsdl"
}
```

**Response:**

```json
{
    "operations": [
        {
            "name": "GetStatus",
            "soap_action": "http://example.com/GetStatus"
        },
        {
            "name": "GetData",
            "soap_action": "http://example.com/GetData"
        }
    ]
}
```

**Errors:**

- `400` - Invalid WSDL URL
- `403` - Access forbidden (private IP, localhost)
- `500` - Failed to fetch or parse WSDL

**Security Notes:**
- Blocks requests to localhost, private IPs, link-local addresses
- Maximum response size: 5MB
- Redirects disabled
- Uses defusedxml for secure XML parsing

**Example:**

```bash
curl -X POST http://localhost:5000/api/wsdl/operations \
  -H 'Content-Type: application/json' \
  -d '{"wsdl_url": "http://webservices.example.com/Service.wsdl"}'
```

---

### POST /api/wsdl/sample-payload

Generate sample SOAP payload for an operation.

**Description:** Creates a sample SOAP envelope for a specific WSDL operation.

**Request Body:**

```json
{
    "wsdl_url": "http://webservices.example.com/Service.wsdl",
    "operation_name": "GetStatus"
}
```

**Response:**

```json
{
    "payload": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n  <soap:Body>\n    <GetStatus xmlns=\"http://example.com/\">\n      <parameter>?</parameter>\n    </GetStatus>\n  </soap:Body>\n</soap:Envelope>"
}
```

**Errors:**

- `400` - Invalid WSDL URL or operation name
- `404` - Operation not found in WSDL
- `500` - Failed to generate payload

**Example:**

```bash
curl -X POST http://localhost:5000/api/wsdl/sample-payload \
  -H 'Content-Type: application/json' \
  -d '{
    "wsdl_url": "http://webservices.example.com/Service.wsdl",
    "operation_name": "GetStatus"
  }'
```

---

## Error Responses

All error responses follow this format:

```json
{
    "error": "Error message describing what went wrong",
    "status_code": 400
}
```

### Common Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | Invalid parameters, missing required fields |
| 404 | Not Found | Endpoint ID doesn't exist |
| 500 | Internal Server Error | Database error, unexpected exception |

## Data Types

### Endpoint Object

```json
{
    "id": integer,
    "name": string,
    "url": string,
    "endpoint_type": "REST" | "SOAP" | "WCF" | "GraphQL",
    "check_interval": integer,
    "timeout": integer,
    "enabled": boolean,
    "soap_action": string | null,
    "soap_payload": string | null,
    "validation_enabled": boolean,
    "validation_type": "contains" | "equals" | "regex" | "json_path" | null,
    "expected_content": string | null,
    "auth_type": "Basic" | "Windows" | "Kerberos" | "OAuth" | null,
    "auth_username": string | null,
    "created_at": string (ISO 8601),
    "updated_at": string (ISO 8601)
}
```

### HealthCheck Object

```json
{
    "id": integer,
    "endpoint_id": integer,
    "status": "success" | "failure" | "timeout" | "validation_failed",
    "status_code": integer | null,
    "response_time": float | null,
    "error_message": string | null,
    "validation_error": string | null,
    "checked_at": string (ISO 8601)
}
```

## Usage Examples

### Monitor Multiple Endpoints

```python
import requests
import time

API_BASE = "http://localhost:5000/api"

def check_all_endpoints():
    response = requests.get(f"{API_BASE}/health")
    data = response.json()
    
    print(f"Overall Status: {data['status']}")
    print(f"Timestamp: {data['timestamp']}")
    print("\nEndpoints:")
    
    for endpoint in data['endpoints']:
        status_icon = "✅" if endpoint['status'] == 'success' else "❌"
        print(f"{status_icon} {endpoint['name']}: {endpoint['response_time_ms']:.2f}ms")

if __name__ == "__main__":
    while True:
        check_all_endpoints()
        time.sleep(60)
```

### Get Endpoint Statistics

```python
import requests

def get_endpoint_stats(endpoint_id):
    response = requests.get(f"http://localhost:5000/api/endpoints/{endpoint_id}/checks")
    data = response.json()
    
    stats = data['statistics']
    print(f"Endpoint: {data['endpoint_name']}")
    print(f"Uptime: {stats['uptime_percent']}%")
    print(f"Avg Response Time: {stats['average_response_time']:.2f}ms")
    print(f"Total Checks: {stats['total_checks']}")
    print(f"Successful: {stats['successful_checks']}")
    print(f"Failed: {stats['failed_checks']}")

get_endpoint_stats(1)
```

### Export to CSV

```python
import requests
import csv
from datetime import datetime

def export_checks_to_csv(endpoint_id, filename='checks.csv'):
    response = requests.get(f"http://localhost:5000/api/endpoints/{endpoint_id}/checks?limit=1000")
    data = response.json()
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['checked_at', 'status', 'status_code', 'response_time', 'error_message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for check in data['checks']:
            writer.writerow({
                'checked_at': check['checked_at'],
                'status': check['status'],
                'status_code': check['status_code'] or '',
                'response_time': check['response_time'] or '',
                'error_message': check['error_message'] or ''
            })
    
    print(f"Exported {len(data['checks'])} checks to {filename}")

export_checks_to_csv(1)
```

## Best Practices

### 1. Handle Errors Gracefully

```python
try:
    response = requests.get('http://localhost:5000/api/health', timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
```

### 2. Use Pagination for Large Datasets

```python
def get_all_checks(endpoint_id):
    all_checks = []
    page = 1
    
    while True:
        response = requests.get(
            f"http://localhost:5000/api/endpoints/{endpoint_id}/checks",
            params={'limit': 100, 'page': page}
        )
        data = response.json()
        
        all_checks.extend(data['checks'])
        
        if len(data['checks']) < 100:
            break
        
        page += 1
    
    return all_checks
```

### 3. Cache Responses

```python
import requests_cache

# Cache for 60 seconds
requests_cache.install_cache('health_monitor_cache', expire_after=60)

response = requests.get('http://localhost:5000/api/health')
```

## Rate Limiting (Future)

!!! note "Planned Feature"
    API rate limiting is planned for a future release. See [Roadmap](../../ROADMAP.md#-api-protection).

**Planned limits:**
- `/api/health` - 100 requests/minute
- `/api/endpoints` - 60 requests/minute
- `/api/endpoints/{id}/checks` - 60 requests/minute

## Authentication (Future)

!!! note "Planned Feature"
    API authentication is planned for a future release. See [Roadmap](../../ROADMAP.md#-user-management).

**Planned authentication methods:**
- API keys
- JWT tokens
- OAuth 2.0

## Next Steps

- [API Overview](overview.md) - High-level API introduction
- [OpenAPI Specification](openapi.md) - OpenAPI/Swagger spec
- [User Guide](../user-guide/quick-start.md) - Get started with the application
