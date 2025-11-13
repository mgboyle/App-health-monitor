# Troubleshooting Guide

This guide helps you solve common issues with App Health Monitor.

## Installation Issues

### Python Version Errors

**Error:**
```
Python 3.12 or higher is required
```

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.12
# Ubuntu/Debian
sudo apt install python3.12

# macOS
brew install python@3.12

# Or use pyenv
pyenv install 3.12.0
pyenv global 3.12.0
```

### Dependency Installation Fails

**Error:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions:**

1. **Update pip:**
   ```bash
   pip install --upgrade pip
   ```

2. **Clear pip cache:**
   ```bash
   pip cache purge
   pip install -r requirements.txt
   ```

3. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep Flask
```

## Application Startup Issues

### Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

1. **Use different port:**
   ```bash
   PORT=8080 python run.py
   ```

2. **Find and kill process using port:**
   ```bash
   # Linux/macOS
   lsof -ti:5000 | xargs kill -9
   
   # Or
   sudo netstat -tulpn | grep :5000
   sudo kill -9 <PID>
   ```

   ```powershell
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   ```

### Database Errors

**Error:**
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Solutions:**

1. **Check directory permissions:**
   ```bash
   mkdir -p instance
   chmod 755 instance
   ```

2. **Reset database:**
   ```bash
   rm -f instance/health_monitor.db
   python run.py
   ```

3. **Specify database URL:**
   ```bash
   export DATABASE_URL=sqlite:///instance/health_monitor.db
   python run.py
   ```

### Secret Key Warning

**Error:**
```
WARNING: Using default SECRET_KEY. Change this in production!
```

**Solution:**
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set in environment
export SECRET_KEY=<generated-key>

# Or in .env file
echo "SECRET_KEY=<generated-key>" > .env
```

## Health Check Issues

### Endpoints Not Being Checked

**Symptoms:**
- Status shows "Not checked yet"
- Last checked timestamp never updates
- No logs appearing

**Causes & Solutions:**

1. **Endpoint disabled:**
   ```
   Solution: Edit endpoint and enable it
   ```

2. **Scheduler not running:**
   ```bash
   # Check application logs
   # Should see "Scheduler started"
   
   # Restart application
   python run.py
   ```

3. **Check interval too long:**
   ```
   Solution: Reduce check_interval or manually trigger check
   ```

### All Checks Timing Out

**Error:**
```
Status: timeout
Error: Request timed out after 30 seconds
```

**Solutions:**

1. **Increase timeout:**
   ```
   Edit endpoint → Timeout: 60 (or higher)
   ```

2. **Check network connectivity:**
   ```bash
   # Test endpoint manually
   curl -v https://api.example.com/health
   
   # Check DNS resolution
   nslookup api.example.com
   
   # Check firewall
   telnet api.example.com 443
   ```

3. **Check application network access:**
   ```bash
   # From Docker container
   docker exec health-monitor curl https://api.example.com/health
   ```

### SSL/TLS Errors

**Error:**
```
SSLError: certificate verify failed
```

**Solutions:**

1. **Update certificates:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ca-certificates
   sudo update-ca-certificates
   
   # macOS
   brew install ca-certificates
   ```

2. **Check certificate:**
   ```bash
   openssl s_client -connect api.example.com:443
   ```

3. **Temporary workaround (not recommended for production):**
   ```python
   # Modify health_checker.py
   verify=False  # Only for testing!
   ```

### Authentication Failures

**Error:**
```
Status: failure
Status Code: 401
Error: Unauthorized
```

**Solutions:**

1. **Verify credentials:**
   ```bash
   # Test manually
   curl -u username:password https://api.example.com/health
   ```

2. **Check auth type:**
   ```
   Ensure correct auth type selected (Basic, Windows, etc.)
   ```

3. **Update credentials:**
   ```
   Edit endpoint → Update username/password
   ```

### Validation Failures

**Error:**
```
Status: validation_failed
Validation Error: Expected content not found
```

**Solutions:**

1. **Check actual response:**
   ```bash
   # View logs to see what was received
   # Navigate to endpoint logs
   ```

2. **Fix validation rule:**
   ```
   Edit endpoint → Adjust validation rules to match actual response
   ```

3. **Common issues:**
   - Case sensitivity
   - JSON path incorrect
   - Regex pattern too strict
   - Response format changed

## Docker Issues

### Container Won't Start

**Error:**
```
Container exits immediately
```

**Solutions:**

1. **Check logs:**
   ```bash
   docker logs health-monitor
   docker-compose logs -f
   ```

2. **Verify environment variables:**
   ```bash
   docker inspect health-monitor | grep -A 10 Env
   ```

3. **Check volume permissions:**
   ```bash
   ls -la ./instance
   chmod 755 ./instance
   ```

### Database Not Persisting

**Issue:**
- Data lost after container restart

**Solutions:**

1. **Check volume mount:**
   ```yaml
   # docker-compose.yml
   volumes:
     - ./instance:/app/instance
   ```

2. **Verify volume:**
   ```bash
   docker-compose down
   ls -la ./instance
   docker-compose up -d
   ```

### Network Issues in Docker

**Issue:**
- Can't access endpoints from container

**Solutions:**

1. **Use host network:**
   ```yaml
   # docker-compose.yml
   network_mode: "host"
   ```

2. **Allow egress traffic:**
   ```bash
   # Check Docker network
   docker network inspect bridge
   ```

