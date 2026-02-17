FROM python:3.8-slim

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

RUN apt update -y \
 && apt install -y build-essential python3-dev cmake libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=TRUE

RUN mkdir -p /app
ADD . /app/
WORKDIR /app

# Ensure pip and build tooling are up-to-date so packages with native extensions can build
RUN pip install --upgrade pip setuptools wheel

RUN pip install -r requirements.txt

CMD ["newrelic-admin", "run-program", "gunicorn", "-w", "4", "-b", "0.0.0.0:17001", "app:app"]

EXPOSE 17001