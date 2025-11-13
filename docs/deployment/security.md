# Security Hardening

This guide covers security best practices for deploying App Health Monitor in production.

## Security Checklist

- [ ] Strong SECRET_KEY configured
- [ ] HTTPS/TLS enabled
- [ ] Database credentials secured
- [ ] Firewall rules configured
- [ ] Regular security updates
- [ ] Access logging enabled
- [ ] Input validation implemented
- [ ] Security headers configured
- [ ] Backup encryption enabled
- [ ] Intrusion detection configured

## Application Security

### 1. Secret Key Management

**Never use default SECRET_KEY in production!**

Generate secure key:

```python
import secrets
secret_key = secrets.token_hex(32)
print(secret_key)
```

Store securely:

```bash
# Environment variable
export SECRET_KEY=<generated-key>

# Or in .env file (not committed to git)
echo "SECRET_KEY=<generated-key>" >> .env

# For Docker
docker run -e SECRET_KEY=<generated-key> ...

# For Kubernetes
kubectl create secret generic health-monitor-secrets \
  --from-literal=secret-key=<generated-key>
```

### 2. Password Storage

**Current Issue:** Passwords stored in plaintext

**Temporary Mitigation:**
- Use service accounts with limited permissions
- Rotate credentials regularly
- Store in environment variables

