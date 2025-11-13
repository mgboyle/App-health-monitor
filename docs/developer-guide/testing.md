# Testing Guide

This guide covers testing practices and strategies for App Health Monitor.

## Overview

App Health Monitor uses **pytest** as the testing framework with the following test types:

- **Unit Tests** - Test individual functions and methods
- **Integration Tests** - Test component interactions
- **End-to-End Tests** - Test complete workflows

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ -v --cov=app --cov-report=html
open htmlcov/index.html
```

### Running Specific Tests

```bash
# Specific test file
pytest tests/test_routes.py -v

# Specific test function
pytest tests/test_routes.py::test_index -v

# Tests matching pattern
pytest -k "test_endpoint" -v
```

### Test Output Options

```bash
# Verbose output
pytest tests/ -vv

# Show local variables on failure
pytest tests/ -l

# Stop on first failure
pytest tests/ -x

# Show slowest tests
pytest tests/ --durations=10
```

## Test Structure

### Test Organization

```
tests/
├── __init__.py
├── conftest.py              # Fixtures and test configuration
├── test_models.py           # Database model tests
├── test_routes.py           # HTTP route tests
├── test_health_checker.py   # Health check logic tests
└── test_soap_utils.py       # SOAP utility tests
```

### Test Fixtures

Fixtures are defined in `conftest.py`:

```python
@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for making requests"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI test runner"""
    return app.test_cli_runner()
```

## Writing Tests

### Unit Test Example

```python
def test_endpoint_to_dict():
    """Test Endpoint.to_dict() serialization"""
    endpoint = Endpoint(
        name="Test API",
        url="https://api.example.com/health",
        endpoint_type="REST",
        check_interval=60,
        timeout=30
    )
    
    result = endpoint.to_dict()
    
    assert result['name'] == "Test API"
    assert result['url'] == "https://api.example.com/health"
    assert result['endpoint_type'] == "REST"
    assert result['check_interval'] == 60
```

### Integration Test Example

```python
def test_add_endpoint_workflow(client):
    """Test complete add endpoint workflow"""
    # Submit form
    response = client.post('/endpoints/add', data={
        'name': 'GitHub Status',
        'url': 'https://www.githubstatus.com/api/v2/status.json',
        'endpoint_type': 'REST',
        'check_interval': '300',
        'timeout': '30',
        'enabled': 'on'
    }, follow_redirects=True)
    
    # Check redirect
    assert response.status_code == 200
    
    # Verify database
    endpoint = Endpoint.query.filter_by(name='GitHub Status').first()
    assert endpoint is not None
    assert endpoint.url == 'https://www.githubstatus.com/api/v2/status.json'
    assert endpoint.enabled == True
```

### Mocking External Services

Use `responses` library for HTTP mocking:

```python
import responses

@responses.activate
def test_health_check_success():
    """Test successful health check"""
    # Mock HTTP response
    responses.add(
        responses.GET,
        'https://api.example.com/health',
        json={'status': 'ok'},
        status=200
    )
    
    # Create test endpoint
    endpoint = Endpoint(
        name="Test",
        url="https://api.example.com/health",
        endpoint_type="REST"
    )
    
    # Perform check
    result = check_endpoint_health(endpoint)
    
    # Verify
    assert result.status == 'success'
    assert result.status_code == 200
    assert result.response_time > 0
```

## Test Coverage

### Coverage Goals

- **Minimum:** 70% overall coverage
- **Target:** 80%+ overall coverage
- **Critical paths:** 90%+ coverage

### Checking Coverage

```bash
# Generate coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Show missing lines
pytest tests/ --cov=app --cov-report=term-missing

# HTML report with highlighting
pytest tests/ --cov=app --cov-report=html
```

### Coverage Configuration

Create `.coveragerc`:

```ini
[run]
source = app
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Continuous Integration

Tests run automatically on GitHub Actions for:

- Every push to main branch
- Every pull request
- Scheduled runs (optional)

### CI Configuration

See `.github/workflows/ci.yml` for the complete configuration.

## SOAP Testing

For detailed SOAP testing procedures, see [TESTING.md](../../TESTING.md) which includes:

