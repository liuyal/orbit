@echo off
REM Generate self-signed SSL certificates for nginx on Windows

REM Create ssl directory if it doesn't exist
if not exist ssl mkdir ssl

REM Generate self-signed certificate using OpenSSL
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl\nginx.key -out ssl\nginx.crt -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo SSL certificates generated successfully in ssl\ directory
