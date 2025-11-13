# OpenAPI Specification

App Health Monitor OpenAPI (Swagger) specification for API documentation and client generation.

## OpenAPI Specification (v3.0)

```yaml
openapi: 3.0.0
info:
  title: App Health Monitor API
  description: REST API for monitoring endpoint health and managing health checks
  version: 1.0.0
  contact:
    name: App Health Monitor
    url: https://github.com/mgboyle/App-health-monitor
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: http://localhost:5000/api
    description: Development server
  - url: https://your-domain.com/api
    description: Production server

paths:
  /health:
    get:
      summary: Get overall health status
      description: Returns the current health status of all monitored endpoints
      operationId: getHealth
      tags:
        - Health
      responses:
        '200':
          description: Health status retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthStatus'

  /endpoints:
    get:
      summary: List all endpoints
      description: Returns all configured endpoints
      operationId: listEndpoints
      tags:
        - Endpoints
      responses:
        '200':
          description: Endpoints retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  endpoints:
                    type: array
                    items:
                      $ref: '#/components/schemas/Endpoint'

  /endpoints/{id}/checks:
    get:
      summary: Get health check history
      description: Returns health check history for a specific endpoint
      operationId: getEndpointChecks
      tags:
        - Health Checks
      parameters:
        - name: id
          in: path
          required: true
          description: Endpoint ID
          schema:
            type: integer
        - name: limit
          in: query
          required: false
          description: Number of results (max 1000)
          schema:
            type: integer
            default: 100
            maximum: 1000
        - name: page
          in: query
          required: false
          description: Page number
          schema:
            type: integer
            default: 1
            minimum: 1
      responses:
        '200':
          description: Health checks retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthCheckHistory'
        '404':
          description: Endpoint not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /wsdl/operations:
    post:
      summary: Fetch WSDL operations
      description: Parse a WSDL URL and return available operations
      operationId: fetchWsdlOperations
      tags:
        - SOAP
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - wsdl_url
              properties:
                wsdl_url:
                  type: string
                  format: uri
                  example: http://webservices.example.com/Service.wsdl
      responses:
        '200':
          description: Operations fetched successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  operations:
                    type: array
                    items:
                      $ref: '#/components/schemas/WsdlOperation'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /wsdl/sample-payload:
    post:
      summary: Generate SOAP sample payload
      description: Generate a sample SOAP envelope for a WSDL operation
      operationId: generateSoapPayload
      tags:
        - SOAP
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - wsdl_url
                - operation_name
              properties:
                wsdl_url:
                  type: string
                  format: uri
                operation_name:
                  type: string
      responses:
        '200':
          description: Payload generated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  payload:
                    type: string
                    description: SOAP XML envelope
        '400':
          description: Invalid request
        '404':
          description: Operation not found

components:
  schemas:
    HealthStatus:
      type: object
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
        timestamp:
          type: string
          format: date-time
        endpoints:
          type: array
          items:
            $ref: '#/components/schemas/EndpointStatus'

    EndpointStatus:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        url:
          type: string
        type:
          type: string
          enum: [REST, SOAP, WCF, GraphQL]
        status:
          type: string
          enum: [success, failure, timeout, validation_failed]
        status_code:
          type: integer
          nullable: true
        response_time_ms:
          type: number
          format: float
          nullable: true
        last_checked:
          type: string
          format: date-time
          nullable: true
        error_message:
          type: string
          nullable: true

    Endpoint:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        url:
          type: string
        endpoint_type:
          type: string
          enum: [REST, SOAP, WCF, GraphQL]
        check_interval:
          type: integer
          description: Seconds between checks
        timeout:
          type: integer
          description: Request timeout in seconds
        enabled:
          type: boolean
        validation_enabled:
          type: boolean
        validation_type:
          type: string
          enum: [contains, equals, regex, json_path]
          nullable: true
        expected_content:
          type: string
          nullable: true
        auth_type:
          type: string
          enum: [Basic, Windows, Kerberos, OAuth]
          nullable: true
        auth_username:
          type: string
          nullable: true
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    HealthCheck:
      type: object
      properties:
        id:
          type: integer
        endpoint_id:
          type: integer
        status:
          type: string
          enum: [success, failure, timeout, validation_failed]
        status_code:
          type: integer
          nullable: true
        response_time:
          type: number
          format: float
          nullable: true
        error_message:
          type: string
          nullable: true
        validation_error:
          type: string
          nullable: true
        checked_at:
          type: string
          format: date-time

    HealthCheckHistory:
      type: object
      properties:
        endpoint_id:
          type: integer
        endpoint_name:
          type: string
        checks:
          type: array
          items:
            $ref: '#/components/schemas/HealthCheck'
        pagination:
          $ref: '#/components/schemas/Pagination'
        statistics:
          $ref: '#/components/schemas/Statistics'

    Pagination:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer

    Statistics:
      type: object
      properties:
        total_checks:
          type: integer
        successful_checks:
          type: integer
        failed_checks:
          type: integer
        uptime_percent:
          type: number
          format: float
        average_response_time:
          type: number
          format: float

    WsdlOperation:
      type: object
      properties:
        name:
          type: string
        soap_action:
          type: string

    Error:
      type: object
      properties:
        error:
          type: string
        status_code:
          type: integer

tags:
  - name: Health
    description: Overall health status operations
  - name: Endpoints
    description: Endpoint configuration management
  - name: Health Checks
    description: Health check history and results
  - name: SOAP
    description: SOAP/WSDL utilities
```

## Using the Specification

### Import into Swagger Editor

1. Copy the YAML above
2. Visit [Swagger Editor](https://editor.swagger.io/)
3. Paste the specification
4. Explore interactive documentation

### Generate API Clients

Use [OpenAPI Generator](https://openapi-generator.tech/) to create clients:

```bash
# Python client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o python-client

# JavaScript client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g javascript \
  -o js-client

# Java client
openapi-generator-cli generate \
  -i openapi.yaml \
  -g java \
  -o java-client
```

### Interactive Documentation (Future)

!!! note "Planned Feature"
    Built-in Swagger UI is planned for a future release.

**Planned path:** `http://localhost:5000/api/docs`

## Next Steps

- [API Overview](overview.md) - High-level introduction
- [REST API Reference](rest-api.md) - Detailed API docs
- [User Guide](../user-guide/quick-start.md) - Get started
