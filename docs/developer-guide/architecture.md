# Architecture Overview

This document provides a high-level overview of the App Health Monitor architecture, design decisions, and system components.

## System Architecture

App Health Monitor follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser / API Client              │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Flask Web Application                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Routes &   │  │   Health     │  │  Scheduler   │  │
│  │   Templates  │  │   Checker    │  │ (APScheduler)│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            │ SQLAlchemy ORM
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Database (SQLite / PostgreSQL)              │
│  ┌──────────────────┐  ┌──────────────────────────┐    │
│  │    Endpoints     │  │     Health Checks        │    │
│  │   (Config)       │  │      (Results)           │    │
│  └──────────────────┘  └──────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTP Requests
                            ▼
┌─────────────────────────────────────────────────────────┐
│              External Monitored Endpoints                │
│   REST APIs  │  SOAP Services  │  GraphQL  │  WCF       │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Flask Application (`app/app.py`)

**Responsibility:** Application initialization and configuration

**Key Functions:**
- `create_app()` - Application factory pattern
- Initializes database connection
- Registers blueprints (routes)
- Starts background scheduler
- Manages application lifecycle

**Design Pattern:** Factory Pattern

```python
def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    scheduler = HealthCheckScheduler(app)
    scheduler.start()
    
    return app
```

### 2. Database Models (`app/models.py`)

**Responsibility:** Data structure and persistence

**Models:**

#### Endpoint Model
Stores configuration for monitored endpoints.

**Fields:**
- `id` - Primary key
- `name` - Human-readable name
- `url` - Endpoint URL
- `endpoint_type` - REST, SOAP, WCF, GraphQL
- `check_interval` - Seconds between checks
- `timeout` - Request timeout
- `enabled` - Active/inactive flag
- `soap_action` - SOAP-specific action
- `soap_payload` - SOAP request body
- `validation_enabled` - Enable response validation
- `validation_type` - Validation method
- `expected_content` - Expected response content
- `auth_type` - Authentication method
- `auth_username` - Auth username
- `auth_password` - Auth password (plaintext - security improvement needed)
- `created_at` - Creation timestamp
- `updated_at` - Last modification timestamp

**Relationships:**
- One-to-many with HealthCheck

#### HealthCheck Model
Stores results of health check executions.

**Fields:**
- `id` - Primary key
- `endpoint_id` - Foreign key to Endpoint
- `status` - success, failure, timeout, validation_failed
- `status_code` - HTTP status code
- `response_time` - Response time in milliseconds
- `error_message` - Error details
- `validation_error` - Validation failure details
- `checked_at` - Timestamp of check

**Relationships:**
- Many-to-one with Endpoint

### 3. Routes (`app/routes.py`)

**Responsibility:** HTTP request handling

**Route Categories:**

#### Web UI Routes
- `GET /` - Dashboard (list all endpoints)
- `GET/POST /endpoints/add` - Add new endpoint
- `GET/POST /endpoints/<id>/edit` - Edit endpoint
- `POST /endpoints/<id>/delete` - Delete endpoint
- `POST /endpoints/<id>/check` - Manual health check
- `GET /endpoints/<id>/logs` - View endpoint logs
- `GET /logs` - View all logs

#### API Routes
- `GET /api/health` - Overall health status (JSON)
- `GET /api/endpoints` - List endpoints (JSON)
- `GET /api/endpoints/<id>/checks` - Health check history (JSON)

#### SOAP Helper Routes
- `POST /api/wsdl/operations` - Fetch WSDL operations
- `POST /api/wsdl/sample-payload` - Generate sample SOAP payload

**Design Pattern:** Blueprint Pattern for modular routes

### 4. Health Checker (`app/health_checker.py`)

**Responsibility:** Perform health checks on endpoints

**Key Functions:**

#### `check_endpoint_health(endpoint)`
Executes a health check for a single endpoint.

