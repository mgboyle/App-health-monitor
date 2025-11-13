# Installation Guide

This guide provides detailed installation instructions for App Health Monitor across different environments and platforms.

## System Requirements

### Minimum Requirements

- **Python**: 3.12 or higher
- **RAM**: 512 MB minimum, 1 GB recommended
- **Disk Space**: 100 MB for application + database storage
- **Operating System**: Linux, macOS, or Windows

### Network Requirements

- Outbound HTTPS access to monitored endpoints
- Inbound access on configured port (default: 5000)

## Installation Methods

### Method 1: Standard Python Installation

This is the recommended method for most users.

#### 1. Install Python

=== "Ubuntu/Debian"
    ```bash
    sudo apt update
    sudo apt install python3.12 python3.12-venv python3-pip
    ```

=== "macOS"
    ```bash
    brew install python@3.12
    ```

=== "Windows"
    Download and install Python 3.12 from [python.org](https://www.python.org/downloads/)
    
    Make sure to check "Add Python to PATH" during installation.

#### 2. Clone the Repository

```bash
git clone https://github.com/mgboyle/App-health-monitor.git
cd App-health-monitor
```

#### 3. Create Virtual Environment

=== "Linux/macOS"
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

=== "Windows"
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

#### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 5. Verify Installation

```bash
python run.py
```

Access the application at `http://localhost:5000`.

### Method 2: Docker Installation

Docker provides isolated, reproducible deployments.

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 20.10 or higher
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0 or higher (optional)

#### Option A: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/mgboyle/App-health-monitor.git
cd App-health-monitor

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

#### Option B: Docker CLI

```bash
# Build the image
docker build -t health-monitor .

# Run the container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -e SECRET_KEY=your-secret-key-here \
  --name health-monitor \
  health-monitor

# View logs
docker logs -f health-monitor

# Stop the container
docker stop health-monitor
docker rm health-monitor
```

### Method 3: Development Installation

For contributors and developers.

#### 1. Clone the Repository

```bash
git clone https://github.com/mgboyle/App-health-monitor.git
cd App-health-monitor
```

#### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

This includes testing tools (pytest) and documentation tools (mkdocs).

#### 4. Run Tests

```bash
pytest tests/ -v
```

#### 5. Run the Application

```bash
python run.py
```

See the [Development Setup Guide](../developer-guide/development-setup.md) for more details.

## Post-Installation Setup

### 1. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp config.sample.env .env
```

Edit `.env` with your preferred settings:

```bash
# Security
SECRET_KEY=generate-a-random-secret-key-here

# Database
DATABASE_URL=sqlite:///instance/health_monitor.db

# Application Settings
DEFAULT_CHECK_INTERVAL=60
DEFAULT_TIMEOUT=30
PORT=5000

# Flask Settings
FLASK_ENV=production
```

!!! danger "Security: Secret Key"
    **Never** use the default secret key in production! Generate a strong random key:
    
    ```python
    import secrets
    print(secrets.token_hex(32))
    ```

### 2. Initialize the Database

The database is automatically created on first run. To manually initialize:

```bash
python -c "from app.app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 3. (Optional) Seed Sample Data

For testing purposes, you can add sample endpoints:

```bash
python seed_data.py
```

### 4. Configure Systemd Service (Linux)

For production deployments on Linux, create a systemd service:

```ini
# /etc/systemd/system/health-monitor.service
[Unit]
Description=App Health Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/health-monitor
Environment="PATH=/opt/health-monitor/venv/bin"
ExecStart=/opt/health-monitor/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable health-monitor
sudo systemctl start health-monitor
sudo systemctl status health-monitor
```

## Database Options

### SQLite (Default)

SQLite is the default and requires no additional setup. Perfect for:

- Development
- Small deployments
- Single-server setups
- Quick testing

Database file location: `instance/health_monitor.db`

### PostgreSQL (Production)

For production deployments with multiple instances, use PostgreSQL:

#### 1. Install PostgreSQL

=== "Ubuntu/Debian"
    ```bash
    sudo apt install postgresql postgresql-contrib
    ```

=== "macOS"
    ```bash
    brew install postgresql
    ```

#### 2. Create Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE health_monitor;
CREATE USER healthmon WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE health_monitor TO healthmon;
\q
```

#### 3. Install Python Driver

```bash
pip install psycopg2-binary
```

#### 4. Update Configuration

In `.env`:

```bash
DATABASE_URL=postgresql://healthmon:strong-password@localhost/health_monitor
```

## Verification

After installation, verify everything is working:

### 1. Check Application Status

```bash
curl http://localhost:5000/
```

Should return the HTML dashboard.

### 2. Check API

```bash
curl http://localhost:5000/api/health
```

Should return JSON health status.

### 3. Add a Test Endpoint

```bash
curl -X POST http://localhost:5000/endpoints/add \
  -F "name=GitHub Status" \
  -F "url=https://www.githubstatus.com/api/v2/status.json" \
  -F "endpoint_type=REST" \
  -F "check_interval=300" \
  -F "timeout=30" \
  -F "enabled=on"
```

### 4. View Logs

Check that health checks are running:

```bash
# View application logs (if using systemd)
journalctl -u health-monitor -f

# Or check the web interface
open http://localhost:5000/logs
```

## Upgrading

To upgrade to the latest version:

### Standard Installation

```bash
cd App-health-monitor
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
python run.py
```

### Docker Installation

```bash
cd App-health-monitor
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

## Uninstallation

### Standard Installation

```bash
# Stop the application (Ctrl+C if running in foreground)

# Stop systemd service (if configured)
sudo systemctl stop health-monitor
sudo systemctl disable health-monitor
sudo rm /etc/systemd/system/health-monitor.service

# Remove files
cd ..
rm -rf App-health-monitor
```

### Docker Installation

```bash
docker-compose down -v  # -v removes volumes
cd ..
rm -rf App-health-monitor
```

## Next Steps

- [Configuration Guide](configuration.md) - Configure the application
- [Quick Start](quick-start.md) - Get started quickly
- [Managing Endpoints](managing-endpoints.md) - Add and configure endpoints
- [Production Deployment](../deployment/production.md) - Deploy to production

## Troubleshooting Installation

### Python Version Issues

```bash
# Check Python version
python --version

# If using multiple Python versions
python3.12 --version
```

### Permission Errors

=== "Linux/macOS"
    ```bash
    # Use virtual environment (recommended)
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

=== "Windows"
    Run Command Prompt or PowerShell as Administrator.

### Dependency Conflicts

```bash
# Clear pip cache
pip cache purge

# Reinstall in clean environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Docker Issues

```bash
# Check Docker is running
docker --version
docker ps

# Rebuild without cache
docker-compose build --no-cache

# View detailed logs
docker-compose logs -f
```

For more help, see the [Troubleshooting Guide](troubleshooting.md).
