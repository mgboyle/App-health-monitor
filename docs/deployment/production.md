# Production Best Practices

This guide covers best practices for deploying App Health Monitor in production environments.

## Pre-Deployment Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong, random value
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Plan backup strategy
- [ ] Review security settings
- [ ] Test deployment in staging environment
- [ ] Document deployment procedures

## Environment Configuration

### Production Environment Variables

```bash
# Security
SECRET_KEY=<strong-random-key-64-chars>

# Database
DATABASE_URL=postgresql://healthmon:SecurePass@db-server:5432/health_monitor

# Application
FLASK_ENV=production
HOST=0.0.0.0
PORT=5000

# Health Check Defaults
DEFAULT_CHECK_INTERVAL=300  # 5 minutes
DEFAULT_TIMEOUT=60

# Database
SQLALCHEMY_TRACK_MODIFICATIONS=False
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_RECYCLE=3600

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/health-monitor/app.log
```

### Generate Secure Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

## Database Setup

### PostgreSQL (Recommended)

#### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Verify installation
sudo systemctl status postgresql
```

#### 2. Create Database and User

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE health_monitor;
CREATE USER healthmon WITH ENCRYPTED PASSWORD 'SecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE health_monitor TO healthmon;
\q
```

#### 3. Configure PostgreSQL

Edit `/etc/postgresql/15/main/postgresql.conf`:

```ini
# Connection Settings
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB

# Write-Ahead Logging
wal_level = replica
checkpoint_completion_target = 0.9

# Logging
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_duration = off
log_lock_waits = on
```

#### 4. Update Application Config

```bash
DATABASE_URL=postgresql://healthmon:SecurePassword123!@localhost:5432/health_monitor
```

### Connection Pooling

