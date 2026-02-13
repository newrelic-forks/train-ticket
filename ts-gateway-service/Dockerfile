FROM eclipse-temurin:8-jre-focal

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

# Download New Relic Java Agent
RUN mkdir -p /app/newrelic /app/logs && \
    curl -o /app/newrelic/newrelic.jar https://download.newrelic.com/newrelic/java-agent/newrelic-agent/current/newrelic.jar

# Copy New Relic configuration file
COPY newrelic.yml /app/newrelic/

ADD ./target/ts-gateway-service-1.0.jar /app/
CMD ["java", "-javaagent:/app/newrelic/newrelic.jar", "-Dnewrelic.config.file=/app/newrelic/newrelic.yml", "-jar", "/app/ts-gateway-service-1.0.jar"]

EXPOSE 18888 
