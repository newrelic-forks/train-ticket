# New Relic Instrumentation Setup - ts-order-service

## Overview
This document describes the New Relic APM instrumentation added to the ts-order-service.

## Environment Variables Required
- `NEW_RELIC_LICENSE_KEY` (required) - Your New Relic license key
- `NEW_RELIC_APP_NAME` (optional) - Application name in New Relic (defaults to "ts-order-service")
- `NEW_RELIC_ENVIRONMENT` (optional) - Environment name (defaults to "development")
- `NEW_RELIC_ACCOUNT_ID` (optional) - Account ID for metrics export

## Files Modified

### 1. pom.xml
Added dependencies:
- `newrelic-agent` (8.17.0) - Java agent
- `newrelic-api` (8.17.0) - API for custom instrumentation
- `spring-boot-starter-actuator` - Health and metrics endpoints
- `micrometer-registry-new-relic` - Metrics integration

### 2. src/main/resources/newrelic.yml
Complete New Relic agent configuration with:
- License key from environment variable
- Application naming
- Transaction tracing
- Error collection
- Distributed tracing
- Custom metrics collection

### 3. Dockerfile
Modified to:
- Download New Relic Java agent during build
- Copy configuration file
- Start JVM with `-javaagent` parameter

### 4. src/main/resources/application.yml
Added:
- New Relic configuration properties
- Management endpoints for health/metrics
- Micrometer New Relic registry configuration

### 5. OrderServiceImpl.java
Added custom instrumentation:
- `@Trace` annotations on key methods:
  - `getSoldTickets()` - Seat availability tracking
  - `findOrderById()` - Order lookup tracking
  - `create()` - Order creation tracking
  - `payOrder()` - Payment processing tracking
- Custom attributes: orderId, orderPrice, trainNumber, orderStatus
- Custom metrics: Order creation count and total value

## Build & Deployment

1. Build the application:
```bash
mvn clean package
```

2. Build Docker image:
```bash
docker build -t ts-order-service .
```

3. Run with New Relic:
```bash
docker run -e NEW_RELIC_LICENSE_KEY=your_license_key ts-order-service
```

## Monitoring Features

### Automatic Instrumentation
- JVM metrics (memory, CPU, GC)
- Database queries (MySQL)
- HTTP requests/responses
- Spring framework components
- Error tracking and stack traces

### Custom Business Metrics
- Order creation rate
- Order total value tracking
- Payment processing performance
- Database query performance per operation

### Health Endpoints
Available at:
- `/actuator/health` - Application health
- `/actuator/info` - Application info
- `/actuator/metrics` - Micrometer metrics

## Troubleshooting

1. **Agent not starting**: Check `NEW_RELIC_LICENSE_KEY` is set
2. **No data in New Relic**: Verify network connectivity to New Relic endpoints
3. **Performance issues**: Adjust agent configuration in `newrelic.yml`
4. **Custom metrics not appearing**: Verify `NEW_RELIC_ACCOUNT_ID` is set for metrics export

## Custom Metrics Available

- `Custom/Orders/Created` - Number of orders created
- `Custom/Orders/TotalValue` - Total monetary value of orders
- Transaction traces for all instrumented methods
- Custom attributes on all transactions showing business context