# Viewing Logs

App Health Monitor maintains a complete history of all health checks performed. This guide explains how to view, analyze, and use the logging features.

## Accessing Logs

### Endpoint-Specific Logs

View logs for a single endpoint:

**Via Web UI:**
1. Click **"View Logs"** on any endpoint card
2. Or navigate to `/endpoints/{id}/logs`

**Via API:**
```bash
curl http://localhost:5000/api/endpoints/1/checks?limit=100
```

### All Logs

View logs for all endpoints:

**Via Web UI:**
1. Click **"All Logs"** in the navigation menu
2. Or navigate to `/logs`

## Log Information

Each log entry contains:

### Basic Information

- **Timestamp** - When the check was performed
- **Endpoint Name** - Which endpoint was checked
- **Status** - Result of the check
- **Status Code** - HTTP status code received
- **Response Time** - How long the request took (ms)

### Status Values

| Status | Meaning |
|--------|---------|
| `success` | Request completed successfully (HTTP 2xx) |
| `failure` | Request failed (HTTP 4xx/5xx or network error) |
| `timeout` | Request exceeded timeout threshold |
| `validation_failed` | Response received but validation failed |

### Additional Details

- **Error Message** - Error details if the check failed
- **Validation Error** - Specific validation failure message
- **URL** - The endpoint that was checked

## Statistics Panel

The logs view includes a statistics panel showing:

### Uptime Percentage

Percentage of successful health checks.

**Calculation:**
```
Uptime % = (Successful Checks / Total Checks) × 100
```

**Example:**
- Total Checks: 1000
- Successful: 985
- Uptime: 98.5%

### Total Checks

Total number of health checks performed for the endpoint.

### Success Count

Number of successful health checks.

### Average Response Time

Mean response time across all health checks (in milliseconds).

**Note:** Only includes successful checks in the calculation.

## Filtering Logs

### By Time Range

Filter logs to a specific time period:

!!! note "Future Feature"
    Time range filtering is planned for a future release. Currently, logs show the most recent entries.

**Planned filters:**
- Last hour
- Last 24 hours
- Last 7 days
- Last 30 days
- Custom date range

### By Status

Filter by check result:

!!! note "Future Feature"
    Status filtering is planned for a future release.

**Planned filters:**
- Success only
- Failures only
- Timeouts only
- Validation failures only

### By Endpoint

When viewing "All Logs", filter by specific endpoint.

!!! note "Future Feature"
    Endpoint filtering is planned for a future release.

## Pagination

Logs are paginated to improve performance:

- **Default page size:** 50 entries
- **Navigation:** Previous/Next buttons
- **Limit parameter:** Customize via API

**API Example:**
```bash
# Get 100 most recent checks
curl http://localhost:5000/api/endpoints/1/checks?limit=100

# Get next page
curl http://localhost:5000/api/endpoints/1/checks?limit=50&page=2
```

## Exporting Logs

### JSON Export (API)

Export logs in JSON format:

```bash
# Export specific endpoint logs
curl http://localhost:5000/api/endpoints/1/checks?limit=1000 > logs.json

# Export all endpoint data
curl http://localhost:5000/api/health > health_status.json
```

### CSV Export

!!! note "Future Feature"
    CSV export is planned for a future release.

**Planned format:**
```csv
timestamp,endpoint_name,status,status_code,response_time_ms,error_message
2024-01-01 12:00:00,Production API,success,200,123.45,
2024-01-01 12:01:00,Production API,success,200,135.67,
```

## Analyzing Logs

### Identifying Patterns

Look for patterns in the logs:

**Intermittent failures:**
- Check appears healthy most of the time
- Occasional failures at specific times
- May indicate resource constraints or scheduled jobs

**Degrading performance:**
- Response times gradually increasing
- May indicate memory leaks or resource exhaustion

**Regular timeouts:**
- Consistent timeout errors
- May indicate insufficient timeout setting or slow service

### Performance Trends

Monitor response time trends:

**Healthy pattern:**
- Consistent response times
- Low variation
- Few outliers

