"""
Database models for the health monitor application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Endpoint(db.Model):
    """Model for storing endpoint information"""
    __tablename__ = 'endpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    endpoint_type = db.Column(db.String(50), nullable=False, default='REST')  # REST, SOAP, or GraphQL
    check_interval = db.Column(db.Integer, default=60)  # seconds
    timeout = db.Column(db.Integer, default=30)  # seconds
    enabled = db.Column(db.Boolean, default=True)
    
    # SOAP-specific fields
    soap_action = db.Column(db.String(500), nullable=True)  # SOAP action/method name
    soap_payload = db.Column(db.Text, nullable=True)  # Sample SOAP request payload
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    health_checks = db.relationship('HealthCheck', backref='endpoint', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert endpoint to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'endpoint_type': self.endpoint_type,
            'check_interval': self.check_interval,
            'timeout': self.timeout,
            'enabled': self.enabled,
            'soap_action': self.soap_action,
            'soap_payload': self.soap_payload,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class HealthCheck(db.Model):
    """Model for storing health check results"""
    __tablename__ = 'health_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('endpoints.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # success, failure, timeout
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # in milliseconds
    error_message = db.Column(db.Text)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert health check to dictionary"""
        return {
            'id': self.id,
            'endpoint_id': self.endpoint_id,
            'status': self.status,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'error_message': self.error_message,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None
        }
