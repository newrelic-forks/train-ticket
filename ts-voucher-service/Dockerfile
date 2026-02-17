FROM python:3

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt ./
RUN pip install cryptography
RUN pip install --no-cache-dir -r requirements.txt

ADD ./server.py /app/
ADD ./newrelic.ini /app/
CMD [ "newrelic-admin", "run-program", "python", "server.py" ]

EXPOSE 16101