**Planned Fix:** See [Roadmap - Password Encryption](../../ROADMAP.md#-security-enhancements)

```python
# Future: Encrypted storage
from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
encrypted = f.encrypt(password.encode())
```

### 3. Database Security

**PostgreSQL Configuration:**

```sql
# Create user with limited permissions
CREATE USER healthmon WITH ENCRYPTED PASSWORD 'SecurePassword123!';
GRANT CONNECT ON DATABASE health_monitor TO healthmon;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO healthmon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO healthmon;

# Revoke unnecessary permissions
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
```

**Connection Security:**

```bash
# Use SSL/TLS
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Client certificate authentication
DATABASE_URL=postgresql://user@host:5432/db?sslmode=verify-full&sslcert=/path/to/client.crt&sslkey=/path/to/client.key&sslrootcert=/path/to/ca.crt
```

## Network Security

### 1. HTTPS/TLS

**Always use HTTPS in production!**

**Let's Encrypt (Free):**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d health-monitor.example.com

# Auto-renewal
sudo certbot renew --dry-run
```

**Nginx TLS Configuration:**

```nginx
server {
    listen 443 ssl http2;
    server_name health-monitor.example.com;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/health-monitor.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/health-monitor.example.com/privkey.pem;
    
    # TLS Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/health-monitor.example.com/chain.pem;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
}
```

### 2. Security Headers

Configure security headers in Nginx:

```nginx
# X-Frame-Options (prevent clickjacking)
add_header X-Frame-Options "SAMEORIGIN" always;

# X-Content-Type-Options (prevent MIME sniffing)
add_header X-Content-Type-Options "nosniff" always;

# X-XSS-Protection (legacy XSS protection)
add_header X-XSS-Protection "1; mode=block" always;

# Content-Security-Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

# Referrer-Policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Permissions-Policy
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### 3. Firewall Configuration

**UFW (Ubuntu):**

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block direct access to application port
sudo ufw deny 5000/tcp

# Status
sudo ufw status
```

**iptables:**

```bash
# Allow established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Block everything else
iptables -A INPUT -j DROP

# Save rules
iptables-save > /etc/iptables/rules.v4
```

## Access Control

### 1. Authentication (Future)

!!! note "Planned Feature"
    User authentication is planned for a future release. See [Roadmap](../../ROADMAP.md#-user-management).

**Temporary Measures:**
- Network-level access control
- VPN requirement
- IP whitelisting
- Basic auth via Nginx

**Nginx Basic Auth:**

```bash
# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Configure Nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

### 2. Rate Limiting (Future)

!!! note "Planned Feature"
    API rate limiting is planned. See [Roadmap](../../ROADMAP.md#-api-protection).

**Temporary Nginx Rate Limiting:**

```nginx
# Define rate limit zone
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

# Apply to location
location /api {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://localhost:5000;
}
```

## Input Validation

### 1. WSDL Security

The WSDL parser includes security protections:

**SSRF Protection:**
```python
# Blocks private IPs, localhost, link-local
BLOCKED_PATTERNS = [
    r'^(127\.|localhost|::1)',
    r'^10\.',
    r'^172\.(1[6-9]|2[0-9]|3[01])\.',
    r'^192\.168\.',
    r'^169\.254\.'
]
```

**XXE Protection:**
```python
# Uses defusedxml
from defusedxml.ElementTree import fromstring
```

**DoS Protection:**
```python
# Max response size
MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5MB
```

### 2. SQL Injection Prevention

Using SQLAlchemy ORM prevents SQL injection:

```python
# Safe - parameterized
endpoint = Endpoint.query.filter_by(id=endpoint_id).first()

# Also safe
endpoints = Endpoint.query.filter(Endpoint.name.like(f"%{search}%")).all()
```

### 3. XSS Prevention

Jinja2 auto-escaping prevents XSS:

```html
<!-- Automatically escaped -->
<p>{{ endpoint.name }}</p>

<!-- Explicitly safe (use cautiously) -->
<p>{{ endpoint.description|safe }}</p>
```

## Monitoring and Auditing

### 1. Access Logging

**Nginx Access Logs:**

```nginx
log_format detailed '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '$request_time';

access_log /var/log/nginx/health-monitor_access.log detailed;
```

**Application Logging:**

```python
# Log security events
app.logger.warning(f"Failed login attempt from {request.remote_addr}")
app.logger.info(f"Endpoint added by {current_user}")
```

### 2. Intrusion Detection

**Fail2Ban Configuration:**

```ini
# /etc/fail2ban/jail.local
[health-monitor]
enabled = true
port = http,https
filter = health-monitor
logpath = /var/log/nginx/health-monitor_access.log
maxretry = 5
bantime = 3600
```

**Filter:**

```ini
# /etc/fail2ban/filter.d/health-monitor.conf
[Definition]
failregex = ^<HOST> .* "(GET|POST) .* HTTP/.*" 40[13]
ignoreregex =
```

### 3. Security Scanning

```bash
# Regular updates
sudo apt update && sudo apt upgrade

# Security-only updates
sudo apt install unattended-upgrades

# Scan for vulnerabilities
sudo apt install lynis
sudo lynis audit system
```

## Container Security

### 1. Docker Security

**Run as non-root:**

```dockerfile
RUN useradd -m -u 1000 healthmon
USER healthmon
```

**Read-only filesystem:**

```yaml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /app/instance
```

**Drop capabilities:**

```yaml
services:
  app:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

**Security scanning:**

```bash
# Scan image
docker scan health-monitor

# Use Trivy
trivy image health-monitor
```

### 2. Kubernetes Security

**Pod Security Policy:**

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  runAsUser:
    rule: MustRunAsNonRoot
  seLinux:
    rule: RunAsAny
  fsGroup:
    rule: RunAsAny
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'secret'
```

## Backup Security

### 1. Encrypt Backups

```bash
# Encrypt backup
gpg --symmetric --cipher-algo AES256 backup.sql

# Decrypt
gpg --decrypt backup.sql.gpg > backup.sql
```

### 2. Secure Backup Storage

- Use encrypted storage (S3 with encryption)
- Limit access permissions
- Regular backup verification
- Off-site storage

## Compliance

### GDPR Considerations

If monitoring endpoints with user data:

- Document data processing
- Implement data retention policies
- Enable data deletion
- Provide data export
- Maintain audit logs

### SOC 2 / ISO 27001

For enterprise compliance:

- Access control policies
- Change management
- Incident response plan
- Regular security audits
- Vendor risk assessments

## Security Incident Response

### 1. Detection

Monitor for:
- Unusual traffic patterns
- Failed authentication attempts
- Suspicious database queries
- Unexpected system changes

### 2. Response Plan

1. **Identify** the incident
2. **Contain** the threat
3. **Eradicate** the vulnerability
4. **Recover** systems
5. **Document** lessons learned

### 3. Contact Information

Keep updated:
- Security team contacts
- Vendor contacts
- Law enforcement (if needed)
- Customer notification plan

## Security Updates

### Keep Software Updated

```bash
# System updates
sudo apt update && sudo apt upgrade

# Python packages
pip list --outdated
pip install -r requirements.txt --upgrade

# Docker images
docker pull python:3.12-slim
docker-compose build --no-cache
```

### Vulnerability Monitoring

- Subscribe to security advisories
- Monitor CVE databases
- Use automated scanning tools
- Regular security audits

## Next Steps

- [Production Best Practices](production.md) - Production deployment
- [Docker Deployment](docker.md) - Container security
- [Backup & Recovery](backup.md) - Secure backups
