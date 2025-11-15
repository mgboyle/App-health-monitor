"""
Certificate utilities for mTLS authentication
Supports both Azure Key Vault and local file-based certificates
"""
import os
import tempfile
from typing import Optional, Tuple


class CertificateManager:
    """Manages certificate loading for mTLS authentication"""
    
    def __init__(self, keyvault_url: Optional[str] = None):
        """
        Initialize certificate manager
        
        Args:
            keyvault_url: Azure Key Vault URL (optional, defaults to config)
        """
        self.keyvault_url = keyvault_url
        self._keyvault_client = None
    
    def _get_keyvault_client(self):
        """
        Get or create Azure Key Vault client
        Uses DefaultAzureCredential which automatically handles:
        - Managed Identity (in AKS)
        - Azure CLI credentials (local development)
        - Environment variables
        
        Returns:
            CertificateClient instance
        """
        if self._keyvault_client is None:
            from azure.keyvault.certificates import CertificateClient
            from azure.identity import DefaultAzureCredential
            
            if not self.keyvault_url:
                raise ValueError("Azure Key Vault URL not configured")
            
            credential = DefaultAzureCredential()
            self._keyvault_client = CertificateClient(
                vault_url=self.keyvault_url,
                credential=credential
            )
        
        return self._keyvault_client
    
    def get_certificate_from_keyvault(self, cert_name: str) -> Tuple[str, str]:
        """
        Retrieve certificate and private key from Azure Key Vault
        
        Args:
            cert_name: Name of the certificate in Key Vault
            
        Returns:
            Tuple of (cert_file_path, key_file_path)
            These are temporary files that should be cleaned up by the caller
            
        Raises:
            Exception if certificate cannot be retrieved
        """
        try:
            client = self._get_keyvault_client()
            
            # Get the certificate (includes both public cert and private key)
            certificate = client.get_certificate(cert_name)
            
            # Download the secret version which contains the private key
            # The certificate's secret_id points to the version with the private key
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            
            secret_client = SecretClient(
                vault_url=self.keyvault_url,
                credential=DefaultAzureCredential()
            )
            
            # Extract secret name from the certificate's secret_id
            # Format: https://{vault}.vault.azure.net/secrets/{name}/{version}
            secret_id = certificate.secret_id
            secret_name = secret_id.split('/')[-2]
            
            # Get the secret which contains the certificate with private key in PKCS12 format
            secret = secret_client.get_secret(secret_name)
            
            # The secret value is base64-encoded PKCS12
            import base64
            pkcs12_data = base64.b64decode(secret.value)
            
            # Extract certificate and key from PKCS12
            from cryptography.hazmat.primitives.serialization import pkcs12
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            
            # Load PKCS12 (assume no password for simplicity, can be enhanced)
            private_key, cert, additional_certs = pkcs12.load_key_and_certificates(
                pkcs12_data,
                password=None,
                backend=default_backend()
            )
            
            # Create temporary files for cert and key
            cert_fd, cert_path = tempfile.mkstemp(suffix='.pem', prefix='cert_')
            key_fd, key_path = tempfile.mkstemp(suffix='.pem', prefix='key_')
            
            try:
                # Write certificate to file
                with os.fdopen(cert_fd, 'wb') as cert_file:
                    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
                    cert_file.write(cert_pem)
                    
                    # Include intermediate certificates if present
                    if additional_certs:
                        for additional_cert in additional_certs:
                            additional_pem = additional_cert.public_bytes(serialization.Encoding.PEM)
                            cert_file.write(additional_pem)
                
                # Write private key to file
                with os.fdopen(key_fd, 'wb') as key_file:
                    key_pem = private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                    key_file.write(key_pem)
                
                return cert_path, key_path
                
            except Exception as e:
                # Clean up temp files on error
                try:
                    os.unlink(cert_path)
                except:
                    pass
                try:
                    os.unlink(key_path)
                except:
                    pass
                raise e
                
        except Exception as e:
            raise Exception(f"Failed to retrieve certificate from Key Vault: {str(e)}")
    
    def get_certificate_from_files(self, cert_path: str, key_path: str) -> Tuple[str, str]:
        """
        Validate and return local certificate file paths
        
        Args:
            cert_path: Path to certificate file
            key_path: Path to private key file
            
        Returns:
            Tuple of (cert_path, key_path)
            
        Raises:
            FileNotFoundError if files don't exist
        """
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"Certificate file not found: {cert_path}")
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Private key file not found: {key_path}")
        
        return cert_path, key_path
    
    def get_certificate(self, endpoint) -> Optional[Tuple[str, str]]:
        """
        Get certificate based on endpoint configuration
        
        Args:
            endpoint: Endpoint model instance with mTLS configuration
            
        Returns:
            Tuple of (cert_path, key_path) or None if mTLS not enabled
            For Key Vault certificates, returns temporary files that should be cleaned up
            
        Raises:
            Exception if certificate cannot be loaded
        """
        if not endpoint.mtls_enabled:
            return None
        
        cert_source = endpoint.mtls_cert_source or 'file'
        
        if cert_source == 'keyvault':
            if not endpoint.mtls_keyvault_cert_name:
                raise ValueError("Key Vault certificate name not specified")
            
            return self.get_certificate_from_keyvault(endpoint.mtls_keyvault_cert_name)
        
        elif cert_source == 'file':
            if not endpoint.mtls_cert_path or not endpoint.mtls_key_path:
                raise ValueError("Certificate or key file path not specified")
            
            return self.get_certificate_from_files(
                endpoint.mtls_cert_path,
                endpoint.mtls_key_path
            )
        
        else:
            raise ValueError(f"Unknown certificate source: {cert_source}")
    
    @staticmethod
    def cleanup_temp_files(*file_paths):
        """
        Clean up temporary certificate files
        
        Args:
            *file_paths: Variable number of file paths to delete
        """
        for path in file_paths:
            if path and path.startswith(tempfile.gettempdir()):
                try:
                    os.unlink(path)
                except Exception:
                    pass  # Ignore errors during cleanup