3. **Use correct URLs:**
   ```
   ❌ http://localhost:8080
   ✅ http://host.docker.internal:8080 (Docker Desktop)
   ✅ http://172.17.0.1:8080 (Linux)
   ✅ http://actual-hostname:8080
   ```

## Performance Issues

### Slow Dashboard

**Symptoms:**
- Dashboard takes long time to load
- UI feels sluggish

**Solutions:**

1. **Reduce endpoint count:**
   ```
   Disable unused endpoints
   ```

2. **Increase check intervals:**
   ```
   Change from 60s to 300s (5 minutes)
   ```

3. **Optimize database:**
   ```bash
   # SQLite
   sqlite3 instance/health_monitor.db "VACUUM;"
   
   # Or switch to PostgreSQL
   ```

4. **Clear old logs:**
   ```sql
   DELETE FROM health_checks 
   WHERE checked_at < datetime('now', '-90 days');
   ```

### High Memory Usage

**Symptoms:**
- Application using excessive RAM
- OOM errors

**Solutions:**

1. **Reduce concurrent checks:**
   ```
   Spread out check intervals
   ```

2. **Limit log retention:**
   ```sql
   -- Delete logs older than 30 days
   DELETE FROM health_checks 
   WHERE checked_at < datetime('now', '-30 days');
   ```

3. **Increase container memory:**
   ```yaml
   # docker-compose.yml
   services:
     health-monitor:
       mem_limit: 512m
   ```

### Database Growing Too Large

**Issue:**
- Database file size increasing rapidly

**Solutions:**

1. **Check database size:**
   ```bash
   du -h instance/health_monitor.db
   ```

2. **Archive old data:**
   ```sql
   -- Export to CSV first, then delete
   DELETE FROM health_checks 
   WHERE checked_at < datetime('now', '-90 days');
   
   VACUUM;
   ```

3. **Reduce check frequency:**
   ```
   Increase check_interval for non-critical endpoints
   ```

## API Issues

### 404 Not Found

**Error:**
```
404 Not Found
```

**Solutions:**

1. **Check URL:**
   ```bash
   # Correct
   http://localhost:5000/api/health
   
   # Wrong
   http://localhost:5000/health
   ```

2. **Verify application is running:**
   ```bash
   curl http://localhost:5000/
   ```

3. **Check route registration:**
   ```bash
   # Should show "Running on http://..."
   python run.py
   ```

### 500 Internal Server Error

**Error:**
```
500 Internal Server Error
```

**Solutions:**

1. **Check application logs:**
   ```bash
   # Look for Python traceback
   tail -f /var/log/health-monitor.log
   ```

2. **Enable debug mode:**
   ```bash
   FLASK_ENV=development python run.py
   ```

3. **Check database connection:**
   ```python
   from app.app import create_app
   app = create_app()
   with app.app_context():
       from app.models import db
       db.create_all()
   ```

### CORS Errors

**Error:**
```
Access-Control-Allow-Origin header missing
```

**Solution:**

!!! note "Future Feature"
    CORS support is planned for a future release.

**Workaround:**
```python
# app/app.py
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    # ...
```

## Configuration Issues

### Environment Variables Not Working

**Issue:**
- `.env` file not being loaded

**Solutions:**

1. **Check file location:**
   ```bash
   # Must be in project root
   ls -la .env
   ```

2. **Verify format:**
   ```bash
   # Correct
   SECRET_KEY=value
   
   # Wrong (no spaces around =)
   SECRET_KEY = value
   ```

3. **Check for BOM:**
   ```bash
   # Remove BOM if present
   dos2unix .env
   ```

4. **Load manually:**
   ```bash
   export $(cat .env | xargs)
   python run.py
   ```

### Configuration Override Not Working

**Issue:**
- Changes to config don't take effect

**Solutions:**

1. **Restart application:**
   ```bash
   # Environment variables loaded at startup
   python run.py
   ```

2. **Check precedence:**
   ```
   Environment variables > .env file > config.py defaults
   ```

3. **Verify environment:**
   ```bash
   echo $FLASK_ENV
   echo $SECRET_KEY
   ```

## Common Error Messages

### "Connection refused"

**Cause:** Endpoint is not accessible

**Solutions:**
- Verify endpoint is running
- Check firewall rules
- Verify URL is correct
- Check network connectivity

### "Name or service not known"

**Cause:** DNS resolution failed

**Solutions:**
- Check domain name spelling
- Verify DNS is working
- Try IP address instead
- Check `/etc/hosts` or network config

### "Too many requests"

**Cause:** Rate limiting on monitored endpoint

**Solutions:**
- Increase check_interval
- Contact endpoint provider
- Use different credentials
- Implement backoff strategy

### "SSL certificate problem"

**Cause:** Invalid or expired SSL certificate

**Solutions:**
- Update CA certificates
- Contact endpoint provider
- Verify certificate validity
- Check date/time on server

## Getting Help

If you can't solve your issue:

1. **Check GitHub Issues:**
   - Search existing issues
   - Look for similar problems

2. **Enable Debug Logging:**
   ```bash
   LOG_LEVEL=DEBUG python run.py
   ```

3. **Gather Information:**
   - Application version
   - Python version
   - Operating system
   - Error messages
   - Steps to reproduce

4. **Open an Issue:**
   - Visit [GitHub Issues](https://github.com/mgboyle/App-health-monitor/issues)
   - Provide detailed information
   - Include relevant logs
   - Describe expected vs actual behavior

## Next Steps

- [Configuration Guide](configuration.md) - Review configuration options
- [API Reference](../api/rest-api.md) - API documentation
- [Development Setup](../developer-guide/development-setup.md) - For developers
