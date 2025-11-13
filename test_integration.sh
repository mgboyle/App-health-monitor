#!/bin/bash
# Quick Test Script for SOAP Endpoint Monitoring
# Run this script to perform a full integration test

set -e  # Exit on error

echo "🚀 Starting App Health Monitor Integration Test"
echo "================================================"

# Configuration
APP_URL="http://localhost:5001"
WSDL_URL="http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL"
OPERATION="CapitalCity"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if server is running
echo -e "\n${BLUE}Step 1: Checking if server is running...${NC}"
if curl -s "${APP_URL}/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server is running${NC}"
else
    echo -e "${RED}✗ Server is not running on ${APP_URL}${NC}"
    echo "Please start the server with: PORT=5001 python run.py"
    exit 1
fi

# Test WSDL Operations
echo -e "\n${BLUE}Step 2: Fetching WSDL operations...${NC}"
OPERATIONS=$(curl -s -X POST "${APP_URL}/api/wsdl/operations" \
    -H 'Content-Type: application/json' \
    -d "{\"wsdl_url\": \"${WSDL_URL}\"}")

if echo "$OPERATIONS" | grep -q "operations"; then
    echo -e "${GREEN}✓ Successfully fetched WSDL operations${NC}"
    OPERATION_COUNT=$(echo "$OPERATIONS" | grep -o '"name"' | wc -l | tr -d ' ')
    echo "  Found ${OPERATION_COUNT} operations"
else
    echo -e "${RED}✗ Failed to fetch WSDL operations${NC}"
    echo "$OPERATIONS"
    exit 1
fi

# Test Sample Payload Generation
echo -e "\n${BLUE}Step 3: Generating sample SOAP payload for ${OPERATION}...${NC}"
PAYLOAD=$(curl -s -X POST "${APP_URL}/api/wsdl/sample-payload" \
    -H 'Content-Type: application/json' \
    -d "{\"wsdl_url\": \"${WSDL_URL}\", \"operation_name\": \"${OPERATION}\"}")

if echo "$PAYLOAD" | grep -q "soap:Envelope"; then
    echo -e "${GREEN}✓ Successfully generated sample payload${NC}"
else
    echo -e "${RED}✗ Failed to generate sample payload${NC}"
    echo "$PAYLOAD"
    exit 1
fi

# Get Current Health Status
echo -e "\n${BLUE}Step 4: Checking current health status...${NC}"
HEALTH=$(curl -s "${APP_URL}/api/health")
if echo "$HEALTH" | grep -q "status"; then
    echo -e "${GREEN}✓ Successfully retrieved health status${NC}"
    ENDPOINT_COUNT=$(echo "$HEALTH" | grep -o '"name"' | wc -l | tr -d ' ')
    echo "  Monitoring ${ENDPOINT_COUNT} endpoints"
else
    echo -e "${RED}✗ Failed to retrieve health status${NC}"
    exit 1
fi

# List All Endpoints
echo -e "\n${BLUE}Step 5: Listing all configured endpoints...${NC}"
ENDPOINTS=$(curl -s "${APP_URL}/api/endpoints")
if echo "$ENDPOINTS" | grep -q '\['; then
    echo -e "${GREEN}✓ Successfully listed endpoints${NC}"
else
    echo -e "${RED}✗ Failed to list endpoints${NC}"
    exit 1
fi

# Summary
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✅ All integration tests passed!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Open your browser to ${APP_URL}"
echo "  2. Click 'Add Endpoint' to add a SOAP endpoint"
echo "  3. Use the WSDL URL: ${WSDL_URL}"
echo "  4. Select operation: ${OPERATION}"
echo "  5. Monitor the health checks on the dashboard"
echo ""
echo "Available operations to test:"
echo "$OPERATIONS" | python3 -m json.tool 2>/dev/null | grep '"name"' | head -10 | sed 's/.*"name": "\(.*\)".*/  - \1/'
echo "  ... and more"
echo ""
echo "To run manual health check:"
echo "  curl -X POST ${APP_URL}/endpoints/{endpoint_id}/check"
echo ""
