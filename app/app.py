"""
Main Flask application factory
"""
from flask import Flask
from app.models import db
from app.config import config
from app.scheduler import HealthCheckScheduler
import os


def create_app(config_name=None):
    """
    Application factory for creating Flask app instances
    
    Args:
        config_name: Configuration to use (development, production, testing)
        
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Initialize and start scheduler
    scheduler = HealthCheckScheduler(app)
    scheduler.start()
    
    # Store scheduler in app for cleanup
    app.scheduler = scheduler
    
    return app
