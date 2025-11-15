"""
Configuration settings for the application
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///health_monitor.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Health check settings
    DEFAULT_CHECK_INTERVAL = int(os.environ.get('DEFAULT_CHECK_INTERVAL', '60'))
    DEFAULT_TIMEOUT = int(os.environ.get('DEFAULT_TIMEOUT', '30'))
    MAX_HEALTH_CHECK_HISTORY = int(os.environ.get('MAX_HEALTH_CHECK_HISTORY', '1000'))
    
    # Azure Key Vault settings (for mTLS certificates in production)
    AZURE_KEYVAULT_URL = os.environ.get('AZURE_KEYVAULT_URL', '')  # e.g., https://myvault.vault.azure.net/
    # Authentication for Key Vault uses Azure Managed Identity or DefaultAzureCredential
    # No explicit credentials needed when running in AKS with managed identity


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_health_monitor.db'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
