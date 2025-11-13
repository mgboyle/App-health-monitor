# Development Setup

This guide will help you set up a local development environment for App Health Monitor.

## Prerequisites

Install the following before starting:

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)
- **pip** - Included with Python
- **virtualenv** (optional) - `pip install virtualenv`

**Optional but Recommended:**
- **VS Code** or **PyCharm** - IDE with Python support
- **Docker Desktop** - For containerized testing
- **PostgreSQL** - For testing with PostgreSQL

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/mgboyle/App-health-monitor.git
cd App-health-monitor
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
# Install all dependencies (including dev tools)
pip install -r requirements-dev.txt
```

This installs:
- Flask, SQLAlchemy (runtime)
- pytest, pytest-cov (testing)
- mkdocs (documentation)

### 4. Set Up Environment Variables

```bash
# Copy sample config
cp config.sample.env .env

# Edit if needed (optional for development)
nano .env
```

### 5. Run the Application

```bash
python run.py
```

Application starts at `http://localhost:5000`

### 6. Run Tests

```bash
pytest tests/ -v
```

All tests should pass ✅

## Detailed Setup

### Virtual Environment

Always use a virtual environment to avoid dependency conflicts:

```bash
# Create
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify
which python
# Should show: /path/to/App-health-monitor/venv/bin/python

# Deactivate when done
deactivate
```

### Installing Dependencies

```bash
# Runtime dependencies only
pip install -r requirements.txt

# Development dependencies (includes runtime)
pip install -r requirements-dev.txt

# Verify installation
pip list
```

### Database Setup

SQLite database is created automatically on first run:

```bash
# Start application
python run.py

# Database created at: instance/health_monitor.db
```

**Manual database initialization:**

```python
from app.app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database created!")
```

**Seed sample data:**

```bash
python seed_data.py
```

## Development Tools

### IDE Setup

#### VS Code

**Recommended Extensions:**
- Python (Microsoft)
- Pylance
- Python Test Explorer
- GitLens
- SQLite Viewer

**Settings (.vscode/settings.json):**
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true,
        "**/instance": true
    }
}
```

#### PyCharm

1. **Open Project** - File → Open → Select App-health-monitor
2. **Configure Interpreter** - Settings → Project → Python Interpreter → Add → Virtualenv → Existing → Select `venv/`
3. **Configure Tests** - Settings → Tools → Python Integrated Tools → Testing → pytest
4. **Run Configuration** - Run → Edit Configurations → Add → Python → Script: `run.py`

### Code Formatting

**Black (Recommended):**
```bash
# Install
pip install black

# Format entire project
black app/ tests/

# Check without formatting
black --check app/ tests/
```

**Flake8 (Linting):**
```bash
# Install
pip install flake8

# Run linter
flake8 app/ tests/

# Configure in setup.cfg
[flake8]
max-line-length = 100
exclude = venv,.git,__pycache__
```

### Git Hooks

Set up pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.12
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_routes.py -v

# Specific test
pytest tests/test_routes.py::test_index -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Writing Tests

See [Testing Guide](testing.md) for details.

**Quick example:**

```python
# tests/test_example.py
def test_endpoint_creation(app):
    """Test creating a new endpoint"""
    with app.app_context():
        endpoint = Endpoint(
            name="Test API",
            url="https://api.example.com/health",
            endpoint_type="REST"
        )
        db.session.add(endpoint)
        db.session.commit()
        
        assert endpoint.id is not None
        assert endpoint.name == "Test API"
```

## Running the Application

### Development Server

```bash
# Standard
python run.py

# Custom port
PORT=8080 python run.py

# Debug mode
FLASK_ENV=development python run.py

# With auto-reload
FLASK_ENV=development FLASK_DEBUG=1 python run.py
```

### Accessing the Application

- **Web UI:** http://localhost:5000
- **API:** http://localhost:5000/api/health
- **Dashboard:** http://localhost:5000/

### Live Reload

Flask automatically reloads when files change in development mode:

```bash
FLASK_ENV=development python run.py
```

## Documentation

### Building Documentation

```bash
# Install mkdocs
pip install -r requirements-dev.txt

