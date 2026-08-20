FROM nginx:alpine

# Install certbot, openssl, bash and curl for automated SSL issuance & renewal
RUN apk add --no-cache certbot certbot-nginx openssl bash curl

# Create required directories
RUN mkdir -p /var/www/certbot /etc/nginx/ssl /etc/nginx/ssl/live

# Copy configuration and entrypoint script
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]
