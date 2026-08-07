#!/bin/sh
# Ensure the WebDAV upload directory is writable by Apache at runtime
chmod -R 777 /usr/local/apache2/htdocs/files

# Hand off to the default Apache entrypoint
exec httpd-foreground "$@"

