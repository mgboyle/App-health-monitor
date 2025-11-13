# Testing Guide for App Health Monitor

This guide explains how to use the VS Code tasks to test the SOAP endpoint monitoring functionality.

## Available VS Code Tasks

Access these tasks via `Terminal > Run Task...` or `Cmd+Shift+P` → "Tasks: Run Task"

### 1. Run Health Monitor App (Port 5001)
**Purpose**: Start the Flask application on port 5001 in the background.

**When to use**: Before running any tests, ensure the app is running.

---

### 2. Test SOAP - Fetch WSDL Operations
**Purpose**: Fetch all available operations from a WSDL endpoint.

**Example**: Tests against the CountryInfo web service to retrieve all SOAP operations.

**Expected Output**: JSON array of operations with their names and SOAP actions.

```json
{
  "operations": [
    {"name": "CapitalCity", "soap_action": ""},
    {"name": "CountryName", "soap_action": ""}
  ]
}
```

---

### 3. Test SOAP - Generate Sample Payload
**Purpose**: Generate a sample SOAP envelope for a specific operation.

**Example**: Generates a sample request for the "CapitalCity" operation.

**Expected Output**: XML SOAP envelope template.

```json
{
  "payload": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope>..."
}
```

---

### 4. Test SOAP - Add CountryInfo Endpoint
**Purpose**: Add a pre-configured CountryInfo SOAP endpoint to the monitor.

**What it does**:
- Adds a SOAP endpoint for the CapitalCity operation
- Configures it to check the capital city of the US
- Sets check interval to 5 minutes (300 seconds)

**Expected Output**: Redirects to the dashboard with the new endpoint added.

---

### 5. Test SOAP - Check Endpoint Health
**Purpose**: Manually trigger a health check for a specific endpoint.

**How to use**: Enter the endpoint ID when prompted (usually 1 for the first endpoint).

**Expected Output**: Triggers a health check and redirects to the dashboard.

---

### 6. Test API - Get Health Status
**Purpose**: Fetch the overall health status of all monitored endpoints.

**Expected Output**: JSON with status of all endpoints, response times, and error messages.

```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T10:00:00",
  "endpoints": [...]
}
```

---

### 7. Test API - List All Endpoints
**Purpose**: List all configured endpoints in the system.

**Expected Output**: JSON array of all endpoints with their configurations.

---

### 8. Test SOAP - Full Integration Test
**Purpose**: Run a complete integration test of the SOAP functionality.

**What it does**:
1. Fetches WSDL operations
2. Generates sample payload
3. Gets overall health status

**When to use**: After adding new SOAP features to verify end-to-end functionality.

---

### 9. Run All Tests (pytest)
**Purpose**: Run the full pytest test suite.

**When to use**: Before committing code to ensure all tests pass.

---

### 10. Debug SOAP WSDL Fetch
**Purpose**: Debug the WSDL fetching mechanism directly.

**What it shows**:
- Whether the WSDL was successfully fetched
- Length of the WSDL content
- First 500 characters for inspection

**When to use**: Troubleshooting WSDL fetch failures or security restrictions.

---

## Quick Testing Workflow

### Testing New SOAP Endpoint Support

1. **Start the app**:
   - Run task: "Run Health Monitor App (Port 5001)"
   - Wait for "Running on http://127.0.0.1:5001" message

2. **Test WSDL parsing**:
   - Run task: "Test SOAP - Fetch WSDL Operations"
   - Verify operations are returned

3. **Test payload generation**:
   - Run task: "Test SOAP - Generate Sample Payload"
   - Verify SOAP envelope is generated

4. **Add endpoint and test**:
   - Run task: "Test SOAP - Add CountryInfo Endpoint"
   - Run task: "Test SOAP - Check Endpoint Health" (enter ID: 1)
   - Check dashboard at http://localhost:5001

5. **Verify integration**:
   - Run task: "Test SOAP - Full Integration Test"
   - All three steps should complete successfully

### Testing CountryInfo WSDL Specifically

The tasks are pre-configured to test against:
```
http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL
```

