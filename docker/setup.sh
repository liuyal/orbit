#!/bin/bash

# ================================================================
# Script Name: docker_setup.sh
# Description: Setup script for Docker environment
# Author: Jerry
# License: MIT
# ================================================================

for arg in "$@"; do
  if [[ "$arg" == "--build" || "$arg" == "-b" ]]; then
    BUILD_FLAG="--build"
  fi
done

if [[ -n "$BUILD_FLAG" ]]; then
  docker stop $(docker ps -q)
  docker rm -f $(docker ps -aq)
  docker system prune -af
  docker volume prune -af
  docker compose -f docker-compose.yml up --build -d
else
  docker compose -f docker-compose.yml up -d
fi