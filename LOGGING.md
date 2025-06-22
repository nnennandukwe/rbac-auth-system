# Logging Documentation

## Overview

The RBAC Auth System implements comprehensive logging throughout the application to provide visibility into system operations, security events, and audit trails. The logging system is designed to be structured, searchable, and compliant with security best practices.

## Logging Architecture

### Log Categories

1. **Application Logs** (`rbac_auth.log`)
   - General application events
   - Performance metrics
   - Error tracking
   - Debug information

2. **Security Logs** (`security.log`)
   - Authentication events (login/logout)
   - Authorization failures
   - Token validation events
   - Permission checks
   - Suspicious activities

3. **Audit Logs** (`audit.log`)
   - User management operations
   - Role assignments
   - Permission changes
   - API access tracking
   - Data modifications

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error events that might still allow the application to continue
- **CRITICAL**: Serious error events that might cause the application to abort

## Log Format

### JSON Structure

All logs are formatted as JSON for easy parsing and analysis:

```json
{
  \"timestamp\": \"2024-01-15T10:30:45.123456Z\",\n  \"level\": \"INFO\",\n  \"logger\": \"rbac_auth.auth\",\n  \"message\": \"User logged in successfully: john_doe\",\n  \"module\": \"auth\",\n  \"function\": \"login\",\n  \"line\": 125,\n  \"user_id\": 123,\n  \"username\": \"john_doe\",\n  \"ip_address\": \"192.168.1.100\",\n  \"roles\": [\"Editor\", \"Viewer\"]\n}
```

### Common Fields