# Serve docs locally
mkdocs serve

# Open browser to http://localhost:8000

# Build static site
mkdocs build
```

### Editing Documentation

Documentation is in `docs/` directory using Markdown.

**File structure:**
```
docs/
├── index.md                    # Home page
├── user-guide/
│   ├── quick-start.md
│   ├── installation.md
│   └── ...
├── developer-guide/
│   ├── architecture.md
│   ├── contributing.md
│   └── ...
├── api/
│   └── rest-api.md
└── deployment/
    └── docker.md
```

**Preview changes:**
```bash
mkdocs serve
# Visit http://localhost:8000
```

## Database Development

### SQLite GUI Tools

**DB Browser for SQLite:**
- Download: https://sqlitebrowser.org/
- Open: `instance/health_monitor.db`

**SQLite CLI:**
```bash
# Open database
sqlite3 instance/health_monitor.db

# List tables
.tables

# Show schema
.schema endpoints

# Query data
SELECT * FROM endpoints;

# Exit
.quit
```

### Database Migrations

Currently using `db.create_all()`. For production, use Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Debugging

### Python Debugger

**pdb (Built-in):**
```python
import pdb; pdb.set_trace()
```

**ipdb (Enhanced):**
```bash
pip install ipdb
```
```python
import ipdb; ipdb.set_trace()
```

### VS Code Debugging

**launch.json:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "run.py",
                "FLASK_ENV": "development"
            },
            "args": ["run", "--no-debugger", "--no-reload"],
            "jinja": true
        }
    ]
}
```

### Logging

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python run.py
```

View logs:
```bash
# Application logs (if configured)
tail -f /tmp/health-monitor.log

# Or check console output
```

## Docker Development

### Build Image

```bash
docker build -t health-monitor:dev .
```

### Run Container

```bash
docker run -it -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  health-monitor:dev
```

### Docker Compose

```bash
# Start
docker-compose up

# Rebuild
docker-compose up --build

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

## Common Development Tasks

### Add New Endpoint Type

1. Update `Endpoint.endpoint_type` enum in `models.py`
2. Add handler in `health_checker.py`
3. Update UI templates
4. Add tests
5. Update documentation

### Add New Validation Type

1. Add to `validation_type` enum in `models.py`
2. Implement logic in `health_checker.py`
3. Update UI
4. Add tests
5. Document

### Modify Database Schema

1. Update model in `models.py`
2. Create migration (or delete DB for dev)
3. Update related code
4. Update tests
5. Document changes

## Troubleshooting

### Import Errors

```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements-dev.txt
```

### Tests Failing

```bash
# Run with verbose output
pytest tests/ -vv

# Check specific test
pytest tests/test_routes.py::test_failing -vv

# Reset test database
rm -f instance/test.db
```

### Database Locked

```bash
# Stop all instances
pkill -f "python run.py"

# Remove database
rm instance/health_monitor.db

# Restart
python run.py
```

### Port in Use

```bash
# Find process
lsof -ti:5000

# Kill it
kill -9 $(lsof -ti:5000)

# Or use different port
PORT=8080 python run.py
```

## Best Practices

1. **Always use virtual environment**
2. **Run tests before committing**
3. **Format code with black**
4. **Write docstrings**
5. **Add tests for new features**
6. **Keep commits small and focused**
7. **Update documentation**

## Next Steps

- [Contributing Guide](contributing.md) - How to contribute
- [Testing Guide](testing.md) - Testing guidelines
- [Architecture](architecture.md) - System architecture
- [Database Schema](database-schema.md) - Database design

## Getting Help

- Review existing code and tests
- Check documentation
- Open an issue on GitHub
- Ask in discussions

Happy coding! 🚀
