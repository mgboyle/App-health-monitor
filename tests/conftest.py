"""
Pytest configuration and fixtures
"""
import pytest
from app.app import create_app
from app.models import db as _db


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = create_app('testing')
    
    # Stop the scheduler during tests
    if hasattr(app, 'scheduler'):
        app.scheduler.shutdown()
    
    yield app


@pytest.fixture(scope='function')
def db(app):
    """Create database for the tests."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Create a test client for the app."""
    return app.test_client()
