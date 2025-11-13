# Backup & Recovery

This guide covers backup strategies and disaster recovery procedures for App Health Monitor.

## Backup Strategy

### What to Backup

1. **Database** - All endpoint and health check data
2. **Configuration** - .env files, secrets, certificates
3. **Application Code** - (Optional, if customized)

### Backup Frequency

| Data Type | Frequency | Retention |
|-----------|-----------|-----------|
| Database (Full) | Daily | 30 days |
| Database (Incremental) | Hourly | 7 days |
| Configuration | On change | 90 days |
| Logs | Daily | 30 days |

## SQLite Backups

### Manual Backup

```bash
# Stop application
sudo systemctl stop health-monitor

# Copy database file
cp instance/health_monitor.db instance/backups/health_monitor_$(date +%Y%m%d_%H%M%S).db

# Restart application
sudo systemctl start health-monitor
```

### Online Backup (No Downtime)

```bash
# Using SQLite backup command
sqlite3 instance/health_monitor.db ".backup 'backups/health_monitor_$(date +%Y%m%d_%H%M%S).db'"
```

### Automated Daily Backup

Create `/usr/local/bin/backup-health-monitor.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups/health-monitor"
DB_PATH="/opt/health-monitor/instance/health_monitor.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/health_monitor_$DATE.db"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
sqlite3 $DB_PATH ".backup '$BACKUP_FILE'"

# Compress
gzip $BACKUP_FILE

# Remove old backups
find $BACKUP_DIR -name "health_monitor_*.db.gz" -mtime +$RETENTION_DAYS -delete

# Log
echo "$(date): Backup completed: $BACKUP_FILE.gz" >> /var/log/health-monitor-backup.log
```

Make executable and schedule:

```bash
chmod +x /usr/local/bin/backup-health-monitor.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/backup-health-monitor.sh" | crontab -
```

## PostgreSQL Backups

### Manual Backup

```bash
# Full database dump
pg_dump health_monitor > health_monitor_$(date +%Y%m%d).sql

# Compressed
pg_dump health_monitor | gzip > health_monitor_$(date +%Y%m%d).sql.gz

# Custom format (for selective restore)
pg_dump -Fc health_monitor > health_monitor_$(date +%Y%m%d).dump
```

### Automated Backup Script

Create `/usr/local/bin/backup-postgres-health-monitor.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups/postgres"
DB_NAME="health_monitor"
DB_USER="healthmon"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/health_monitor_$DATE.sql.gz"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_FILE

# Verify backup
if [ $? -eq 0 ]; then
    echo "$(date): Backup successful: $BACKUP_FILE" >> /var/log/postgres-backup.log
else
    echo "$(date): Backup FAILED" >> /var/log/postgres-backup.log
    exit 1
fi

# Remove old backups
find $BACKUP_DIR -name "health_monitor_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_FILE s3://my-backups/health-monitor/
```

Schedule:

```bash
# Daily at 2 AM
0 2 * * * /usr/local/bin/backup-postgres-health-monitor.sh

# Hourly incremental (if configured)
0 * * * * /usr/local/bin/backup-postgres-incremental.sh
```

### Point-in-Time Recovery (PITR)

Enable WAL archiving in `postgresql.conf`:

```ini
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backups/postgres/wal/%f'
max_wal_senders = 3
```

Create base backup:

```bash
pg_basebackup -U healthmon -D /backups/postgres/base -Fp -Xs -P
```

## Docker Backups

### Volume Backup

```bash
# Backup Docker volume
docker run --rm \
  -v health-monitor_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres-data-$(date +%Y%m%d).tar.gz /data

# Backup specific files
docker run --rm \
  -v health-monitor_instance:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/instance-$(date +%Y%m%d).tar.gz /data
```

### Container Backup

```bash
# Export container
docker export health-monitor > health-monitor-container-$(date +%Y%m%d).tar

# Or commit to image
docker commit health-monitor health-monitor-backup:$(date +%Y%m%d)
```

## Cloud Backups

### AWS S3

Install AWS CLI:

```bash
sudo apt install awscli
aws configure
```

Backup script:

```bash
#!/bin/bash

LOCAL_BACKUP="/backups/health-monitor/health_monitor_$(date +%Y%m%d).sql.gz"
S3_BUCKET="s3://my-backups/health-monitor/"

# Create local backup
pg_dump health_monitor | gzip > $LOCAL_BACKUP

# Upload to S3
aws s3 cp $LOCAL_BACKUP $S3_BUCKET

# Verify
aws s3 ls $S3_BUCKET

# Set lifecycle policy (optional)
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-backups \
  --lifecycle-configuration file://lifecycle.json
```

Lifecycle policy (`lifecycle.json`):

```json
{
  "Rules": [
    {
      "Id": "DeleteOldBackups",
      "Status": "Enabled",
      "Prefix": "health-monitor/",
      "Expiration": {
        "Days": 90
      }
    }
  ]
}
```

### Google Cloud Storage

```bash
# Install gsutil
curl https://sdk.cloud.google.com | bash

# Upload
gsutil cp backup.sql.gz gs://my-backups/health-monitor/

# Download
gsutil cp gs://my-backups/health-monitor/backup.sql.gz .
```

## Backup Verification

### Verify Backup Integrity

```bash
# Test SQLite backup
sqlite3 backups/health_monitor_20240101.db "PRAGMA integrity_check;"

# Test PostgreSQL backup
gunzip -c backup.sql.gz | head -n 50

# Test restore to temp database
createdb health_monitor_test
gunzip -c backup.sql.gz | psql health_monitor_test
dropdb health_monitor_test
```

