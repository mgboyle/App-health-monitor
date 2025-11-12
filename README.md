# App Health Monitor

A comprehensive web application for monitoring REST and WCF endpoints with real-time health checks, status tracking, and detailed logging.

![Python Version](https://img.shields.io/badge/python-3.12-blue)
![Flask](https://img.shields.io/badge/flask-3.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- 🔍 **Endpoint Monitoring**: Monitor REST, WCF, SOAP, and GraphQL endpoints
- 📊 **Real-time Dashboard**: View status, latency, and health metrics at a glance
- 📝 **Detailed Logging**: Track all health check results with timestamps and error messages
- ⚡ **Automated Checks**: Background scheduler runs health checks at configurable intervals
- 🌐 **Web UI**: User-friendly interface to manage endpoints and view logs
- 🔌 **REST API**: JSON API for programmatic access to health data
- 💾 **SQLite Storage**: Lightweight local database for storing results
- 🐳 **Docker Support**: Containerized deployment with Docker and Docker Compose
- 🔄 **CI/CD Integration**: GitHub Actions workflow for automated testing and health checks
- 📈 **Statistics**: Uptime percentage, average response times, and success rates

## Quick Start

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mgboyle/App-health-monitor.git
   cd App-health-monitor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Configuration

The application can be configured using environment variables. See `config.sample.env` for available options:

```bash
# Copy the sample configuration
cp config.sample.env .env

# Edit the configuration
nano .env
```

### Key Configuration Options

- `SECRET_KEY`: Secret key for Flask sessions (change in production!)
- `DATABASE_URL`: Database connection string (default: SQLite)
- `DEFAULT_CHECK_INTERVAL`: Default interval for health checks in seconds (default: 60)
- `DEFAULT_TIMEOUT`: Default timeout for requests in seconds (default: 30)
- `PORT`: Application port (default: 5000)

## Usage

### Web Interface

#### Adding an Endpoint

1. Navigate to the dashboard at `http://localhost:5000`
2. Click **"Add Endpoint"**
3. Fill in the endpoint details:
   - **Name**: A friendly name for the endpoint
   - **URL**: The full URL to monitor (e.g., `https://api.example.com/health`)
   - **Type**: REST, WCF, SOAP, or GraphQL
   - **Check Interval**: How often to check (in seconds)
   - **Timeout**: Request timeout (in seconds)
   - **Enable**: Whether to actively monitor this endpoint
4. Click **"Add Endpoint"**

#### Viewing Endpoint Status

The dashboard displays all configured endpoints with:
- Current health status (Healthy/Failed/Timeout)
- HTTP status code
- Response time in milliseconds
- Last check timestamp
- Error messages (if any)

#### Viewing Logs

- **Endpoint-specific logs**: Click "View Logs" on any endpoint card
- **All logs**: Click "All Logs" in the navigation menu

Logs include statistics like:
- Uptime percentage
- Total checks performed
- Number of successful checks
- Average response time

### REST API

The application provides a REST API for programmatic access:

#### Get Overall Health Status

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
      "name": "Production API",
      "url": "https://api.example.com/health",
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

#### List All Endpoints

```bash
curl http://localhost:5000/api/endpoints
```

#### Get Health Checks for an Endpoint

```bash
curl http://localhost:5000/api/endpoints/1/checks?limit=100
```

## Docker Deployment

### Using Docker

Build and run the container:

```bash
# Build the image
docker build -t health-monitor .

# Run the container
docker run -d -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -e SECRET_KEY=your-secret-key \
  health-monitor
```

### Using Docker Compose

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

The database will be persisted in the `./instance` directory on your host machine.

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Project Structure

```
App-health-monitor/
├── app/
│   ├── __init__.py
│   ├── app.py              # Application factory
│   ├── config.py           # Configuration settings
│   ├── models.py           # Database models
│   ├── routes.py           # Web routes and API endpoints
│   ├── health_checker.py   # Health check logic
│   ├── scheduler.py        # Background scheduler
│   ├── static/
│   │   └── css/
│   │       └── style.css   # Application styles
│   └── templates/
│       ├── base.html       # Base template
│       ├── index.html      # Dashboard
│       ├── add_endpoint.html
│       ├── edit_endpoint.html
│       ├── logs.html
│       └── all_logs.html
├── tests/
│   ├── conftest.py         # Test fixtures
│   ├── test_models.py      # Model tests
│   ├── test_routes.py      # Route tests
│   └── test_health_checker.py  # Integration tests
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── config.sample.env
├── run.py                  # Application entry point
└── README.md
```

## CI/CD Integration

The project includes a GitHub Actions workflow that:

1. **Runs tests** on every push and pull request
2. **Builds Docker image** to verify containerization
3. **Performs automated health checks** on a schedule (hourly)
4. **Generates health reports** for all configured endpoints

### Scheduled Health Checks

The workflow runs automatically every hour to check all enabled endpoints and generates a health report. This is useful for:

- Monitoring production endpoints
- Alerting on failures
- Tracking historical uptime data

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard homepage |
| GET/POST | `/endpoints/add` | Add new endpoint |
| GET/POST | `/endpoints/<id>/edit` | Edit endpoint |
| POST | `/endpoints/<id>/delete` | Delete endpoint |
| POST | `/endpoints/<id>/check` | Manually trigger health check |
| GET | `/endpoints/<id>/logs` | View endpoint logs |
| GET | `/logs` | View all logs |
| GET | `/api/health` | Get health status (JSON) |
| GET | `/api/endpoints` | List all endpoints (JSON) |
| GET | `/api/endpoints/<id>/checks` | Get health checks for endpoint (JSON) |

### Data Models

#### Endpoint

```json
{
  "id": 1,
  "name": "Production API",
  "url": "https://api.example.com/health",
  "endpoint_type": "REST",
  "check_interval": 60,
  "timeout": 30,
  "enabled": true,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

#### Health Check

```json
{
  "id": 1,
  "endpoint_id": 1,
  "status": "success",
  "status_code": 200,
  "response_time": 123.45,
  "error_message": null,
  "checked_at": "2024-01-01T12:00:00"
}
```

## Security Considerations

1. **Change the SECRET_KEY**: Always use a strong, random secret key in production
2. **HTTPS**: Deploy behind a reverse proxy with HTTPS enabled
3. **Authentication**: Consider adding authentication for production deployments
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Network Access**: Ensure the application has appropriate network access to monitored endpoints

## Troubleshooting

### Database Issues

If you encounter database errors, try:

```bash
# Remove the database and start fresh
rm -f health_monitor.db
python run.py
```

### Port Already in Use

If port 5000 is already in use:

```bash
PORT=8080 python run.py
```

Or modify the `PORT` environment variable in your configuration.

### Health Checks Not Running

Verify that:
1. Endpoints are enabled in the database
2. The scheduler is running (check application logs)
3. Network connectivity to monitored endpoints is available

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask - Web framework
- SQLAlchemy - Database ORM
- APScheduler - Background job scheduling
- Bootstrap inspiration for UI design

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

Made with ❤️ for monitoring your applications