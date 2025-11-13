# Docker Deployment

This guide covers deploying App Health Monitor using Docker and Docker Compose.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/mgboyle/App-health-monitor.git
cd App-health-monitor

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Access application
open http://localhost:5000
```

### Using Docker CLI

```bash
# Build image
docker build -t health-monitor .

# Run container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -e SECRET_KEY=your-secret-key \
  --name health-monitor \
  health-monitor

# View logs
docker logs -f health-monitor
```

## Docker Configuration

### Dockerfile

The included `Dockerfile` is optimized for production:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/instance

# Expose port
EXPOSE 5000

# Environment
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["python", "run.py"]
```

### Optimized Multi-Stage Dockerfile

For smaller images:

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 healthmon && \
    mkdir -p /app/instance && \
    chown -R healthmon:healthmon /app

USER healthmon

EXPOSE 5000

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
```

## Docker Compose

### Basic Configuration

```yaml
version: '3.8'

services:
  health-monitor:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
    restart: unless-stopped
```

### Production Configuration

With PostgreSQL and monitoring:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://healthmon:${DB_PASSWORD}@db:5432/health_monitor
      - FLASK_ENV=production
      - HOST=0.0.0.0
      - PORT=5000
    volumes:
      - app-logs:/var/log/health-monitor
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - health-monitor-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=health_monitor
      - POSTGRES_USER=healthmon
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - health-monitor-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - health-monitor-network

volumes:
  postgres-data:
  app-logs:

networks:
  health-monitor-network:
    driver: bridge
```

### Environment Variables

Create `.env` file:

```bash
SECRET_KEY=your-very-secret-random-key-here
DB_PASSWORD=secure-database-password
```

## Container Management

### Build and Run

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# Start specific service
docker-compose up -d app

# View logs
docker-compose logs -f app

# Follow logs for all services
docker-compose logs -f
```

### Stop and Remove

```bash
# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Scaling

```bash
# Scale app service
docker-compose up -d --scale app=3

# Verify
docker-compose ps
```

## Volume Management

### Data Persistence

Map volumes for persistent data:

```yaml
volumes:
  # SQLite database (if not using PostgreSQL)
  - ./instance:/app/instance
  
  # PostgreSQL data
  - postgres-data:/var/lib/postgresql/data
  
  # Application logs
  - ./logs:/var/log/health-monitor
```

### Backup Volumes

```bash
# Backup volume
docker run --rm \
  -v health-monitor_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres-backup-$(date +%Y%m%d).tar.gz /data

# Restore volume
docker run --rm \
  -v health-monitor_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/postgres-backup-20240101.tar.gz -C /
```

## Networking

### Custom Network

```yaml
networks:
  health-monitor-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### Service Discovery

Services communicate using service names:

```python
# In app, connect to PostgreSQL
DATABASE_URL=postgresql://user:pass@db:5432/health_monitor
```

## Health Checks

### Docker Health Check

Add to `Dockerfile`:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/health', timeout=5)"
```

Or in `docker-compose.yml`:

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Monitoring

### Container Stats

```bash
# View stats
docker stats health-monitor

# All containers
docker-compose stats
```

### Logs

```bash
# Application logs
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app

# Since timestamp
docker-compose logs --since 2024-01-01T12:00:00 app
```

## Production Best Practices

### 1. Use Multi-Stage Builds

Reduce image size and improve security:

```dockerfile
FROM python:3.12-slim AS builder
# Build dependencies

FROM python:3.12-slim
# Runtime only
```

### 2. Run as Non-Root User

```dockerfile
RUN useradd -m -u 1000 healthmon
USER healthmon
```

### 3. Minimize Layers

```dockerfile
# Good: Single layer
RUN apt-get update && \
    apt-get install -y package1 package2 && \
    rm -rf /var/lib/apt/lists/*

# Bad: Multiple layers
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2
```

### 4. Use .dockerignore

Create `.dockerignore`:

```
.git
.gitignore
.env
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
htmlcov/
.coverage
instance/
*.db
README.md
docs/
```

### 5. Security Scanning

```bash
# Scan image for vulnerabilities
docker scan health-monitor

# Use Trivy
trivy image health-monitor
```

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: health-monitor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: health-monitor
  template:
    metadata:
      labels:
        app: health-monitor
    spec:
      containers:
      - name: health-monitor
        image: health-monitor:latest
        ports:
        - containerPort: 5000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: health-monitor-secrets
              key: secret-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: health-monitor-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: health-monitor-service
spec:
  selector:
    app: health-monitor
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs health-monitor

# Inspect container
docker inspect health-monitor

# Start in interactive mode
docker run -it --rm health-monitor /bin/sh
```

### Database Connection Issues

```bash
# Check network
docker network inspect health-monitor_default

# Test connection from app container
docker exec -it health-monitor-app ping db
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Inspect container
docker inspect health-monitor | grep -i memory

# Update resource limits
docker update --memory="512m" --cpus="1.0" health-monitor
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Docker Build and Push

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t health-monitor:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push health-monitor:${{ github.sha }}
```

## Next Steps

- [Production Best Practices](production.md) - Production deployment
- [Security Hardening](security.md) - Security configuration
- [Backup & Recovery](backup.md) - Data protection