**Available Operations**:
- `CapitalCity` - Get capital city of a country
- `CountryName` - Get country name by ISO code
- `ListOfCountryNamesByName` - List all countries
- `FullCountryInfo` - Get complete country information
- And many more (see Task #2 for full list)

**Sample SOAP Request for CapitalCity**:
```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <CapitalCity xmlns="http://www.oorsprong.org/websamples.countryinfo">
      <sCountryISOCode>US</sCountryISOCode>
    </CapitalCity>
  </soap:Body>
</soap:Envelope>
```

**Expected Response**:
```xml
<CapitalCityResult>Washington</CapitalCityResult>
```

---

## Common Issues and Troubleshooting

### Issue: "Connection refused" on port 5001

**Solution**: Run task "Run Health Monitor App (Port 5001)" first.

---

### Issue: "Failed to fetch WSDL"

**Possible causes**:
1. WSDL URL is not accessible (check network connection)
2. URL points to private/internal IP (security restriction)
3. Response is too large (>5MB limit)

**Debug**: Run task "Debug SOAP WSDL Fetch" to see detailed error.

---

### Issue: 500 error when testing SOAP endpoint

**Check**:
1. Is the SOAP payload valid XML?
2. Does the operation exist in the WSDL?
3. Are the namespaces correct?
4. Check `/tmp/health-monitor.log` for detailed errors

---

### Issue: No operations found in WSDL

**Possible causes**:
1. WSDL uses non-standard namespaces
2. WSDL is in WSDL 2.0 format (currently only WSDL 1.1 supported)

**Debug**: 
- Run "Debug SOAP WSDL Fetch" 
- Manually inspect the WSDL XML structure

---

## Manual Testing with curl

If you prefer manual testing:

```bash
# Fetch operations
curl -X POST http://localhost:5001/api/wsdl/operations \
  -H 'Content-Type: application/json' \
  -d '{"wsdl_url": "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL"}'

# Generate sample payload
curl -X POST http://localhost:5001/api/wsdl/sample-payload \
  -H 'Content-Type: application/json' \
  -d '{"wsdl_url": "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL", "operation_name": "CapitalCity"}'

# Get health status
curl http://localhost:5001/api/health

# Manually check endpoint (replace {id} with endpoint ID)
curl -X POST http://localhost:5001/endpoints/{id}/check -L
```

---

## Adding Your Own SOAP Endpoints for Testing

### Method 1: Via Web UI
1. Navigate to http://localhost:5001
2. Click "Add Endpoint"
3. Fill in the form:
   - **Name**: Descriptive name
   - **URL**: SOAP endpoint URL
   - **Type**: Select "SOAP"
   - **WSDL URL**: Paste WSDL URL
   - Select operation from dropdown
   - Edit the generated payload if needed
   - Set check interval and timeout
4. Click "Add Endpoint"

### Method 2: Via API
```bash
curl -X POST http://localhost:5001/endpoints/add \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'name=My SOAP Service' \
  --data-urlencode 'url=https://example.com/soap' \
  --data-urlencode 'endpoint_type=SOAP' \
  --data-urlencode 'soap_action=http://example.com/MyOperation' \
  --data-urlencode 'soap_payload=<soap:Envelope>...</soap:Envelope>' \
  --data-urlencode 'check_interval=60' \
  --data-urlencode 'timeout=30' \
  --data-urlencode 'enabled=on'
```

---

## Security Notes

The WSDL parser includes security restrictions to prevent:
- **SSRF attacks**: Blocks localhost, private IPs, and link-local addresses
- **XXE attacks**: Uses `defusedxml` for secure XML parsing
- **DoS attacks**: Limits response size to 5MB
- **Redirect attacks**: Disables redirects during WSDL fetch

These are intentional security features. If you need to test against localhost SOAP services, you'll need to temporarily modify the security restrictions in `app/soap_utils.py`.

---

## Running Tests in CI/CD

The pytest suite includes tests for:
- WSDL parsing
- SOAP payload generation
- Endpoint health checking
- Database models

Run in your CI pipeline:
```bash
source venv/bin/activate
pytest tests/ -v --cov=app --cov-report=html
```

---

## Next Steps

After testing SOAP endpoints:
1. Monitor the logs at http://localhost:5001/logs
2. Check response times and success rates
3. Adjust check intervals based on your needs
4. Set up alerts for failures (future feature)
5. Export health data for external monitoring (future feature)

---

**Happy Testing! 🧪**
