# Configuration Guide

This guide covers all configuration options available in App Health Monitor.

## Configuration Methods

App Health Monitor can be configured through:

1. **Environment variables** (recommended for production)
2. **`.env` file** (recommended for development)
3. **`config.py`** (for advanced customization)

## Environment Variables

### Core Settings

#### SECRET_KEY

**Required in production**

Flask secret key for session management and CSRF protection.

```bash
SECRET_KEY=your-very-secret-random-key-here
```

!!! danger "Security Critical"
    Never use the default secret key in production! Generate a strong random key:
    
    ```python
    import secrets
    print(secrets.token_hex(32))
    ```

#### DATABASE_URL

Database connection string.

**Default**: `sqlite:///instance/health_monitor.db`

```bash
# SQLite (default)
DATABASE_URL=sqlite:///instance/health_monitor.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/health_monitor

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost/health_monitor
```

#### FLASK_ENV

Application environment mode.

**Default**: `development`

**Options**: `development`, `production`, `testing`

```bash
FLASK_ENV=production
```

**Effects**:

- `development`: Debug mode ON, auto-reload ON
- `production`: Debug mode OFF, optimized settings
- `testing`: Special test configuration

### Application Settings

#### PORT

Port number for the web server.

**Default**: `5000`

```bash
PORT=8080
```

#### HOST

Host address to bind to.

**Default**: `127.0.0.1` (localhost only)

```bash
# Listen on all interfaces (required for Docker)
HOST=0.0.0.0

# Localhost only
HOST=127.0.0.1
```

#### DEFAULT_CHECK_INTERVAL

Default interval (in seconds) for health checks.

**Default**: `60`

```bash
DEFAULT_CHECK_INTERVAL=300  # 5 minutes
```

#### DEFAULT_TIMEOUT

Default timeout (in seconds) for HTTP requests.

**Default**: `30`

```bash
DEFAULT_TIMEOUT=60
```

### Advanced Settings

#### SQLALCHEMY_DATABASE_URI

Alternative to `DATABASE_URL`. If both are set, `SQLALCHEMY_DATABASE_URI` takes precedence.

```bash
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/health_monitor
```

#### SQLALCHEMY_TRACK_MODIFICATIONS

Track object modifications.

**Default**: `False` (recommended)

```bash
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

#### SQLALCHEMY_ECHO

Log all SQL statements (useful for debugging).

**Default**: `False`

```bash
SQLALCHEMY_ECHO=True  # Enable SQL logging
```

#### LOG_LEVEL

Application logging level.

**Default**: `INFO`

**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

```bash
LOG_LEVEL=DEBUG
```

#### MAX_CONTENT_LENGTH

Maximum size for request bodies (in bytes).

**Default**: `16777216` (16 MB)

```bash
MAX_CONTENT_LENGTH=52428800  # 50 MB
```

## Configuration File (.env)

Create a `.env` file in the project root:

```bash
# Copy sample configuration
cp config.sample.env .env
```

### Sample .env File

```bash
# =============================================================================
# App Health Monitor Configuration
# =============================================================================

# -----------------------------------------------------------------------------
# Security Settings
# -----------------------------------------------------------------------------
# IMPORTANT: Change this to a strong random secret key in production!
SECRET_KEY=change-this-to-a-strong-random-secret-key

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
# SQLite (default - good for development and small deployments)
DATABASE_URL=sqlite:///instance/health_monitor.db

# PostgreSQL (recommended for production)
# DATABASE_URL=postgresql://username:password@localhost:5432/health_monitor

# MySQL
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/health_monitor

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
# Flask environment: development, production, or testing
FLASK_ENV=production

# Server port
PORT=5000

# Server host (0.0.0.0 for all interfaces, 127.0.0.1 for localhost only)
HOST=0.0.0.0

# -----------------------------------------------------------------------------
# Health Check Defaults
# -----------------------------------------------------------------------------
# Default interval between health checks (seconds)
DEFAULT_CHECK_INTERVAL=60

# Default timeout for HTTP requests (seconds)
DEFAULT_TIMEOUT=30

