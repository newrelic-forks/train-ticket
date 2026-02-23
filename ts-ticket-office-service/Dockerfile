FROM node

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

RUN mkdir -p /app
WORKDIR /app

ADD ./package.json /app/
RUN npm install
ADD ./public /app/public

ADD ./bin /app/bin
ADD ./app.js /app/
ADD ./newrelic.js /app/
CMD [ "npm", "start" ]

EXPOSE 16108