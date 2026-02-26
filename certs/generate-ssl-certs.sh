#!/bin/bash
# Generate self-signed SSL certificates for nginx

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/ca.key \
  -out ssl/ca.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "SSL certificates generated successfully in ssl/ directory"