- `timestamp`: ISO 8601 formatted timestamp in UTC
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger`: Logger name indicating the source module
- `message`: Human-readable log message
- `module`: Python module name
- `function`: Function name where log was generated
- `line`: Line number in source code

### Context Fields

Additional fields are included based on context:

- `user_id`: Database ID of the user
- `username`: Username of the authenticated user
- `ip_address`: Client IP address
- `endpoint`: API endpoint being accessed
- `method`: HTTP method (GET, POST, etc.)
- `status_code`: HTTP response status code
- `duration_ms`: Request processing time in milliseconds
- `permission`: Permission being checked
- `roles`: User roles
- `error_type`: Type of exception/error
- `event_type`: Specific event type for security/audit logs

## Security Events

### Authentication Events

#### Successful Login
```json
{
  \"event_type\": \"LOGIN_SUCCESS\",\n  \"message\": \"User logged in successfully: john_doe\",\n  \"username\": \"john_doe\",\n  \"user_id\": 123,\n  \"ip_address\": \"192.168.1.100\",\n  \"roles\": [\"Editor\"]\n}
```

#### Failed Login
```json
{
  \"event_type\": \"LOGIN_FAILED\",\n  \"message\": \"Login failed - invalid password for user: john_doe\",\n  \"username\": \"john_doe\",\n  \"ip_address\": \"192.168.1.100\",\n  \"reason\": \"invalid_password\"\n}
```

#### Token Events
```json
{
  \"event_type\": \"TOKEN_VALIDATION_FAILED\",\n  \"message\": \"Token validation failed - token expired\",\n  \"reason\": \"expired\"\n}
```

### Authorization Events

#### Permission Granted
```json
{
  \"event_type\": \"PERMISSION_GRANTED\",\n  \"message\": \"Permission granted: can_write for user john_doe\",\n  \"username\": \"john_doe\",\n  \"permission\": \"can_write\",\n  \"roles\": [\"Editor\"]\n}
```

#### Permission Denied
```json
{
  \"event_type\": \"PERMISSION_DENIED\",\n  \"message\": \"Permission denied: can_delete for user john_doe\",\n  \"username\": \"john_doe\",\n  \"permission\": \"can_delete\",\n  \"roles\": [\"Viewer\"]\n}
```

## Audit Events

### User Management
```json
{
  \"event_type\": \"USER_CREATED\",\n  \"message\": \"New user created: jane_doe\",\n  \"username\": \"jane_doe\",\n  \"user_id\": 124,\n  \"email\": \"jane@example.com\",\n  \"roles\": [\"Viewer\"]\n}
```

### API Access
```json
{
  \"event_type\": \"API_ACCESS\",\n  \"message\": \"Admin area accessed by user: john_doe\",\n  \"username\": \"john_doe\",\n  \"resource\": \"/admin\",\n  \"roles\": [\"Admin\"]\n}
```

## Configuration

### Environment Variables

Set these environment variables to configure logging:

```bash
LOG_LEVEL=INFO          # Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)\nLOG_FILE=logs/rbac_auth.log  # Main log file path\n```

### Log Rotation

Logs are automatically rotated when they reach 10MB in size, with up to 5 backup files kept for application logs and 10 backup files for security/audit logs.

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Failed Login Attempts**
   - Multiple failed attempts from same IP
   - Failed attempts for non-existent users
   - Brute force attack patterns

2. **Permission Violations**
   - Repeated permission denied events
   - Privilege escalation attempts
   - Access to sensitive endpoints

3. **System Errors**
   - Database connection failures
   - Token validation errors
   - Unexpected exceptions

### Sample Queries

#### Find Failed Login Attempts
```bash
grep '\"event_type\": \"LOGIN_FAILED\"' logs/security.log | jq '.'\n```

#### Monitor Permission Denials
```bash
grep '\"event_type\": \"PERMISSION_DENIED\"' logs/security.log | jq '.username, .permission, .timestamp'\n```

#### Track API Access
```bash
grep '\"event_type\": \"API_ACCESS\"' logs/audit.log | jq '.username, .resource, .timestamp'\n```

## Log Analysis Tools

### Recommended Tools

1. **ELK Stack** (Elasticsearch, Logstash, Kibana)
   - Centralized log aggregation
   - Real-time search and analysis
   - Visualization dashboards

2. **Splunk**
   - Enterprise log management
   - Advanced analytics
   - Alerting capabilities

3. **Fluentd/Fluent Bit**
   - Log forwarding and processing
   - Multiple output destinations
   - Lightweight and efficient

### Sample Logstash Configuration

```ruby
input {\n  file {\n    path => \"/path/to/logs/*.log\"\n    start_position => \"beginning\"\n    codec => \"json\"\n  }\n}\n\nfilter {\n  if [logger] =~ /rbac_auth/ {\n    mutate {\n      add_tag => [\"rbac_auth\"]\n    }\n  }\n  \n  if [event_type] {\n    mutate {\n      add_tag => [\"security_event\"]\n    }\n  }\n}\n\noutput {\n  elasticsearch {\n    hosts => [\"localhost:9200\"]\n    index => \"rbac-auth-logs-%{+YYYY.MM.dd}\"\n  }\n}\n```

## Security Considerations

### Sensitive Data

The logging system is designed to avoid logging sensitive information:

- Passwords are never logged
- JWT tokens are not logged in full
- Personal data is minimized in logs
- IP addresses are logged for security purposes

### Log Integrity

- Logs are written with appropriate file permissions
- Consider implementing log signing for critical environments
- Regular backup of log files is recommended
- Monitor log files for tampering

### Compliance

The logging system supports compliance with various standards:

- **GDPR**: Personal data handling is minimized
- **SOX**: Audit trails for financial systems
- **HIPAA**: Healthcare data access logging
- **PCI DSS**: Payment card industry security standards

## Troubleshooting

### Common Issues

1. **Log Files Not Created**
   - Check directory permissions
   - Verify LOG_FILE environment variable
   - Ensure logs directory exists

2. **Missing Log Entries**
   - Check log level configuration
   - Verify logger names in code
   - Check for exceptions in logging setup

3. **Performance Impact**
   - Monitor disk I/O for log writes
   - Consider async logging for high-volume systems
   - Adjust log levels in production

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export LOG_LEVEL=DEBUG\npython -m uvicorn app.main:app --reload\n```

## Best Practices

1. **Log Levels**
   - Use appropriate log levels for different events
   - DEBUG for development, INFO+ for production
   - ERROR for exceptions, WARNING for potential issues

2. **Structured Logging**
   - Always use JSON format for machine readability
   - Include relevant context in log entries
   - Use consistent field names across the application

3. **Performance**
   - Avoid excessive logging in tight loops
   - Use async logging for high-throughput systems
   - Monitor log file sizes and rotation

4. **Security**
   - Never log sensitive data (passwords, tokens)
   - Log security events immediately
   - Implement log monitoring and alerting

5. **Maintenance**
   - Regular log rotation and cleanup
   - Monitor disk space usage
   - Archive old logs for compliance