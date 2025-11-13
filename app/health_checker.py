"""
Health checker service for monitoring endpoints
"""
import requests
import time
from datetime import datetime
from app.models import db, Endpoint, HealthCheck


class HealthChecker:
    """Service to perform health checks on endpoints"""
    
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
                    allow_redirects=True
                )
            else:
                # Default to GET request for REST and other types
                response = requests.get(
                    endpoint.url,
                    timeout=endpoint.timeout,
                    allow_redirects=True
                )
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            health_check.status_code = response.status_code
            health_check.response_time = round(response_time, 2)
            
            # Consider 2xx and 3xx as success
            if 200 <= response.status_code < 400:
                health_check.status = 'success'
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
