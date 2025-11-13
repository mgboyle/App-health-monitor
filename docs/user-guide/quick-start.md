# Quick Start Guide

Get App Health Monitor up and running in just a few minutes!

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12 or higher**
- **pip** (Python package manager)
- **Git** (for cloning the repository)

Optional:
- **Docker** (for containerized deployment)
- **Docker Compose** (for orchestrated deployment)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/mgboyle/App-health-monitor.git
cd App-health-monitor
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

!!! tip "Virtual Environment Recommended"
    It's recommended to use a virtual environment to avoid dependency conflicts:
    
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

### 3. Run the Application

```bash
python run.py
```

You should see output similar to:

```
 * Running on http://127.0.0.1:5000
 * Scheduler started
```

### 4. Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

You should see the App Health Monitor dashboard!

## Quick Configuration

### Set Environment Variables

Copy the sample configuration file:

```bash
cp config.sample.env .env
```

Edit the `.env` file to customize your settings:

```bash
# Security
SECRET_KEY=change-this-to-a-random-secret-key

# Database
DATABASE_URL=sqlite:///health_monitor.db

# Defaults
DEFAULT_CHECK_INTERVAL=60
DEFAULT_TIMEOUT=30

# Server
PORT=5000
```

!!! warning "Important: Change the Secret Key"
    Always change the `SECRET_KEY` in production to a strong, random value!

## Add Your First Endpoint

### Using the Web UI

1. Click the **"Add Endpoint"** button on the dashboard
2. Fill in the endpoint details:
   - **Name**: `Example API`
   - **URL**: `https://api.github.com/status`
   - **Type**: `REST`
   - **Check Interval**: `60` (seconds)
   - **Timeout**: `30` (seconds)
3. Click **"Add Endpoint"**

### Using the API

You can also add endpoints programmatically:

```bash
curl -X POST http://localhost:5000/endpoints/add \
  -F "name=Example API" \
  -F "url=https://api.github.com/status" \
  -F "endpoint_type=REST" \
  -F "check_interval=60" \
  -F "timeout=30" \
  -F "enabled=on"
```

## View Health Status

### Web Dashboard

The dashboard automatically refreshes and shows:

- ✅ **Status**: Healthy, Failed, or Timeout
- ⏱️ **Response Time**: In milliseconds
- 🕒 **Last Checked**: Timestamp of the last health check
- 📊 **Statistics**: Uptime percentage and success rate

### API Endpoint

Get health status programmatically:

```bash
curl http://localhost:5000/api/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "endpoints": [
    {
      "name": "Example API",
      "url": "https://api.github.com/status",
      "type": "REST",
      "status": "success",
      "status_code": 200,
      "response_time_ms": 123.45,
      "last_checked": "2024-01-01T12:00:00",
      "error_message": null
    }
  ]
}
```

## Next Steps

Now that you have App Health Monitor running, explore these guides:

- [Installation Guide](installation.md) - Detailed installation options
- [Configuration Guide](configuration.md) - All configuration options
- [Managing Endpoints](managing-endpoints.md) - Learn about endpoint types and features
- [Docker Deployment](../deployment/docker.md) - Deploy with Docker

## Docker Quick Start

Prefer to use Docker? Here's the fastest way:

```bash
# Using Docker Compose
docker-compose up -d

# Access the application
open http://localhost:5000
```

That's it! The application is now running in a container with persistent storage.

## Troubleshooting

### Port Already in Use

If port 5000 is already in use:

```bash
PORT=8080 python run.py
```

### Database Errors

If you encounter database errors, reset the database:

```bash
rm -f instance/health_monitor.db
python run.py
```

### Module Not Found

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

For more troubleshooting tips, see the [Troubleshooting Guide](troubleshooting.md).
