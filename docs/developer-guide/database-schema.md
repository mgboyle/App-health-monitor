# Database Schema

This document describes the database schema for App Health Monitor, including tables, relationships, indexes, and design rationale.

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Endpoint                             │
├─────────────────────────────────────────────────────────────┤
│ PK │ id                    INTEGER                           │
│    │ name                  VARCHAR(200)                      │
│    │ url                   VARCHAR(500)                      │
│    │ endpoint_type         VARCHAR(50)                       │
│    │ check_interval        INTEGER                           │
│    │ timeout               INTEGER                           │
│    │ enabled               BOOLEAN                           │
│    │ soap_action           VARCHAR(500)    [nullable]        │
│    │ soap_payload          TEXT            [nullable]        │
│    │ validation_enabled    BOOLEAN                           │
│    │ validation_type       VARCHAR(20)     [nullable]        │
│    │ expected_content      TEXT            [nullable]        │
│    │ auth_type             VARCHAR(20)     [nullable]        │
│    │ auth_username         VARCHAR(200)    [nullable]        │
│    │ auth_password         VARCHAR(200)    [nullable]        │
│    │ created_at            DATETIME                          │
│    │ updated_at            DATETIME                          │
└────┬────────────────────────────────────────────────────────┘
     │
     │ 1:N
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                      HealthCheck                             │
├─────────────────────────────────────────────────────────────┤
│ PK │ id                    INTEGER                           │
│ FK │ endpoint_id           INTEGER                           │
│    │ status                VARCHAR(20)                       │
│    │ status_code           INTEGER         [nullable]        │
│    │ response_time         FLOAT           [nullable]        │
│    │ error_message         TEXT            [nullable]        │
│    │ validation_error      TEXT            [nullable]        │
│    │ checked_at            DATETIME        [indexed]         │
└─────────────────────────────────────────────────────────────┘
```

## Tables

### `endpoints`

Stores configuration for monitored endpoints.

#### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `name` | VARCHAR(200) | NOT NULL | Human-readable endpoint name |
| `url` | VARCHAR(500) | NOT NULL | Full URL to monitor |
| `endpoint_type` | VARCHAR(50) | NOT NULL, DEFAULT 'REST' | Protocol type: REST, SOAP, WCF, GraphQL |
| `check_interval` | INTEGER | DEFAULT 60 | Seconds between health checks |
| `timeout` | INTEGER | DEFAULT 30 | Request timeout in seconds |
| `enabled` | BOOLEAN | DEFAULT TRUE | Whether to actively monitor |
| `soap_action` | VARCHAR(500) | NULLABLE | SOAP action/method name |
| `soap_payload` | TEXT | NULLABLE | SOAP request XML body |
| `validation_enabled` | BOOLEAN | DEFAULT FALSE | Enable response validation |
| `validation_type` | VARCHAR(20) | NULLABLE | Validation method: contains, equals, regex, json_path |
| `expected_content` | TEXT | NULLABLE | Expected response content for validation |
| `auth_type` | VARCHAR(20) | NULLABLE | Authentication type: None, Basic, Windows, Kerberos, OAuth |
| `auth_username` | VARCHAR(200) | NULLABLE | Username for Basic auth |
| `auth_password` | VARCHAR(200) | NULLABLE | Password for Basic auth (plaintext - needs encryption) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |

#### Indexes

```sql
CREATE INDEX idx_endpoints_enabled ON endpoints(enabled);
CREATE INDEX idx_endpoints_type ON endpoints(endpoint_type);
```

**Rationale:** 
- `enabled` index for fast filtering of active endpoints
- `endpoint_type` index for filtering by protocol type

#### Constraints

```sql
CHECK (check_interval > 0)
CHECK (timeout > 0)
CHECK (endpoint_type IN ('REST', 'SOAP', 'WCF', 'GraphQL'))
CHECK (validation_type IN ('contains', 'equals', 'regex', 'json_path') OR validation_type IS NULL)
CHECK (auth_type IN ('Basic', 'Windows', 'Kerberos', 'OAuth') OR auth_type IS NULL)
```

### `health_checks`

Stores results of health check executions.

#### Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `endpoint_id` | INTEGER | FOREIGN KEY, NOT NULL | Reference to endpoints.id |
| `status` | VARCHAR(20) | NOT NULL | Check result: success, failure, timeout, validation_failed |
| `status_code` | INTEGER | NULLABLE | HTTP status code (if available) |
| `response_time` | FLOAT | NULLABLE | Response time in milliseconds |
| `error_message` | TEXT | NULLABLE | Error details if check failed |
| `validation_error` | TEXT | NULLABLE | Validation failure details |
| `checked_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP, INDEXED | Timestamp of health check |

#### Indexes

