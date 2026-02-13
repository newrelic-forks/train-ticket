FROM eclipse-temurin:8-jre-focal

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

# Install unzip for New Relic agent download
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# Download New Relic Java Agent
RUN mkdir -p /app/newrelic && \
    curl -O https://download.newrelic.com/newrelic/java-agent/newrelic-agent/current/newrelic-java.zip && \
    unzip newrelic-java.zip -d /app/newrelic && \
    rm newrelic-java.zip

ADD ./target/ts-payment-service-1.0.jar /app/

# Copy New Relic configuration
COPY ./src/main/resources/newrelic.yml /app/newrelic/
# Start with New Relic agent
CMD ["java", "-Xmx200m", "-javaagent:/app/newrelic/newrelic/newrelic.jar", "-Dnewrelic.config.file=/app/newrelic/newrelic.yml", "-jar", "/app/ts-payment-service-1.0.jar"]

EXPOSE 19001