#!/bin/bash

# ================================================================
# Script Name: docker_setup.sh
# Description: Setup script for Docker environment
# Author: Jerry
# License: MIT
# ================================================================

docker stop $(docker ps -q)
docker rm -f $(docker ps -aq)

docker system prune -af

docker compose -f docker-compose.yml up --build -d
