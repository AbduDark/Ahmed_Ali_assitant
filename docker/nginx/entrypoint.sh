#!/bin/bash
set -e

DOMAIN="${DOMAIN_NAME:-assistant.192.99.144.235.nip.io}"
EMAIL="${SSL_EMAIL:-admin@assistant.192.99.144.235.nip.io}"

echo "========================================================"
echo "🔐 Starting Nginx with Automated SSL for: $DOMAIN"
echo "========================================================"

mkdir -p /var/www/certbot
mkdir -p /etc/nginx/ssl/selfsigned
mkdir -p /etc/nginx/ssl/live

# 1. Create fallback self-signed certificate if Let's Encrypt certificate doesn't exist yet
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "📜 Generating temporary self-signed certificate for initial boot..."
    openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
        -keyout /etc/nginx/ssl/selfsigned/privkey.pem \
        -out /etc/nginx/ssl/selfsigned/fullchain.pem \
        -subj "/CN=$DOMAIN/O=TeacherAssistant/C=EG" >/dev/null 2>&1

    cp /etc/nginx/ssl/selfsigned/fullchain.pem /etc/nginx/ssl/live/fullchain.pem
    cp /etc/nginx/ssl/selfsigned/privkey.pem /etc/nginx/ssl/live/privkey.pem
else
    echo "✅ Found existing Let's Encrypt certificate."
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/nginx/ssl/live/fullchain.pem
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/nginx/ssl/live/privkey.pem
fi

# 2. Function to request / renew Let's Encrypt SSL certificate in background
obtain_and_maintain_ssl() {
    # Wait for Nginx to be up
    sleep 5

    echo "🌐 Attempting to obtain official Let's Encrypt SSL certificate for $DOMAIN..."
    if certbot certonly --webroot -w /var/www/certbot \
        -d "$DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --non-interactive \
        --keep-until-expiring; then

        echo "🎉 Let's Encrypt certificate successfully obtained / verified!"
        cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" /etc/nginx/ssl/live/fullchain.pem
        cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" /etc/nginx/ssl/live/privkey.pem
        nginx -s reload
        echo "🔄 Nginx reloaded with trusted Let's Encrypt certificate."
    else
        echo "⚠️ Certbot challenge failed or rate-limited. Running with self-signed certificate on port 443."
    fi

    # Auto-renewal loop every 12 hours
    while true; do
        sleep 43200
        echo "🔍 Checking certificate renewal for $DOMAIN..."
        if certbot renew --webroot -w /var/www/certbot --quiet; then
            if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
                cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" /etc/nginx/ssl/live/fullchain.pem
                cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" /etc/nginx/ssl/live/privkey.pem
                nginx -s reload
                echo "🔄 Certificate renewed and Nginx reloaded."
            fi
        fi
    done
}

# Start background certificate manager
obtain_and_maintain_ssl &

# Start Nginx in foreground
echo "🚀 Starting Nginx reverse proxy..."
exec nginx -g 'daemon off;'
