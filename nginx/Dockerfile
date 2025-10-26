FROM nginx:alpine

# Install envsubst for templating
RUN apk add --no-cache bash gettext

# Copy custom nginx configuration (templated)
COPY default.conf /tmp/default.conf.template

# Create nginx user and set permissions
RUN addgroup -g 1001 -S nginx && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Expose ports
EXPOSE 80 443

# Render template and start nginx
ENV DOMAIN=localhost
CMD ["/bin/sh", "-c", "envsubst '$$DOMAIN' < /tmp/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'" ]

