# Contributing Guide

Thank you for your interest in contributing to App Health Monitor! This guide will help you get started.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We welcome contributors of all skill levels.

## Ways to Contribute

### 1. Report Bugs

Found a bug? Please open an issue with:

- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or screenshots

**Template:**
```markdown
**Bug Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.12.0
- App Version: 1.0.0

**Additional Context:**
Any other relevant information
```

### 2. Suggest Features

Have an idea? Open an issue tagged `enhancement`:

- Describe the feature
- Explain the use case
- Propose implementation (optional)
- Note any potential impacts

### 3. Improve Documentation

Documentation improvements are always welcome:

- Fix typos
- Clarify confusing sections
- Add examples
- Translate to other languages (future)

### 4. Submit Code

Contribute bug fixes or new features:

- Fork the repository
- Create a feature branch
- Make your changes
- Add tests
- Submit a pull request

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Virtual environment tool

### Setup Steps

1. **Fork and Clone**

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/App-health-monitor.git
cd App-health-monitor
```

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

4. **Set Up Database**

```bash
# Database is auto-created on first run
python run.py
# Press Ctrl+C to stop
```

5. **Run Tests**

```bash
pytest tests/ -v
```

6. **Start Development Server**

```bash
python run.py
```

Application runs at `http://localhost:5000`

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Changes

Follow the coding standards (see below).

### 3. Write Tests

Add tests for new functionality:

```python
# tests/test_your_feature.py
def test_new_feature(client):
    """Test your new feature"""
    response = client.get('/your-endpoint')
    assert response.status_code == 200
```

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test
pytest tests/test_routes.py::test_index -v
```

### 5. Lint Code

```bash
# Format code (if using black)
black app/ tests/

# Check PEP 8 compliance
flake8 app/ tests/
```

### 6. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: endpoint health statistics"
```

**Commit message format:**
```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code restructuring
- `test` - Tests
- `chore` - Maintenance

**Examples:**
```
feat: add SOAP endpoint support

Add SOAP/WSDL parsing and health check support for SOAP services.
Includes WSDL operation fetching and sample payload generation.

Closes #42
```

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Pull Request Guidelines

### PR Title

Clear and descriptive:

```
Add SOAP endpoint support
Fix timeout handling for slow endpoints
Update installation documentation
```

### PR Description

Include:

- **What:** What does this PR do?
- **Why:** Why is this change needed?
- **How:** How was it implemented?
- **Testing:** How was it tested?
- **Screenshots:** If UI changes

**Template:**
```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Before and after screenshots

## Related Issues
Closes #123
```

### PR Checklist

Before submitting:

- [ ] Code follows project style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass locally
- [ ] Documentation updated (if needed)
- [ ] No sensitive data in commits
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

## Coding Standards

### Python Style Guide

Follow PEP 8 with some modifications:

**Line Length:** 100 characters (not 79)

**Imports:**
```python
# Standard library
import os
from datetime import datetime

# Third-party
from flask import Flask, render_template
import requests

# Local
from app.models import Endpoint, HealthCheck
from app.health_checker import check_endpoint_health
```

**Docstrings:**
```python
def check_endpoint_health(endpoint):
    """
    Perform a health check on the given endpoint.
    
    Args:
        endpoint (Endpoint): The endpoint to check
        
    Returns:
        HealthCheck: Result of the health check
        
    Raises:
        ValueError: If endpoint is invalid
    """
    pass
```

**Type Hints (Optional but Encouraged):**
```python
from typing import List, Optional

def get_endpoints(enabled: bool = True) -> List[Endpoint]:
    """Get list of endpoints"""
    return Endpoint.query.filter_by(enabled=enabled).all()
```

### Naming Conventions

**Variables and Functions:** `snake_case`
```python
check_interval = 60
def check_endpoint_health():
    pass
```

**Classes:** `PascalCase`
```python
class HealthCheckScheduler:
    pass
```

**Constants:** `UPPER_SNAKE_CASE`
```python
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
```

**Private Methods:** Prefix with `_`
```python
def _internal_helper():
    pass
```

### Code Organization

**File Structure:**
```
app/
├── __init__.py          # Package init
├── app.py               # Application factory
├── models.py            # Database models
├── routes.py            # HTTP routes
├── health_checker.py    # Health check logic
├── scheduler.py         # Background scheduler
└── config.py            # Configuration
```

**Keep functions small:**
- Max 50 lines per function
- Single responsibility
- Clear purpose

**Avoid deep nesting:**
- Max 3-4 levels of indentation
- Use early returns
- Extract complex logic to functions

### Testing Standards

**Test Organization:**
```
tests/
├── conftest.py          # Fixtures
├── test_models.py       # Model tests
├── test_routes.py       # Route tests
└── test_health_checker.py
```

**Test Naming:**
```python
def test_create_endpoint_success():
    """Test successful endpoint creation"""
    pass