**Process:**
1. Prepare request (URL, headers, auth, payload)
2. Send HTTP/HTTPS request
3. Measure response time
4. Validate response (if enabled)
5. Store result in database

**Returns:** HealthCheck object

**Error Handling:**
- Connection errors → status: failure
- Timeouts → status: timeout
- Validation failures → status: validation_failed
- Success → status: success

#### Protocol-Specific Handlers

**REST:**
```python
response = requests.get(url, timeout=timeout, auth=auth)
```

**SOAP:**
```python
headers = {'Content-Type': 'text/xml', 'SOAPAction': soap_action}
response = requests.post(url, data=soap_payload, headers=headers)
```

**GraphQL:**
```python
response = requests.post(url, json={'query': query}, timeout=timeout)
```

#### Response Validation

**Validation Types:**
- `contains` - Check if response contains text
- `equals` - Check exact match
- `regex` - Pattern matching
- `json_path` - Validate JSON fields

### 5. Scheduler (`app/scheduler.py`)

**Responsibility:** Background job scheduling

**Implementation:** APScheduler with BackgroundScheduler

**Key Features:**
- Interval-based scheduling
- Per-endpoint schedule
- Automatic job management
- Graceful shutdown

**Workflow:**
1. On app start, load all enabled endpoints
2. For each endpoint, create scheduled job
3. Job runs every `check_interval` seconds
4. Calls `check_endpoint_health()`
5. Stores result in database

**Code Structure:**
```python
class HealthCheckScheduler:
    def __init__(self, app):
        self.scheduler = BackgroundScheduler()
        self.app = app
    
    def start(self):
        with self.app.app_context():
            endpoints = Endpoint.query.filter_by(enabled=True).all()
            for endpoint in endpoints:
                self.schedule_endpoint_check(endpoint)
        
        self.scheduler.start()
    
    def schedule_endpoint_check(self, endpoint):
        self.scheduler.add_job(
            func=self._check_wrapper,
            args=[endpoint.id],
            trigger='interval',
            seconds=endpoint.check_interval,
            id=f'check_endpoint_{endpoint.id}'
        )
```

### 6. Configuration (`app/config.py`)

**Responsibility:** Application configuration management

**Environments:**
- **Development** - Debug enabled, verbose logging
- **Production** - Optimized settings, no debug
- **Testing** - In-memory database, special settings

**Configuration Sources:**
1. Environment variables (highest priority)
2. `.env` file
3. Config class defaults

### 7. SOAP Utilities (`app/soap_utils.py`)

**Responsibility:** SOAP/WSDL handling

**Key Functions:**

#### `fetch_wsdl_operations(wsdl_url)`
Parses WSDL and extracts available operations.

**Process:**
1. Fetch WSDL XML
2. Parse with defusedxml (security)
3. Extract operation names and SOAP actions
4. Return list of operations

**Security:**
- Blocks localhost/private IPs (SSRF protection)
- Uses defusedxml (XXE protection)
- Limits response size (DoS protection)
- Disables redirects

#### `generate_sample_payload(wsdl_url, operation_name)`
Generates sample SOAP envelope for an operation.

**Process:**
1. Fetch and parse WSDL
2. Find operation definition
3. Extract input parameters
4. Generate XML envelope template
5. Return formatted SOAP XML

## Data Flow

### Health Check Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. Scheduler triggers job at configured interval        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  2. Load endpoint configuration from database            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  3. Build HTTP request (URL, auth, headers, payload)     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  4. Send request and measure response time               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  5. Validate response (if validation enabled)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  6. Create HealthCheck record with results               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  7. Save to database                                     │
└─────────────────────────────────────────────────────────┘
```

### Add Endpoint Flow

```
User fills form → POST /endpoints/add
                       │
                       ▼
              Validate input data
                       │
                       ▼
              Create Endpoint record
                       │
                       ▼
              Save to database
                       │
                       ▼
              Add to scheduler
                       │
                       ▼
              Redirect to dashboard
