# Using the Dashboard

The App Health Monitor dashboard provides a real-time view of all your monitored endpoints with their current health status, performance metrics, and historical data.

## Dashboard Overview

The dashboard is the main interface of the application, accessible at `http://localhost:5000/`.

### Main Components

1. **Navigation Bar** - Access different sections of the application
2. **Endpoint Cards** - Visual representation of each monitored endpoint
3. **Quick Actions** - Add, edit, delete, and check endpoints
4. **Status Indicators** - Visual health status indicators

## Endpoint Cards

Each endpoint is displayed as a card showing:

### Status Information

- **Name** - The friendly name you assigned
- **URL** - The endpoint being monitored
- **Type** - REST, SOAP, WCF, or GraphQL
- **Status Badge** - Visual indicator of current health:
  - 🟢 **Healthy** - Last check was successful (HTTP 2xx)
  - 🔴 **Failed** - Last check failed (HTTP 4xx, 5xx)
  - 🟡 **Timeout** - Request timed out
  - ⚠️ **Validation Failed** - Response validation failed
  - ⚪ **Not Checked Yet** - No health checks performed

### Performance Metrics

- **Response Time** - Latest response time in milliseconds
- **Status Code** - HTTP status code from the last check
- **Last Checked** - Timestamp of the most recent health check
- **Error Message** - Displayed if the check failed

### Statistics (Available in Logs View)

- **Uptime %** - Percentage of successful checks
- **Total Checks** - Number of health checks performed
- **Success Count** - Number of successful checks
- **Average Response Time** - Mean response time across all checks

## Quick Actions

### Add Endpoint

Click the **"Add Endpoint"** button to create a new monitored endpoint.

**Required Fields:**
- Name
- URL
- Type (REST, SOAP, WCF, GraphQL)

**Optional Fields:**
- Check Interval (default: 60 seconds)
- Timeout (default: 30 seconds)
- Authentication settings
- Response validation rules

See [Managing Endpoints](managing-endpoints.md) for detailed information.

### Manual Check

Click **"Check Now"** on any endpoint card to immediately trigger a health check without waiting for the scheduled interval.

Use cases:
- Verify a fix after an outage
- Test a newly added endpoint
- Get immediate status update

### Edit Endpoint

Click **"Edit"** to modify endpoint configuration:

- Change check interval
- Update URL or authentication
- Enable/disable the endpoint
- Modify validation rules

### Delete Endpoint

Click **"Delete"** to remove an endpoint. This will:

- Stop scheduled health checks
- Remove the endpoint from the dashboard
- Delete all associated health check history

!!! warning "Deletion is Permanent"
    Deleting an endpoint removes all historical data. This action cannot be undone.

### View Logs

Click **"View Logs"** to see the health check history for a specific endpoint.

Logs include:
- Timestamp of each check
- Status and status code
- Response time
- Error messages
- Validation results

## Dashboard Features

### Auto Refresh

The dashboard automatically updates the health status of endpoints as checks are performed in the background.

Refresh interval: Based on individual endpoint check intervals

### Color-Coded Status

Quick visual identification of endpoint health:

| Color | Status | Meaning |
|-------|--------|---------|
| Green | ✅ Healthy | Endpoint is responding successfully |
| Red | ❌ Failed | Endpoint returned an error |
| Yellow | ⏱️ Timeout | Request exceeded timeout threshold |
| Orange | ⚠️ Validation Failed | Response received but validation failed |
| Gray | ⚪ Pending | No checks performed yet |

### Responsive Design

The dashboard is mobile-friendly and adapts to different screen sizes:

- **Desktop** - Multi-column grid layout
- **Tablet** - Two-column layout
- **Mobile** - Single-column layout

## Navigation

### Main Menu

- **Dashboard** (/) - Main endpoint overview
- **Add Endpoint** (/endpoints/add) - Create new endpoint
- **All Logs** (/logs) - View all health check logs
- **API** (/api/health) - JSON API endpoint

### Breadcrumbs

Navigate back to previous pages using breadcrumb navigation at the top of each page.

## Keyboard Shortcuts

Speed up your workflow with keyboard shortcuts:

| Shortcut | Action |
|----------|--------|
| `A` | Add new endpoint |
| `L` | View all logs |
| `R` | Refresh dashboard |
| `?` | Show help |

!!! note "Future Feature"
    Keyboard shortcuts are planned for a future release.

## Dashboard Customization

### Sorting

Endpoints can be sorted by:
- Name (alphabetical)
- Status (healthy first or failed first)
- Last checked (most recent first)
- Response time (fastest first)

!!! note "Future Feature"
    Custom sorting is planned for a future release. Currently, endpoints are displayed in creation order.

### Filtering

Filter endpoints by:
- Type (REST, SOAP, WCF, GraphQL)
- Status (Healthy, Failed, Timeout)
- Tags (when implemented)

!!! note "Future Feature"
    Filtering is planned for a future release.

## Best Practices

### 1. Use Descriptive Names

Give endpoints clear, descriptive names:

✅ Good:
- "Production API - User Service"
- "Staging - Payment Gateway"
- "Legacy SOAP - Order Processing"

❌ Avoid:
- "API 1"
- "Test"
- "Endpoint"

### 2. Organize by Environment

Prefix endpoint names with the environment:

- `[PROD] Customer API`
- `[STAGE] Payment Service`
- `[DEV] Authentication`

### 3. Set Appropriate Check Intervals

- **Critical production endpoints**: 30-60 seconds
- **Standard endpoints**: 5 minutes
- **Non-critical or slow endpoints**: 15-30 minutes

### 4. Use Validation

Enable response validation to catch issues beyond HTTP status codes:

- Validate critical response fields
- Check for expected content
- Ensure JSON structure is correct

### 5. Monitor the Dashboard Regularly

- Check daily for any red/yellow indicators
- Review error messages for failed checks
- Adjust check intervals based on usage patterns

## Troubleshooting

### Endpoint Stuck on "Pending"

**Causes:**
- Scheduler not running
- Endpoint is disabled
- Check interval is very long

**Solutions:**
1. Check that the application is running
2. Verify endpoint is enabled (Edit > Enable checkbox)
3. Manually trigger a check with "Check Now"
4. Check application logs for errors

### Dashboard Not Updating

**Causes:**
- Browser cache
- JavaScript errors
- Network issues

**Solutions:**
1. Hard refresh (Ctrl+F5 or Cmd+Shift+R)
2. Clear browser cache
3. Check browser console for errors
4. Try a different browser

### Wrong Status Displayed

**Causes:**
- Recent configuration change
- Manual check overriding scheduled check
- Validation rules changed

**Solutions:**
1. Wait for next scheduled check
2. Trigger a manual check
3. Review validation rules in endpoint settings

### Performance Issues

**Causes:**
- Too many endpoints
- Very short check intervals
- Slow monitored endpoints

**Solutions:**
1. Increase check intervals
2. Disable non-critical endpoints
3. Increase timeout values
4. Use more powerful server hardware

## Next Steps

- [Managing Endpoints](managing-endpoints.md) - Learn about endpoint configuration
- [Viewing Logs](logs.md) - Deep dive into health check history
- [API Reference](../api/rest-api.md) - Programmatic access to health data