**Warning signs:**
- Increasing average response time
- High variation in response times
- Frequent spikes

### Uptime Analysis

Use uptime percentage to measure reliability:

**SLA Examples:**
- **99.9% uptime** - "Three nines" - 8.76 hours downtime/year
- **99.95% uptime** - 4.38 hours downtime/year
- **99.99% uptime** - "Four nines" - 52.56 minutes downtime/year

## Common Use Cases

### 1. Investigating an Incident

When an endpoint fails:

1. View endpoint-specific logs
2. Look at the error message
3. Check if validation failed
4. Review response times before failure
5. Check for patterns (time of day, frequency)

**Example Investigation:**
```
Error: Connection refused
Pattern: Started at 2:00 AM
Analysis: Nightly maintenance window
Action: Adjust check schedule or disable during maintenance
```

### 2. Monitoring SLA Compliance

Track if services meet SLA requirements:

1. Check uptime percentage
2. Compare against SLA target (e.g., 99.9%)
3. Review failure count
4. Identify root causes of downtime

### 3. Performance Baselining

Establish normal performance baselines:

1. Review average response time over 30 days
2. Identify typical range
3. Set alerts for values outside normal range
4. Track improvements after optimizations

### 4. Capacity Planning

Use response time trends for capacity planning:

1. Monitor response time growth
2. Correlate with usage patterns
3. Identify when scaling is needed
4. Plan infrastructure upgrades

## Best Practices

### 1. Regular Review

Review logs regularly:

- **Daily:** Check for new failures
- **Weekly:** Review uptime percentages
- **Monthly:** Analyze trends and patterns

### 2. Act on Failures

Don't ignore failures:

1. Investigate root cause
2. Document issues
3. Fix or adjust configuration
4. Verify fix with manual check

### 3. Set Realistic Expectations

Understand that 100% uptime is unrealistic:

- Network issues happen
- Services restart
- Maintenance windows occur

**Target:** 99%+ uptime for production services

### 4. Use Validation

Don't rely solely on HTTP status codes:

- Enable response validation
- Verify critical response fields
- Catch degraded but "responding" services

### 5. Archive Old Logs

Plan for log retention:

!!! note "Future Feature"
    Automatic log archival and retention policies are planned for a future release.

**Recommendations:**
- Keep detailed logs for 30-90 days
- Archive summary statistics for longer
- Delete very old data to save space

## Troubleshooting

### Logs Not Appearing

**Causes:**
- Endpoint not enabled
- Scheduler not running
- Check interval too long
- First check hasn't run yet

**Solutions:**
1. Verify endpoint is enabled
2. Check application is running
3. Manually trigger a check
4. Wait for next scheduled check

### Statistics Incorrect

**Causes:**
- Recent configuration change
- Database migration
- Validation rules changed

**Solutions:**
1. Wait for more checks to accumulate
2. Manually recalculate if needed
3. Review recent configuration changes

### Missing Time Periods

**Causes:**
- Application was stopped
- Endpoint was disabled
- System maintenance

**Solutions:**
1. Check application uptime logs
2. Review endpoint history (enabled/disabled)
3. Fill gaps with manual checks if needed

### Response Times Seem Wrong

**Causes:**
- Network latency included
- Server processing time varies
- Validation adds overhead

**Notes:**
- Response time includes full round-trip
- DNS lookup time included
- SSL handshake included
- Network latency included

## Data Retention

### Current Behavior

All health check logs are retained indefinitely.

**Database Growth:**
- ~1KB per check
- 1 endpoint @ 60s interval = ~1.4MB/day
- 10 endpoints = ~14MB/day

### Future Features

Planned automatic retention policies:

- **Detailed logs:** 90 days
- **Hourly summaries:** 1 year
- **Daily summaries:** Forever

## Next Steps

- [Troubleshooting](troubleshooting.md) - Solve common issues
- [API Reference](../api/rest-api.md) - Programmatic access to logs
- [Dashboard](dashboard.md) - Real-time monitoring