```sql
CREATE INDEX idx_health_checks_endpoint_id ON health_checks(endpoint_id);
CREATE INDEX idx_health_checks_checked_at ON health_checks(checked_at);
CREATE INDEX idx_health_checks_status ON health_checks(status);
CREATE INDEX idx_health_checks_endpoint_checked 
  ON health_checks(endpoint_id, checked_at DESC);
```

**Rationale:**
- `endpoint_id` index for fast endpoint-specific queries
- `checked_at` index for time-based queries and sorting
- `status` index for filtering by check result
- Composite index on `(endpoint_id, checked_at)` for common query pattern

#### Foreign Keys

```sql
FOREIGN KEY (endpoint_id) REFERENCES endpoints(id) ON DELETE CASCADE
```

**Cascade Delete:** When an endpoint is deleted, all its health checks are also deleted.

#### Constraints

```sql
CHECK (status IN ('success', 'failure', 'timeout', 'validation_failed'))
CHECK (response_time >= 0 OR response_time IS NULL)
CHECK (status_code >= 100 AND status_code <= 599 OR status_code IS NULL)
```

## Relationships

### One-to-Many: Endpoint → HealthCheck

- One endpoint can have many health check results
- Each health check belongs to exactly one endpoint
- Cascade delete: Deleting an endpoint deletes all its health checks

**SQLAlchemy ORM:**
```python
class Endpoint(db.Model):
    health_checks = db.relationship('HealthCheck', 
                                     backref='endpoint', 
                                     lazy=True, 
                                     cascade='all, delete-orphan')

class HealthCheck(db.Model):
    endpoint_id = db.Column(db.Integer, 
                             db.ForeignKey('endpoints.id'), 
                             nullable=False)
```

## Common Queries

### Get All Enabled Endpoints

```sql
SELECT * FROM endpoints 
WHERE enabled = TRUE
ORDER BY name;
```

### Get Recent Health Checks for Endpoint

```sql
SELECT * FROM health_checks
WHERE endpoint_id = ?
ORDER BY checked_at DESC
LIMIT 100;
```

### Calculate Uptime Statistics

```sql
SELECT 
    endpoint_id,
    COUNT(*) as total_checks,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_checks,
    ROUND(100.0 * SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2) as uptime_percent,
    AVG(CASE WHEN status = 'success' THEN response_time ELSE NULL END) as avg_response_time
FROM health_checks
WHERE endpoint_id = ?
GROUP BY endpoint_id;
```

### Get Latest Status for All Endpoints

```sql
SELECT e.*, 
       hc.status, 
       hc.status_code, 
       hc.response_time, 
       hc.checked_at,
       hc.error_message
FROM endpoints e
LEFT JOIN health_checks hc ON e.id = hc.endpoint_id
WHERE hc.id = (
    SELECT MAX(id) FROM health_checks WHERE endpoint_id = e.id
)
ORDER BY e.name;
```

### Get Failed Checks in Last 24 Hours

```sql
SELECT e.name, hc.*
FROM health_checks hc
JOIN endpoints e ON hc.endpoint_id = e.id
WHERE hc.status IN ('failure', 'timeout', 'validation_failed')
  AND hc.checked_at >= datetime('now', '-1 day')
ORDER BY hc.checked_at DESC;
```

### Delete Old Health Checks (Retention Policy)

```sql
DELETE FROM health_checks
WHERE checked_at < datetime('now', '-90 days');
```

## Database Migrations

### Current State

Database schema is created automatically via SQLAlchemy on first run:

```python
# app/app.py
with app.app_context():
    db.create_all()
```

### Future: Alembic Migrations