```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

## Application Server

### Option 1: Gunicorn (Recommended)

Install Gunicorn:

```bash
pip install gunicorn
```

Create `gunicorn_config.py`:

```python
bind = "0.0.0.0:5000"
workers = 4  # (2 x CPU cores) + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 60
keepalive = 5
errorlog = "/var/log/health-monitor/gunicorn_error.log"
accesslog = "/var/log/health-monitor/gunicorn_access.log"
loglevel = "info"
```

Run with Gunicorn:

```bash
gunicorn -c gunicorn_config.py "app.app:create_app()"
```

### Option 2: uWSGI

Install uWSGI:

```bash
pip install uwsgi
```

Create `uwsgi.ini`:

```ini
[uwsgi]
module = app.app:create_app()
callable = app
master = true
processes = 4
threads = 2
socket = /tmp/health-monitor.sock
chmod-socket = 660
vacuum = true
die-on-term = true
```

Run with uWSGI:

```bash
uwsgi --ini uwsgi.ini
```

## Reverse Proxy

### Nginx Configuration

Install Nginx:

```bash
sudo apt install nginx
```

Create `/etc/nginx/sites-available/health-monitor`:

```nginx
upstream health_monitor {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name health-monitor.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name health-monitor.example.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/health-monitor.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/health-monitor.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /var/log/nginx/health-monitor_access.log;
    error_log /var/log/nginx/health-monitor_error.log;
    
    # Proxy Settings
    location / {
        proxy_pass http://health_monitor;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
    
    # Static files (if served separately)
    location /static {
        alias /opt/health-monitor/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/health-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d health-monitor.example.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

## Systemd Service

Create `/etc/systemd/system/health-monitor.service`:

```ini
[Unit]
Description=App Health Monitor
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=healthmon
Group=healthmon
WorkingDirectory=/opt/health-monitor
Environment="PATH=/opt/health-monitor/venv/bin"
Environment="FLASK_ENV=production"
EnvironmentFile=/opt/health-monitor/.env
ExecStart=/opt/health-monitor/venv/bin/gunicorn -c gunicorn_config.py "app.app:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable health-monitor
sudo systemctl start health-monitor
sudo systemctl status health-monitor
```

## Monitoring and Logging

### Application Logging

Configure logging in `config.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory
os.makedirs('/var/log/health-monitor', exist_ok=True)

# Configure logger
handler = RotatingFileHandler(
    '/var/log/health-monitor/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.WARNING)
```

### System Monitoring

Monitor with systemd:

```bash
# View logs
sudo journalctl -u health-monitor -f

# Check status
sudo systemctl status health-monitor

# Resource usage
systemctl show health-monitor --property=MemoryCurrent
systemctl show health-monitor --property=CPUUsageNSec
```

### External Monitoring

Use tools like:

- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **ELK Stack** - Log aggregation
- **Datadog/New Relic** - APM

## Performance Optimization

### Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_health_checks_endpoint_checked 
  ON health_checks(endpoint_id, checked_at DESC);

-- Analyze tables
ANALYZE endpoints;
ANALYZE health_checks;

-- Vacuum
VACUUM ANALYZE;
```

### Application Tuning

```python
# Connection pooling
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
SQLALCHEMY_POOL_RECYCLE = 3600

# Query optimization
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Caching (Future)

Consider adding Redis for caching:

```python
# config.py
CACHE_TYPE = "RedisCache"
CACHE_REDIS_URL = "redis://localhost:6379/0"
CACHE_DEFAULT_TIMEOUT = 300
```

## Scaling Strategies

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize database queries
- Increase worker processes
- Add database indexes

### Horizontal Scaling

- Multiple application instances
- Load balancer (HAProxy, AWS ELB)
- Shared PostgreSQL database
- Redis for session storage

### Architecture for Scale

```
                    ┌─────────────┐
                    │ Load Balancer│
                    └─────┬───────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
     ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
     │  App 1  │    │  App 2  │    │  App 3  │
     └────┬────┘    └────┬────┘    └────┬────┘
          │              │              │
          └──────────────┼──────────────┘
                         │
                    ┌────▼────────┐
                    │ PostgreSQL  │
                    │  (Primary)  │
                    └─────────────┘
```

## High Availability

### Database Replication

Set up PostgreSQL streaming replication:

```bash
# Primary server
wal_level = replica
max_wal_senders = 3
wal_keep_size = 64

# Standby server
hot_standby = on
```

### Application Redundancy

- Multiple app instances
- Health check on each instance
- Automatic failover
- Session persistence

## Maintenance

### Regular Tasks

**Daily:**
- Check logs for errors
- Monitor disk space
- Review failed health checks

**Weekly:**
- Review performance metrics
- Check for security updates
- Analyze slow queries

**Monthly:**
- Update dependencies
- Clean old logs
- Database maintenance (VACUUM, ANALYZE)
- Review and update documentation

### Update Procedure

1. Test in staging
2. Schedule maintenance window
3. Backup database
4. Update code
5. Run migrations
6. Restart services
7. Verify functionality
8. Monitor for issues

```bash
# Update procedure
cd /opt/health-monitor
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
# Run database migrations if needed
sudo systemctl restart health-monitor
sudo systemctl status health-monitor
```

## Disaster Recovery

### Backup Strategy

See [Backup & Recovery Guide](backup.md) for details.

**Key points:**
- Daily automated backups
- Off-site backup storage
- Regular restore testing
- Document recovery procedures

### Recovery Time Objective (RTO)

Target: < 1 hour for full recovery

### Recovery Point Objective (RPO)

Target: < 15 minutes of data loss

## Security

See [Security Hardening Guide](security.md) for comprehensive security practices.

**Key points:**
- HTTPS only
- Strong authentication
- Regular security updates
- Firewall configuration
- Intrusion detection
- Security audits

## Checklist: Go-Live

- [ ] Production database configured
- [ ] SECRET_KEY changed
- [ ] HTTPS/SSL configured
- [ ] Firewall rules set
- [ ] Systemd service created
- [ ] Nginx reverse proxy configured
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backups automated
- [ ] Documentation updated
- [ ] Team trained
- [ ] Runbook created

## Next Steps

- [Docker Deployment](docker.md) - Container deployment
- [Security Hardening](security.md) - Security best practices
- [Backup & Recovery](backup.md) - Backup strategies
