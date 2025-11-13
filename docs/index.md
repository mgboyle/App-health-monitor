# App Health Monitor

Welcome to the comprehensive documentation for **App Health Monitor** - a powerful web application for monitoring REST, SOAP, WCF, and GraphQL endpoints with real-time health checks, status tracking, and detailed logging.

![Python Version](https://img.shields.io/badge/python-3.12-blue)
![Flask](https://img.shields.io/badge/flask-3.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Overview

App Health Monitor is designed to help you maintain visibility into the health and performance of your critical API endpoints. Whether you're monitoring REST APIs, SOAP web services, WCF endpoints, or GraphQL servers, this tool provides a unified interface for tracking their availability, performance, and reliability.

## Key Features

- 🔍 **Multi-Protocol Support**: Monitor REST, WCF, SOAP, and GraphQL endpoints
- 📊 **Real-time Dashboard**: View status, latency, and health metrics at a glance
- 📝 **Detailed Logging**: Track all health check results with timestamps and error messages
- ⚡ **Automated Checks**: Background scheduler runs health checks at configurable intervals
- 🌐 **Web UI**: User-friendly interface to manage endpoints and view logs
- 🔌 **REST API**: JSON API for programmatic access to health data
- 💾 **SQLite Storage**: Lightweight local database for storing results
- 🐳 **Docker Support**: Containerized deployment with Docker and Docker Compose
- 🔄 **CI/CD Integration**: GitHub Actions workflow for automated testing and health checks
- 📈 **Statistics**: Uptime percentage, average response times, and success rates
- 🔐 **Authentication Support**: Basic Auth, Windows Auth, Kerberos, and OAuth
- ✅ **Response Validation**: Validate response content with multiple validation types

## Quick Links

- [Quick Start Guide](user-guide/quick-start.md) - Get up and running in minutes
- [Installation](user-guide/installation.md) - Detailed installation instructions
- [API Reference](api/rest-api.md) - Complete API documentation
- [Docker Deployment](deployment/docker.md) - Deploy with Docker
- [Contributing](developer-guide/contributing.md) - How to contribute to the project

## Use Cases

### 1. Production Monitoring
Monitor critical production APIs to ensure they're healthy and responsive. Get immediate visibility into outages or performance degradation.

### 2. Integration Testing
Continuously verify that external APIs your application depends on are available and responding correctly.

### 3. SLA Compliance
Track uptime statistics and response times to ensure your services meet SLA requirements.

### 4. Multi-Protocol Environments
If you work with legacy SOAP services alongside modern REST APIs, monitor them all from a single dashboard.

### 5. CI/CD Health Checks
Integrate health checks into your CI/CD pipeline to verify deployment success and endpoint availability.

## Architecture

App Health Monitor is built with:

- **Flask**: Lightweight web framework for the web UI and API
- **SQLAlchemy**: ORM for database operations
- **APScheduler**: Background job scheduler for automated health checks
- **SQLite**: Default database (PostgreSQL support available)
- **Bootstrap**: Responsive UI components

## Getting Started

Ready to start monitoring your endpoints? Head over to the [Quick Start Guide](user-guide/quick-start.md) to get up and running in just a few minutes.

## Support

For issues, questions, or contributions:

- [Open an issue on GitHub](https://github.com/mgboyle/App-health-monitor/issues)
- [View the roadmap](roadmap.md)
- [Read the contributing guide](developer-guide/contributing.md)

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/mgboyle/App-health-monitor/blob/main/LICENSE) file for details.
