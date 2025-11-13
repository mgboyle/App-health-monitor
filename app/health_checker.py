"""
Health checker service for monitoring endpoints
"""
import requests
import time
import re
import json
from datetime import datetime
from app.models import db, Endpoint, HealthCheck
from requests_kerberos import HTTPKerberosAuth, OPTIONAL


class HealthChecker:
    """Service to perform health checks on endpoints"""
    
    @staticmethod
    def validate_response_content(response, endpoint):
        """
        Validate response content based on endpoint configuration
        
        Args:
            response: requests.Response object
            endpoint: Endpoint model instance
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not endpoint.validation_enabled or not endpoint.expected_content:
            return True, None
        
        try:
            response_text = response.text
            expected = endpoint.expected_content
            validation_type = endpoint.validation_type or 'contains'
            
            if validation_type == 'contains':
                if expected in response_text:
                    return True, None
                else:
                    return False, f"Response does not contain expected text: '{expected[:100]}'"
            
            elif validation_type == 'equals':
                if response_text.strip() == expected.strip():
                    return True, None
                else:
                    return False, f"Response does not equal expected content. Got: '{response_text[:100]}...'"
            
            elif validation_type == 'regex':
                if re.search(expected, response_text):
                    return True, None
                else:
                    return False, f"Response does not match regex pattern: '{expected}'"
            
            elif validation_type == 'json_path':
                # Simple JSON path validation (e.g., "status=ok" or "data.user.name")
                try:
                    response_json = response.json()
                    
                    # Handle simple equality check like "status=ok"
                    if '=' in expected:
                        path, value = expected.split('=', 1)
                        path = path.strip()
                        value = value.strip()
                        
                        # Navigate JSON path
                        current = response_json
                        for key in path.split('.'):
                            if isinstance(current, dict) and key in current:
                                current = current[key]
                            else:
                                return False, f"JSON path '{path}' not found in response"
                        
                        # Compare values (handle different types)
                        current_str = str(current).strip('"\'')
                        value_str = value.strip('"\'')
                        
                        if current_str == value_str:
                            return True, None
                        else:
                            return False, f"JSON path '{path}' has value '{current_str}', expected '{value_str}'"
                    else:
                        # Just check if path exists
                        current = response_json
                        for key in expected.split('.'):
                            if isinstance(current, dict) and key in current:
                                current = current[key]
                            else:
                                return False, f"JSON path '{expected}' not found in response"
                        return True, None
                        
                except json.JSONDecodeError:
                    return False, "Response is not valid JSON"
            
            else:
                return False, f"Unknown validation type: {validation_type}"
                
        except Exception as e:
            return False, f"Validation error: {str(e)[:200]}"
    
    @staticmethod
    def get_auth_config(endpoint):
        """
        Get authentication configuration for endpoint
        
        Args:
            endpoint: Endpoint model instance
            
        Returns:
            dict: Authentication configuration for requests
        """
        auth_config = {}
        
        if endpoint.auth_type == 'basic' and endpoint.auth_username:
            from requests.auth import HTTPBasicAuth
            auth_config['auth'] = HTTPBasicAuth(
                endpoint.auth_username,
                endpoint.auth_password or ''
            )
        elif endpoint.auth_type == 'kerberos':
            # Kerberos uses default system credentials (current user's ticket)
            # No username/password needed
            auth_config['auth'] = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
        
        return auth_config
    
    @staticmethod
    def check_endpoint(endpoint):
        """
        Perform a health check on a single endpoint
        
        Args:
            endpoint: Endpoint model instance
            
        Returns:
            HealthCheck model instance
        """
        health_check = HealthCheck(endpoint_id=endpoint.id)
        
        try:
            start_time = time.time()
            
            # Get authentication configuration
            auth_config = HealthChecker.get_auth_config(endpoint)
            
            # Handle SOAP endpoints differently
            if endpoint.endpoint_type == 'SOAP' and endpoint.soap_payload:
                headers = {
                    'Content-Type': 'text/xml; charset=utf-8'
                }
                
                # Add SOAPAction header if specified
                if endpoint.soap_action:
                    headers['SOAPAction'] = endpoint.soap_action
                
                response = requests.post(
                    endpoint.url,
                    data=endpoint.soap_payload,
                    headers=headers,
                    timeout=endpoint.timeout,
                    allow_redirects=True,
                    **auth_config
                )
            else:
                # Default to GET request for REST and other types
                response = requests.get(
                    endpoint.url,
                    timeout=endpoint.timeout,
                    allow_redirects=True,
                    **auth_config
                )
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            health_check.status_code = response.status_code
            health_check.response_time = round(response_time, 2)
            
            # Consider 2xx and 3xx as success
            if 200 <= response.status_code < 400:
                # Validate response content if enabled
                is_valid, validation_error = HealthChecker.validate_response_content(response, endpoint)
                
                if is_valid:
                    health_check.status = 'success'
                else:
                    health_check.status = 'validation_failed'
                    health_check.validation_error = validation_error
                    health_check.error_message = 'Content validation failed'
            else:
                health_check.status = 'failure'
                health_check.error_message = f'HTTP {response.status_code}'
                
        except requests.exceptions.Timeout:
            health_check.status = 'timeout'
            health_check.error_message = f'Request timeout after {endpoint.timeout} seconds'
            
        except requests.exceptions.ConnectionError as e:
            health_check.status = 'failure'
            health_check.error_message = f'Connection error: {str(e)[:200]}'
            
        except Exception as e:
            health_check.status = 'failure'
            health_check.error_message = f'Error: {str(e)[:200]}'
        
        health_check.checked_at = datetime.utcnow()
        return health_check
    
    @staticmethod
    def check_all_endpoints(app):
        """
        Check all enabled endpoints and save results to database
        
        Args:
            app: Flask application instance
        """
        with app.app_context():
            endpoints = Endpoint.query.filter_by(enabled=True).all()
            
            for endpoint in endpoints:
                health_check = HealthChecker.check_endpoint(endpoint)
                db.session.add(health_check)
            
            # Commit all health checks at once
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error saving health checks: {e}")
    
    @staticmethod
    def get_latest_status(endpoint_id):
        """
        Get the latest health check status for an endpoint
        
        Args:
            endpoint_id: ID of the endpoint
            
        Returns:
            Latest HealthCheck instance or None
        """
        return HealthCheck.query.filter_by(
            endpoint_id=endpoint_id
        ).order_by(
            HealthCheck.checked_at.desc()
        ).first()
