FROM eclipse-temurin:8-jre-focal

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

ADD ./target/ts-security-service-1.0.jar /app/
CMD ["java", "-Xmx200m",  "-jar", "/app/ts-security-service-1.0.jar"]

EXPOSE 11188