### Automated Verification Script

```bash
#!/bin/bash

LATEST_BACKUP=$(ls -t /backups/health-monitor/*.sql.gz | head -1)

# Create temporary database
createdb health_monitor_verify

# Restore
gunzip -c $LATEST_BACKUP | psql health_monitor_verify

# Verify
psql health_monitor_verify -c "SELECT COUNT(*) FROM endpoints;"
RESULT=$?

# Cleanup
dropdb health_monitor_verify

if [ $RESULT -eq 0 ]; then
    echo "$(date): Backup verification PASSED" >> /var/log/backup-verify.log
else
    echo "$(date): Backup verification FAILED" >> /var/log/backup-verify.log
    # Send alert
fi
```

## Recovery Procedures

### SQLite Recovery

**Full Restore:**

```bash
# Stop application
sudo systemctl stop health-monitor

# Restore database
gunzip -c backups/health_monitor_20240101.db.gz > instance/health_monitor.db

# Verify permissions
chown healthmon:healthmon instance/health_monitor.db

# Start application
sudo systemctl start health-monitor

# Verify
curl http://localhost:5000/api/health
```

### PostgreSQL Recovery

**Full Restore:**

```bash
# Stop application
sudo systemctl stop health-monitor

# Drop existing database
sudo -u postgres psql -c "DROP DATABASE health_monitor;"

# Create new database
sudo -u postgres psql -c "CREATE DATABASE health_monitor OWNER healthmon;"

# Restore
gunzip -c backups/health_monitor_20240101.sql.gz | sudo -u postgres psql health_monitor

# Verify
sudo -u postgres psql health_monitor -c "SELECT COUNT(*) FROM endpoints;"

# Start application
sudo systemctl start health-monitor
```

**Point-in-Time Recovery:**

```bash
# Restore base backup
cp -R /backups/postgres/base/* /var/lib/postgresql/15/main/

# Create recovery.conf
cat > /var/lib/postgresql/15/main/recovery.conf << EOF
restore_command = 'cp /backups/postgres/wal/%f %p'
recovery_target_time = '2024-01-01 14:30:00'
EOF

# Start PostgreSQL
sudo systemctl start postgresql

# Verify
psql health_monitor -c "SELECT NOW();"
```

### Docker Volume Recovery

```bash
# Stop containers
docker-compose down

# Restore volume
docker run --rm \
  -v health-monitor_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/postgres-data-20240101.tar.gz -C /

# Start containers
docker-compose up -d
```

## Disaster Recovery

### Recovery Time Objective (RTO)

**Target:** 1 hour

**Steps:**
1. Identify issue (5 min)
2. Access backups (5 min)
3. Restore database (20 min)
4. Verify functionality (10 min)
5. Resume operations (20 min)

### Recovery Point Objective (RPO)

**Target:** 15 minutes (with hourly backups)

**Improvement:**
- Implement WAL archiving
- Real-time replication
- Continuous backup

### Disaster Recovery Plan

1. **Assessment**
   - Identify scope of issue
   - Determine required recovery point

2. **Communication**
   - Notify stakeholders
   - Update status page

3. **Recovery**
   - Execute recovery procedure
   - Verify data integrity
   - Test functionality

4. **Verification**
   - Check all endpoints
   - Review recent health checks
   - Confirm scheduler running

5. **Post-Mortem**
   - Document incident
   - Identify improvements
   - Update procedures

## Backup Monitoring

### Monitor Backup Success

```bash
#!/bin/bash

BACKUP_LOG="/var/log/health-monitor-backup.log"
LAST_BACKUP=$(tail -1 $BACKUP_LOG)

if [[ $LAST_BACKUP == *"completed"* ]]; then
    # Success
    exit 0
else
    # Failure - send alert
    echo "Backup failed!" | mail -s "Health Monitor Backup Alert" admin@example.com
    exit 1
fi
```

### Alerting

Set up alerts for:
- Backup failures
- Missing backups
- Verification failures
- Storage capacity issues

## Best Practices

### 1. 3-2-1 Backup Rule

- **3** copies of data
- **2** different storage types
- **1** off-site copy

### 2. Test Restores Regularly

```bash
# Monthly restore test
0 0 1 * * /usr/local/bin/test-restore.sh
```

### 3. Encrypt Backups

```bash
# Encrypt with GPG
gpg --symmetric --cipher-algo AES256 backup.sql

# Decrypt
gpg --decrypt backup.sql.gpg > backup.sql
```

### 4. Document Procedures

Maintain runbook with:
- Backup locations
- Restore procedures
- Contact information
- Known issues

### 5. Monitor Storage

```bash
# Check backup directory size
du -sh /backups/health-monitor

# Alert if low space
df -h /backups | awk '$5 > "80%" {print "Low disk space!"}'
```

## Backup Retention Policy

| Backup Type | Retention |
|-------------|-----------|
| Hourly | 24 hours |
| Daily | 30 days |
| Weekly | 12 weeks |
| Monthly | 12 months |
| Yearly | 7 years |

Implement in backup script:

```bash
# Daily - keep 30
find /backups/daily -name "*.gz" -mtime +30 -delete

# Weekly - keep 12
find /backups/weekly -name "*.gz" -mtime +84 -delete

# Monthly - keep 12
find /backups/monthly -name "*.gz" -mtime +365 -delete
```

## Next Steps

- [Production Best Practices](production.md) - Production deployment
- [Security Hardening](security.md) - Secure your deployment
- [Docker Deployment](docker.md) - Container backups