# -----------------------------------------------------------------------------
# Database Settings
# -----------------------------------------------------------------------------
# Disable modification tracking for better performance
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Enable SQL query logging (useful for debugging)
# SQLALCHEMY_ECHO=False

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# -----------------------------------------------------------------------------
# Advanced Settings
# -----------------------------------------------------------------------------
# Maximum request body size (bytes)
MAX_CONTENT_LENGTH=16777216
```

## Configuration by Environment

### Development Configuration

For local development:

```bash
# .env.development
FLASK_ENV=development
SECRET_KEY=dev-secret-key-not-for-production
DATABASE_URL=sqlite:///instance/dev.db
PORT=5000
HOST=127.0.0.1
LOG_LEVEL=DEBUG
SQLALCHEMY_ECHO=True
```

Start with development config:

```bash
cp .env.development .env
python run.py
```

### Production Configuration

For production deployments:

```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://healthmon:SecurePass123@db-server:5432/health_monitor
PORT=5000
HOST=0.0.0.0
LOG_LEVEL=WARNING
SQLALCHEMY_TRACK_MODIFICATIONS=False
DEFAULT_CHECK_INTERVAL=300
DEFAULT_TIMEOUT=60
```

### Testing Configuration

For automated testing:

```bash
# .env.testing
FLASK_ENV=testing
SECRET_KEY=test-secret-key
DATABASE_URL=sqlite:///:memory:
LOG_LEVEL=ERROR
```

## Endpoint-Specific Configuration

When adding endpoints, you can configure:

### REST Endpoints

```python
{
    "name": "Production API",
    "url": "https://api.example.com/health",
    "endpoint_type": "REST",
    "check_interval": 60,      # Check every 60 seconds
    "timeout": 30,              # 30-second timeout
    "enabled": True,
    "validation_enabled": False
}
```

### SOAP/WCF Endpoints

```python
{
    "name": "Legacy SOAP Service",
    "url": "https://soap.example.com/service",
    "endpoint_type": "SOAP",
    "soap_action": "http://example.com/GetData",
    "soap_payload": "<?xml version=\"1.0\"?>...",
    "check_interval": 300,     # Check every 5 minutes
    "timeout": 60,
    "enabled": True
}
```

### Authentication Configuration

#### No Authentication

```python
{
    "auth_type": None
}
```

#### Basic Authentication

```python
{
    "auth_type": "Basic",
    "auth_username": "api_user",
    "auth_password": "api_password"
}
```

!!! warning "Password Security"
    Passwords are currently stored in plaintext. Use environment-specific credentials and consider implementing encryption (see [Security Hardening](../deployment/security.md)).

#### Windows/Kerberos Authentication

```python
{
    "auth_type": "Windows"  # or "Kerberos"
}
```

Requires additional configuration:

```bash
# Install Kerberos tools
pip install requests-kerberos
```

### Response Validation Configuration

#### Contains Validation

Check if response contains specific text:

```python
{
    "validation_enabled": True,
    "validation_type": "contains",
    "expected_content": "healthy"
}
```

#### Equals Validation

Check if response exactly matches:

```python
{
    "validation_enabled": True,
    "validation_type": "equals",
    "expected_content": "OK"
}
```

#### Regex Validation

Check if response matches a pattern:

```python
{
    "validation_enabled": True,
    "validation_type": "regex",
    "expected_content": "^status:\\s*ok$"
}
```

#### JSON Path Validation

Check specific JSON fields:

```python
{
    "validation_enabled": True,
    "validation_type": "json_path",
    "expected_content": "$.status=healthy"
}
```

## Docker Configuration

### docker-compose.yml

Configure Docker Compose deployment:

```yaml
version: '3.8'

services:
  health-monitor:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://healthmon:password@db:5432/health_monitor
      - FLASK_ENV=production
      - PORT=5000
      - HOST=0.0.0.0
    volumes:
      - ./instance:/app/instance
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=health_monitor
      - POSTGRES_USER=healthmon
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Environment Variables in Docker

Pass via `.env` file:

```bash
# .env
SECRET_KEY=your-secret-key
```

Or via `docker-compose`:

```bash
docker-compose up -d
```

Or via `docker run`:

```bash
docker run -d \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///instance/health_monitor.db \
  -e FLASK_ENV=production \
  -p 5000:5000 \
  health-monitor
```

## Configuration Best Practices

### 1. Use Environment-Specific Configs

Keep separate configuration files for each environment:

```
.env.development
.env.staging
.env.production
```

### 2. Never Commit Secrets

Add `.env` to `.gitignore`:

```gitignore
.env
.env.*
!.env.example
```

### 3. Use Strong Secret Keys

Generate cryptographically secure secret keys:

```python
import secrets
print(secrets.token_hex(32))
```

### 4. Use Environment Variables in Production

Don't use `.env` files in production. Set environment variables directly:

```bash
# systemd service
Environment="SECRET_KEY=xxx"
Environment="DATABASE_URL=postgresql://..."

# Docker
docker run -e SECRET_KEY=xxx -e DATABASE_URL=xxx ...

# Kubernetes
envFrom:
  - secretRef:
      name: health-monitor-secrets
```

### 5. Validate Configuration on Startup

The application validates critical configuration on startup:

- `SECRET_KEY` must be set in production
- `DATABASE_URL` must be valid
- Port must be available

## Troubleshooting Configuration

### Configuration Not Loading

Check that `.env` file is in the correct location:

```bash
# Must be in project root
App-health-monitor/
├── .env          <-- Here
├── app/
├── run.py
└── ...
```

### Environment Variables Not Working

Verify environment variables are set:

```bash
echo $SECRET_KEY
echo $DATABASE_URL
```

### Database Connection Errors

Test database connection:

```python
from app.app import create_app
app = create_app()
with app.app_context():
    from app.models import db
    db.create_all()
    print("Database connected successfully!")
```

### Port Already in Use

Change the port:

```bash
PORT=8080 python run.py
```

## Next Steps

- [Managing Endpoints](managing-endpoints.md) - Configure and manage endpoints
- [Security Hardening](../deployment/security.md) - Secure your deployment
- [Production Deployment](../deployment/production.md) - Deploy to production