For production deployments, use Alembic for schema migrations:

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Planned:** See [Roadmap - Database Optimization](../../ROADMAP.md#-database-optimization)

## Data Types

### SQLite Data Types

| SQLAlchemy Type | SQLite Type | Notes |
|-----------------|-------------|-------|
| INTEGER | INTEGER | Autoincrement for primary keys |
| VARCHAR(n) | TEXT | Length constraint enforced by SQLAlchemy |
| TEXT | TEXT | Unlimited length |
| BOOLEAN | INTEGER | 0 = False, 1 = True |
| DATETIME | TEXT | ISO 8601 format: YYYY-MM-DD HH:MM:SS |
| FLOAT | REAL | Response times in milliseconds |

### PostgreSQL Data Types

For production deployments:

| SQLAlchemy Type | PostgreSQL Type |
|-----------------|-----------------|
| INTEGER | INTEGER |
| VARCHAR(n) | VARCHAR(n) |
| TEXT | TEXT |
| BOOLEAN | BOOLEAN |
| DATETIME | TIMESTAMP |
| FLOAT | REAL |

## Storage Estimates

### Endpoint Table

**Average row size:** ~500 bytes

**Example:**
- 100 endpoints = ~50 KB
- 1,000 endpoints = ~500 KB

### HealthCheck Table

**Average row size:** ~200 bytes

**Growth estimates:**

| Endpoints | Interval | Checks/Day | Data/Day | Data/Month |
|-----------|----------|------------|----------|------------|
| 10 | 60s | 14,400 | ~2.8 MB | ~84 MB |
| 50 | 300s | 14,400 | ~2.8 MB | ~84 MB |
| 100 | 60s | 144,000 | ~28 MB | ~840 MB |

**Retention strategy needed** for large deployments.

## Performance Optimization

### Recommended Indexes

Already implemented:
```sql
CREATE INDEX idx_health_checks_endpoint_checked 
  ON health_checks(endpoint_id, checked_at DESC);
```

**Benefits:**
- Fast endpoint-specific log queries
- Efficient sorting by timestamp
- Covers common dashboard queries

### Additional Indexes (If Needed)

For status-based filtering:
```sql
CREATE INDEX idx_health_checks_endpoint_status 
  ON health_checks(endpoint_id, status);
```

For time-range queries:
```sql
CREATE INDEX idx_health_checks_checked_status 
  ON health_checks(checked_at, status);
```

### Partitioning (PostgreSQL)

For very large deployments, consider table partitioning:

```sql
-- Partition by month
CREATE TABLE health_checks_2024_01 PARTITION OF health_checks
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE health_checks_2024_02 PARTITION OF health_checks
  FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

## Data Retention

### Current Behavior

All data retained indefinitely.

### Recommended Retention Policy

**Detailed logs:**
- Keep for 90 days
- Delete older records

**Aggregated statistics:**
- Hourly aggregates: 1 year
- Daily aggregates: Forever

**Implementation:**

```sql
-- Delete old detailed logs
DELETE FROM health_checks
WHERE checked_at < datetime('now', '-90 days');

-- Create aggregated statistics (future feature)
CREATE TABLE health_check_hourly_stats AS
SELECT 
    endpoint_id,
    strftime('%Y-%m-%d %H:00:00', checked_at) as hour,
    COUNT(*) as total_checks,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
    AVG(CASE WHEN status = 'success' THEN response_time ELSE NULL END) as avg_response_time
FROM health_checks
GROUP BY endpoint_id, strftime('%Y-%m-%d %H:00:00', checked_at);
```

## Security Considerations

### Password Storage

**Current:** Plaintext in `auth_password` column

**Issue:** Security risk if database is compromised

**Planned Fix:** Encrypt passwords using Fernet or hash using bcrypt

```python
from cryptography.fernet import Fernet

# Encrypt before storing
key = Fernet.generate_key()
f = Fernet(key)
encrypted_password = f.encrypt(password.encode())

# Decrypt when needed
decrypted_password = f.decrypt(encrypted_password).decode()
```

See [Roadmap - Security Enhancements](../../ROADMAP.md#-security-enhancements)

### Database Connection Security

**Recommendations:**
- Use SSL/TLS for PostgreSQL connections
- Store credentials in environment variables
- Use connection pooling with timeout
- Restrict database user permissions (no DROP, CREATE)

## Backup and Recovery

### SQLite Backup

```bash
# Simple copy (application must be stopped)
cp instance/health_monitor.db instance/health_monitor.db.backup

# Online backup using SQLite CLI
sqlite3 instance/health_monitor.db ".backup instance/backup.db"

# Automated daily backups
0 2 * * * sqlite3 /path/to/health_monitor.db ".backup /path/to/backups/health_monitor_$(date +\%Y\%m\%d).db"
```

### PostgreSQL Backup

```bash
# Dump database
pg_dump health_monitor > health_monitor_backup.sql

# Restore database
psql health_monitor < health_monitor_backup.sql

# Automated backups
0 2 * * * pg_dump health_monitor | gzip > /path/to/backups/health_monitor_$(date +\%Y\%m\%d).sql.gz
```

See [Backup & Recovery Guide](../deployment/backup.md) for details.

## Schema Evolution

### Version History

**v1.0 (Current)**
- Initial schema
- Endpoints and HealthChecks tables
- Basic validation and auth support

**v1.1 (Planned)**
- Add `Endpoint.tags` for categorization
- Add `Notification` table for alerts
- Add `User` table for authentication
- Encrypt `auth_password` column

**v2.0 (Future)**
- Partition health_checks by time
- Add time-series statistics tables
- Add audit logging table

## Database Administration

### Vacuum (SQLite)

Reclaim unused space:

```bash
sqlite3 instance/health_monitor.db "VACUUM;"
```

### Analyze (SQLite)

Update query planner statistics:

```bash
sqlite3 instance/health_monitor.db "ANALYZE;"
```

### Connection Pooling (PostgreSQL)

```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

## Next Steps

- [Architecture Overview](architecture.md) - System architecture
- [Development Setup](development-setup.md) - Set up dev environment
- [Testing](testing.md) - Testing guidelines
- [Backup & Recovery](../deployment/backup.md) - Production backup strategies