def test_create_endpoint_missing_url():
    """Test endpoint creation fails without URL"""
    pass
```

**Test Structure:**
```python
def test_something():
    # Arrange
    endpoint = create_test_endpoint()
    
    # Act
    result = check_endpoint_health(endpoint)
    
    # Assert
    assert result.status == 'success'
```

**Coverage Target:** 80%+ for new code

## Testing Guidelines

### Unit Tests

Test individual functions/methods:

```python
def test_endpoint_to_dict():
    """Test Endpoint.to_dict() method"""
    endpoint = Endpoint(
        name="Test",
        url="http://test.com",
        endpoint_type="REST"
    )
    result = endpoint.to_dict()
    assert result['name'] == "Test"
    assert result['url'] == "http://test.com"
```

### Integration Tests

Test multiple components together:

```python
def test_add_endpoint_flow(client):
    """Test complete add endpoint workflow"""
    response = client.post('/endpoints/add', data={
        'name': 'Test API',
        'url': 'http://api.example.com',
        'endpoint_type': 'REST'
    })
    assert response.status_code == 302
    
    endpoint = Endpoint.query.filter_by(name='Test API').first()
    assert endpoint is not None
```

### Mock External Services

Use `responses` or `unittest.mock`:

```python
import responses

@responses.activate
def test_health_check_success():
    """Test successful health check"""
    responses.add(
        responses.GET,
        'http://api.example.com/health',
        json={'status': 'ok'},
        status=200
    )
    
    result = check_endpoint_health(endpoint)
    assert result.status == 'success'
```

## Documentation Standards

### Code Comments

**When to comment:**
- Complex algorithms
- Non-obvious business logic
- Workarounds for bugs
- Performance optimizations

**When NOT to comment:**
- Obvious code
- Bad code (refactor instead)

**Good:**
```python
# SOAP requires explicit SOAPAction header per WS-I Basic Profile
headers['SOAPAction'] = endpoint.soap_action or ""
```

**Bad:**
```python
# Set the URL
url = endpoint.url
```

### Docstrings

All public functions, classes, and modules should have docstrings:

```python
def check_endpoint_health(endpoint):
    """
    Perform a health check on the specified endpoint.
    
    Sends an HTTP request to the endpoint and records the result,
    including response time, status code, and any errors.
    
    Args:
        endpoint: The Endpoint object to check
        
    Returns:
        HealthCheck: The result of the health check
        
    Raises:
        ValueError: If endpoint configuration is invalid
        
    Example:
        >>> endpoint = Endpoint.query.get(1)
        >>> result = check_endpoint_health(endpoint)
        >>> print(result.status)
        'success'
    """
    pass
```

### User Documentation

When adding features, update:

- User guide (if user-facing)
- API documentation (if API changes)
- Configuration guide (if new config options)

## Review Process

### What to Expect

1. **Automated Checks**
   - Tests run automatically
   - Code quality checks
   - Security scans

2. **Code Review**
   - Maintainer reviews code
   - Feedback provided
   - Changes requested (if needed)

3. **Approval and Merge**
   - PR approved
   - Merged to main branch
   - You're credited as contributor!

### Review Timeline

- Small PRs: 1-3 days
- Medium PRs: 3-7 days
- Large PRs: 1-2 weeks

## Common Issues

### Tests Failing

```bash
# Run tests locally first
pytest tests/ -v

# Check specific failure
pytest tests/test_routes.py::test_failing_test -vv
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
echo $PYTHONPATH
```

### Database Errors

```bash
# Reset test database
rm -f instance/test.db
pytest tests/ -v
```

## Questions?

- Check [existing issues](https://github.com/mgboyle/App-health-monitor/issues)
- Review [documentation](../index.md)
- Open a new issue with the `question` label

## Recognition

Contributors are listed in:
- GitHub contributors page
- Release notes
- CONTRIBUTORS.md file (if created)

Thank you for contributing to App Health Monitor! 🎉

## Next Steps

- [Development Setup](development-setup.md) - Detailed setup guide
- [Architecture](architecture.md) - System architecture
- [Testing](testing.md) - Testing guidelines
