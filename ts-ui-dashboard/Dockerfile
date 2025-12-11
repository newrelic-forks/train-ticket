FROM openresty/openresty:trusty

RUN /bin/cp /usr/share/zoneinfo/America/New_York /etc/localtime && echo 'America/New_York' >/etc/timezone

COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf

COPY static /usr/share/nginx/html