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
  elif [[ "$arg" == "--clear" || "$arg" == "-c" ]]; then
    CLEAR_FLAG="--clear"
  fi
done

if [[ -n "$CLEAR_FLAG" ]]; then
  echo "Cleanuping up existing Docker containers and images..."
  docker stop $(docker ps -q)
  docker rm -f $(docker ps -aq)
  docker system prune -af
  docker volume prune -af
  echo "Docker cleanup complete"
  exit 0
  
elif [[ -n "$BUILD_FLAG" ]]; then
  echo "Cleanuping up existing Docker containers and images..."
  docker stop $(docker ps -q)
  docker rm -f $(docker ps -aq)
  docker system prune -af
  docker volume prune -af

  echo "Building and starting Docker containers..."
  docker compose -f docker-compose.yml up --build -d

else
  echo "Starting Docker containers..."
  docker compose -f docker-compose.yml up -d
fi

echo "Docker setup complete"
echo "Access the application at: https://localhost"
