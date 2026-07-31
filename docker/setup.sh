#!/bin/bash

# ================================================================
# Script Name: docker_setup.sh
# Description: Setup script for Docker environment
# Author: Jerry
# License: MIT
# ================================================================

show_help() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  -h, --help            Show this help message and exit"
  echo "  -c, --clean           Clean up Docker containers and images"
  echo "  -p, --stop            Stop and remove all Docker containers"
  echo "  -b, --build           Build Docker images"
  echo "  -s, --start           Start Docker containers"
  echo
}

# Load environment variables from .env file if it exists
if [ -f ../env/.env ]; then
  echo "Loading environment variables from .env file..."
  set -a
  source ../env/.env
  set +a
fi

# Parse arguments
ARGS=("$@")
for ((i=0; i<$#; i++)); do
  arg="${ARGS[$i]}"

  if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
    show_help
    exit 0

  elif [[ "$arg" == "--clean" || "$arg" == "-c" ]]; then
    CLEAN_FLAG="--clean"

  elif [[ "$arg" == "--stop" || "$arg" == "-p" ]]; then
    STOP_FLAG="--stop"

  elif [[ "$arg" == "--build" || "$arg" == "-b" ]]; then
    BUILD_FLAG="--build"

  elif [[ "$arg" == "--start" || "$arg" == "-s" ]]; then
    START_FLAG="--start"
  fi
done

if [[ -n "$STOP_FLAG" ]]; then
  echo "Cleaning up existing Docker containers..."
  docker stop $(docker ps -q)
  docker rm -f $(docker ps -aq)
  echo "Docker containers cleanup complete"
fi

if [[ -n "$CLEAN_FLAG" ]]; then
  echo "Cleaning up Docker containers and images..."
  docker stop $(docker ps -q)
  docker rm -f $(docker ps -aq)
  docker system prune -af
  docker volume prune -af
  echo "Docker cleanup complete"
fi

if [[ -n "$BUILD_FLAG" ]]; then
  echo "Building docker images..."
  docker compose -f docker-compose.yml build
fi


if [[ -n "$START_FLAG" ]]; then
  echo "Starting Docker containers..."
  docker compose -f docker-compose.yml up -d
  echo "Access the application at: https://localhost"
fi


echo "Docker setup complete"