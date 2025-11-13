"""
SOAP/WSDL utilities for parsing and generating SOAP requests
"""
import requests
from xml.etree import ElementTree as ET
from typing import Dict, List, Optional
from defusedxml.ElementTree import fromstring


class WSDLParser:
    """Parser for WSDL files to extract operations and generate sample payloads"""
    
    SOAP_NAMESPACES = {
        'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
        'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
        'soap12': 'http://schemas.xmlsoap.org/wsdl/soap12/',
        'xsd': 'http://www.w3.org/2001/XMLSchema',
        's': 'http://www.w3.org/2003/05/soap-envelope'
    }
    
    # Allowed URL schemes for WSDL fetching
    ALLOWED_SCHEMES = ['http', 'https']
    
    # Maximum response size (5 MB)
    MAX_RESPONSE_SIZE = 5 * 1024 * 1024
    
    @staticmethod
    def fetch_wsdl(wsdl_url: str, timeout: int = 30) -> Optional[str]:
        """
        Fetch WSDL content from URL with security restrictions
        
        Args:
            wsdl_url: URL to the WSDL file
            timeout: Request timeout in seconds
            
        Returns:
            WSDL content as string or None if failed
        """
        try:
            # Validate URL scheme to prevent SSRF
            from urllib.parse import urlparse
            parsed_url = urlparse(wsdl_url)
            if parsed_url.scheme not in WSDLParser.ALLOWED_SCHEMES:
                print(f"Invalid URL scheme: {parsed_url.scheme}")
                return None
            
            # Prevent access to internal/private networks
            if parsed_url.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
                print("Access to localhost is not allowed")
                return None
            
            response = requests.get(
                wsdl_url, 
                timeout=timeout,
                stream=True,
                allow_redirects=False  # Prevent redirect-based SSRF
            )
            response.raise_for_status()
            
            # Check content size to prevent memory exhaustion
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > WSDLParser.MAX_RESPONSE_SIZE:
                print(f"Response too large: {content_length} bytes")
                return None
            
            # Read with size limit
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > WSDLParser.MAX_RESPONSE_SIZE:
                    print("Response exceeded maximum size")
                    return None
            
            return content.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error fetching WSDL: {e}")
            return None
    
    @staticmethod
    def parse_operations(wsdl_content: str) -> List[Dict[str, str]]:
        """
        Parse WSDL to extract available operations/methods using secure XML parsing
        
        Args:
            wsdl_content: WSDL XML content as string
            
        Returns:
            List of dictionaries containing operation details
        """
        operations = []
        
        try:
            # Use defusedxml to prevent XML bomb attacks
            root = fromstring(wsdl_content)
            
            # Try to find operations in WSDL 1.1 format
            for operation in root.findall('.//wsdl:operation', WSDLParser.SOAP_NAMESPACES):
                name = operation.get('name')
                if name:
                    # Try to find SOAP action
                    soap_operation = operation.find('.//soap:operation', WSDLParser.SOAP_NAMESPACES)
                    soap_action = ''
                    if soap_operation is not None:
                        soap_action = soap_operation.get('soapAction', '')
                    
                    operations.append({
                        'name': name,
                        'soap_action': soap_action
                    })
            
            # If no operations found, try alternative namespaces
            if not operations:
                for operation in root.findall('.//{http://schemas.xmlsoap.org/wsdl/}operation'):
                    name = operation.get('name')
                    if name:
                        operations.append({
                            'name': name,
                            'soap_action': ''
                        })
            
        except Exception as e:
            print(f"Error parsing WSDL operations: {e}")
        
        return operations
    
    @staticmethod
    def generate_sample_payload(wsdl_content: str, operation_name: str) -> str:
        """
        Generate a sample SOAP request payload for an operation using secure XML parsing
        
        Args:
            wsdl_content: WSDL XML content as string
            operation_name: Name of the operation
            
        Returns:
            Sample SOAP XML request as string
        """
        # Basic SOAP envelope template
        template = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <{operation_name} xmlns="http://tempuri.org/">
      <!-- Add your parameters here -->
    </{operation_name}>
  </soap:Body>
</soap:Envelope>'''
        
        try:
            # Use defusedxml to prevent XML bomb attacks
            root = fromstring(wsdl_content)
            
            # Try to find message schema for the operation
            # This is a simplified version - full WSDL parsing is complex
            for message in root.findall('.//wsdl:message', WSDLParser.SOAP_NAMESPACES):
                if operation_name in message.get('name', ''):
                    # Found the message, try to extract parts
                    parts = []
                    for part in message.findall('.//wsdl:part', WSDLParser.SOAP_NAMESPACES):
                        part_name = part.get('name')
                        part_type = part.get('type', 'string')
                        if part_name:
                            parts.append(f'      <{part_name}>?</{part_name}>')
                    
                    if parts:
                        template = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <{operation_name} xmlns="http://tempuri.org/">
{chr(10).join(parts)}
    </{operation_name}>
  </soap:Body>
</soap:Envelope>'''
        
        except Exception as e:
            print(f"Error generating sample payload: {e}")
        
        return template
