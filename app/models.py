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
    
    # Response validation fields
    validation_enabled = db.Column(db.Boolean, default=False)  # Enable response validation
    validation_type = db.Column(db.String(20), nullable=True)  # contains, equals, regex, json_path
    expected_content = db.Column(db.Text, nullable=True)  # Expected content to validate
    
    # Authentication fields
    auth_type = db.Column(db.String(20), nullable=True)  # None, Basic, Windows, Kerberos, OAuth, mTLS
    auth_username = db.Column(db.String(200), nullable=True)  # For Basic auth
    auth_password = db.Column(db.String(200), nullable=True)  # For Basic auth (should be encrypted in production)
    
    # mTLS certificate fields
    mtls_enabled = db.Column(db.Boolean, default=False)  # Enable mTLS authentication
    mtls_cert_source = db.Column(db.String(20), nullable=True)  # 'keyvault' or 'file'
    mtls_cert_path = db.Column(db.String(500), nullable=True)  # Local file path for cert (for testing)
    mtls_key_path = db.Column(db.String(500), nullable=True)  # Local file path for private key (for testing)
    mtls_keyvault_cert_name = db.Column(db.String(200), nullable=True)  # Azure Key Vault certificate name
    
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
            'validation_enabled': self.validation_enabled,
            'validation_type': self.validation_type,
            'expected_content': self.expected_content,
            'auth_type': self.auth_type,
            'auth_username': self.auth_username,
            'mtls_enabled': self.mtls_enabled,
            'mtls_cert_source': self.mtls_cert_source,
            'mtls_cert_path': self.mtls_cert_path,
            'mtls_key_path': self.mtls_key_path,
            'mtls_keyvault_cert_name': self.mtls_keyvault_cert_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class HealthCheck(db.Model):
    """Model for storing health check results"""
    __tablename__ = 'health_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('endpoints.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # success, failure, timeout, validation_failed
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # in milliseconds
    error_message = db.Column(db.Text)
    validation_error = db.Column(db.Text)  # Specific validation failure message
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
            'validation_error': self.validation_error,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None
        }
