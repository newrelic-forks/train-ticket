FROM eclipse-temurin:8-jre-focal

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

ADD ./target/ts-gateway-service-1.0.jar /app/
CMD ["java", "-Xmx1024m",  "-jar", "/app/ts-gateway-service-1.0.jar"]

EXPOSE 18888 