```

## Design Patterns

### 1. Factory Pattern
**Used in:** `create_app()`

**Purpose:** Flexible application initialization

**Benefits:**
- Multiple configuration environments
- Easier testing
- Clean initialization

### 2. Repository Pattern
**Used in:** Database access via SQLAlchemy ORM

**Purpose:** Abstract data access

**Benefits:**
- Database-agnostic code
- Easy to test
- Maintainable queries

### 3. Singleton Pattern
**Used in:** Database session, scheduler instance

**Purpose:** Single shared instance

**Benefits:**
- Resource efficiency
- Consistent state

### 4. Template Method Pattern
**Used in:** Health check execution

**Purpose:** Define algorithm structure

**Benefits:**
- Consistent check flow
- Easy to extend

## Security Considerations

### Current Implementation

1. **CSRF Protection** - Flask session management
2. **SQL Injection** - SQLAlchemy parameterized queries
3. **XSS Protection** - Jinja2 auto-escaping
4. **SSRF Protection** - WSDL fetcher blocks private IPs
5. **XXE Protection** - defusedxml for XML parsing
6. **DoS Protection** - Response size limits

### Security Gaps (Roadmap Items)

1. **Password Encryption** - Currently plaintext
2. **Authentication** - No user authentication system
3. **Authorization** - No RBAC
4. **Rate Limiting** - No API rate limits
5. **Audit Logging** - No security audit trail

See [Security Roadmap](../../ROADMAP.md#-security-enhancements) for planned improvements.

## Performance Characteristics

### Scalability

**Current Limits:**
- Endpoints: ~100-500 per instance
- Check frequency: 1 check per second recommended minimum
- Database: SQLite suitable for <1M records

**Bottlenecks:**
- Network I/O for health checks
- Database writes (especially SQLite)
- Single-threaded scheduler

**Scaling Strategies:**
- Horizontal: Multiple instances with shared PostgreSQL
- Vertical: Increase check intervals, optimize queries
- Caching: Cache endpoint configs in memory

### Resource Usage

**Typical:**
- Memory: 100-200 MB
- CPU: <5% idle, spikes during checks
- Disk I/O: Moderate (log writes)
- Network: Depends on monitored endpoints

## Technology Stack

### Backend
- **Flask 3.0** - Web framework
- **SQLAlchemy 3.1** - ORM
- **APScheduler 3.10** - Job scheduling
- **Requests 2.31** - HTTP client
- **defusedxml 0.7** - Secure XML parsing

### Frontend
- **Jinja2** - Template engine
- **HTML/CSS** - Custom styling
- **Minimal JavaScript** - Progressive enhancement

### Database
- **SQLite** - Default (development, small deployments)
- **PostgreSQL** - Recommended for production

### Deployment
- **Docker** - Containerization
- **Docker Compose** - Orchestration

## Extension Points

### Adding New Endpoint Types

1. Update `endpoint_type` enum in models
2. Add protocol-specific handler in `health_checker.py`
3. Update UI forms/templates
4. Add validation logic

### Custom Validation Types

1. Add validation type to `validation_type` enum
2. Implement validation logic in `health_checker.py`
3. Update UI to support new type

### Custom Notification Channels

1. Create notification handler class
2. Integrate with health check results
3. Add configuration options
4. Update UI

See [Contributing Guide](contributing.md) for development guidelines.

## Future Architecture

### Planned Improvements

1. **Microservices** - Separate checker from API
2. **Message Queue** - Decouple checks from results
3. **Caching Layer** - Redis for performance
4. **API Gateway** - Rate limiting, auth
5. **Time Series DB** - Better metrics storage

See [Roadmap](../../ROADMAP.md) for details.

## Next Steps

- [Database Schema](database-schema.md) - Detailed database design
- [Development Setup](development-setup.md) - Set up dev environment
- [Contributing](contributing.md) - Contribute to the project
- [Testing](testing.md) - Testing guidelines
