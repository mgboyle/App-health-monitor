#!/usr/bin/env python3
"""
Seed script to pre-configure sample SOAP endpoints
"""
from app.app import create_app
from app.models import db, Endpoint

def seed_sample_endpoints():
    """Add sample SOAP endpoints for testing"""
    app = create_app()
    
    with app.app_context():
        # Clear existing endpoints
        Endpoint.query.delete()
        
        # REST API Example - Open-Meteo Weather API with JSON validation
        weather_api = Endpoint(
            name='Open-Meteo Weather API (Toronto)',
            url='https://api.open-meteo.com/v1/forecast?latitude=43.7&longitude=-79.4&current_weather=true',
            endpoint_type='REST',
            soap_action=None,
            soap_payload=None,
            check_interval=180,
            timeout=15,
            enabled=True,
            validation_enabled=True,
            validation_type='contains',
            expected_content='"current_weather"'
        )
        
        # CountryInfo SOAP Service - CapitalCity operation with validation
        capital_city = Endpoint(
            name='CountryInfo - CapitalCity (US)',
            url='http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso',
            endpoint_type='SOAP',
            soap_action='',
            soap_payload='''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <CapitalCity xmlns="http://www.oorsprong.org/websamples.countryinfo">
      <sCountryISOCode>US</sCountryISOCode>
    </CapitalCity>
  </soap:Body>
</soap:Envelope>''',
            check_interval=300,
            timeout=30,
            enabled=True,
            validation_enabled=True,
            validation_type='contains',
            expected_content='Washington'
        )
        
        # CountryInfo SOAP Service - CountryName operation with regex validation
        country_name = Endpoint(
            name='CountryInfo - CountryName (GB)',
            url='http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso',
            endpoint_type='SOAP',
            soap_action='',
            soap_payload='''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <CountryName xmlns="http://www.oorsprong.org/websamples.countryinfo">
      <sCountryISOCode>GB</sCountryISOCode>
    </CountryName>
  </soap:Body>
</soap:Envelope>''',
            check_interval=300,
            timeout=30,
            enabled=True,
            validation_enabled=True,
            validation_type='regex',
            expected_content='United Kingdom|Great Britain'
        )
        
        # CountryInfo SOAP Service - ListOfCountryNamesByName with validation
        list_countries = Endpoint(
            name='CountryInfo - List Countries',
            url='http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso',
            endpoint_type='SOAP',
            soap_action='',
            soap_payload='''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <ListOfCountryNamesByName xmlns="http://www.oorsprong.org/websamples.countryinfo" />
  </soap:Body>
</soap:Envelope>''',
            check_interval=300,
            timeout=30,
            enabled=True,
            validation_enabled=True,
            validation_type='contains',
            expected_content='<tCountryCodeAndName>'
        )
        
        # Add all endpoints
        db.session.add(weather_api)
        db.session.add(capital_city)
        db.session.add(country_name)
        db.session.add(list_countries)
        
        # Commit to database
        db.session.commit()
        
        print("✅ Successfully seeded 4 sample endpoints with validation:")
        print("   1. Open-Meteo Weather API - REST (JSON validation)")
        print("   2. CountryInfo - CapitalCity - SOAP (contains 'Washington')")
        print("   3. CountryInfo - CountryName - SOAP (regex validation)")
        print("   4. CountryInfo - List Countries - SOAP (XML tag validation)")
        print("\n📋 Validation Types Demonstrated:")
        print("   • Contains: Simple string matching")
        print("   • Regex: Pattern matching with alternatives")
        print("\nYou can now test these endpoints at http://localhost:5001")

if __name__ == '__main__':
    seed_sample_endpoints()
