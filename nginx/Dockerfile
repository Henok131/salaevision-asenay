FROM nginx:alpine

RUN apk add --no-cache bash gettext

# Copy template config and entrypoint
COPY default.conf /etc/nginx/templates/default.conf.template
COPY --chown=root:root <<'EOF' /docker-entrypoint.d/50-envsubst-on-templates.sh
#!/usr/bin/env sh
set -eu

TEMPLATE="/etc/nginx/templates/default.conf.template"
TARGET="/etc/nginx/conf.d/default.conf"
envsubst '$DOMAIN' < "$TEMPLATE" > "$TARGET"
echo "Rendered NGINX config with DOMAIN=$DOMAIN"
EOF

RUN chmod +x /docker-entrypoint.d/50-envsubst-on-templates.sh

# Create nginx user and set permissions
RUN addgroup -g 1001 -S nginx && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

