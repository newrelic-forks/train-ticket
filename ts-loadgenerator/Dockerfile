# Train-Ticket Load Generator Dockerfile
# Based on Python 3.11 with Locust framework
# Compatible with Ubuntu EC2 (AMD64/x86_64)

FROM python:3.11.1-slim AS base

FROM base AS builder

COPY requirements.txt .

# Install dependencies with platform-specific wheels for AMD64
RUN pip install --prefix="/install" --no-cache-dir -r requirements.txt

FROM base

WORKDIR /loadgen

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local

# Add application code
COPY locustfile.py .

# Enable gevent support in debugger
ENV GEVENT_SUPPORT=True

# Run Locust in headless mode
# FRONTEND_ADDR: Target UI dashboard service (e.g., ts-ui-dashboard:8080)
# USERS: Number of concurrent simulated users (default: 10)
ENTRYPOINT ["/bin/sh", "-c", "locust --host=\"http://${FRONTEND_ADDR}\" --headless -u \"${USERS:-10}\" -r \"${SPAWN_RATE:-1}\" ${RUN_TIME:+--run-time $RUN_TIME} 2>&1"]
