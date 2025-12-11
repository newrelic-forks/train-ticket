FROM node

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

RUN mkdir -p /app
WORKDIR /app

ADD ./node_modules /app/node_modules
ADD ./package.json /app/
ADD ./public /app/public
# RUN npm install

ADD ./bin /app/bin
ADD ./app.js /app/
CMD [ "npm", "start" ]

EXPOSE 16108