- VS Code task configurations
- SOAP WSDL fetching tests
- Payload generation tests
- Integration test workflows
- Debugging procedures

## Best Practices

### 1. Test Naming

Use descriptive names that explain what is being tested:

```python
# Good
def test_endpoint_creation_with_valid_data():
    pass

def test_health_check_timeout_handling():
    pass

# Bad
def test1():
    pass

def test_endpoint():
    pass
```

### 2. Arrange-Act-Assert Pattern

Structure tests clearly:

```python
def test_something():
    # Arrange - Set up test data
    endpoint = create_test_endpoint()
    
    # Act - Perform the action
    result = check_endpoint_health(endpoint)
    
    # Assert - Verify the result
    assert result.status == 'success'
```

### 3. Test Independence

Each test should be independent:

```python
# Good - Creates own data
def test_endpoint_creation():
    endpoint = Endpoint(name="Test")
    db.session.add(endpoint)
    db.session.commit()
    assert endpoint.id is not None

# Bad - Depends on other tests
def test_endpoint_exists():
    endpoint = Endpoint.query.first()  # Assumes data exists
    assert endpoint is not None
```

### 4. Use Fixtures

Reuse common setup with fixtures:

```python
@pytest.fixture
def test_endpoint():
    """Create a test endpoint"""
    endpoint = Endpoint(
        name="Test API",
        url="https://api.example.com",
        endpoint_type="REST"
    )
    db.session.add(endpoint)
    db.session.commit()
    return endpoint

def test_with_endpoint(test_endpoint):
    """Test using the fixture"""
    assert test_endpoint.name == "Test API"
```

### 5. Test Edge Cases

Don't just test the happy path:

```python
def test_health_check_with_invalid_url():
    """Test health check with malformed URL"""
    endpoint = Endpoint(url="not-a-url")
    result = check_endpoint_health(endpoint)
    assert result.status == 'failure'

def test_health_check_with_timeout():
    """Test health check that times out"""
    endpoint = Endpoint(url="https://httpstat.us/200?sleep=60000", timeout=1)
    result = check_endpoint_health(endpoint)
    assert result.status == 'timeout'
```

## Debugging Tests

### Print Debugging

```python
def test_something(client):
    response = client.get('/')
    print(response.data)  # Use -s flag: pytest -s
    assert response.status_code == 200
```

### Using pdb

```python
def test_something():
    import pdb; pdb.set_trace()
    # Test code here
```

### VS Code Debugging

1. Set breakpoint in test
2. Run → Debug Test
3. Step through code

## Performance Testing

### Measuring Test Duration

```bash
# Show slowest 10 tests
pytest tests/ --durations=10

# Show all test durations
pytest tests/ --durations=0
```

### Benchmarking

For performance-critical code:

```python
import time

def test_health_check_performance():
    """Ensure health check completes quickly"""
    endpoint = create_test_endpoint()
    
    start = time.time()
    result = check_endpoint_health(endpoint)
    duration = time.time() - start
    
    assert duration < 5.0  # Should complete in < 5 seconds
```

## Testing Guidelines

### What to Test

✅ **Do test:**
- Public API functions
- Database models
- HTTP routes
- Business logic
- Error handling
- Edge cases

❌ **Don't test:**
- Third-party libraries
- Framework internals
- Obvious getters/setters

### When to Write Tests

1. **Before coding** (TDD)
2. **While coding** (alongside features)
3. **After coding** (bug fixes)
4. **When fixing bugs** (regression tests)

## Troubleshooting

### Tests Fail Locally

```bash
# Clear pytest cache
pytest --cache-clear

# Reset database
rm -f instance/test.db

# Reinstall dependencies
pip install -r requirements-dev.txt
```

### Database Locked

```bash
# Ensure no other instances running
pkill -f pytest

# Remove test database
rm -f instance/test.db
```

### Import Errors

```bash
# Verify virtual environment
which python

# Reinstall app
pip install -e .
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)
- [TESTING.md](../../TESTING.md) - SOAP-specific testing guide
- [Contributing Guide](contributing.md) - Contribution workflow

## Next Steps

- [Development Setup](development-setup.md) - Set up dev environment
- [Contributing](contributing.md) - Contribute to the project
- [Architecture](architecture.md) - Understand the system
