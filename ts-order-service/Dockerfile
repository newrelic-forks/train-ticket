FROM eclipse-temurin:8-jre-focal

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

# Download New Relic Java Agent
RUN mkdir -p /app/newrelic && \
    curl -O https://download.newrelic.com/newrelic/java-agent/newrelic-agent/current/newrelic-java.zip && \
    unzip newrelic-java.zip -d /app/newrelic && \
    rm newrelic-java.zip

ADD ./target/ts-order-service-1.0.jar /app/

# Copy New Relic configuration
COPY ./src/main/resources/newrelic.yml /app/newrelic/

# Start with New Relic agent
CMD ["java", "-Xmx200m", "-javaagent:/app/newrelic/newrelic/newrelic.jar", "-Dnewrelic.config.file=/app/newrelic/newrelic.yml", "-jar", "/app/ts-order-service-1.0.jar"]

EXPOSE 12031