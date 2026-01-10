#!/bin/bash

# ================================================================
# Script Name: docker_setup.sh
# Description: Setup script for Docker environment
# Author: Jerry
# License: MIT
# ================================================================

RUNNER_SCALE=10  # Default value

# Parse arguments
ARGS=("$@")
for ((i=0; i<$#; i++)); do
  arg="${ARGS[$i]}"
  next_arg="${ARGS[$((i+1))]:-}"
  if [[ "$arg" == "--build" || "$arg" == "-b" ]]; then
    BUILD_FLAG="--build"
  elif [[ "$arg" == "--clear" || "$arg" == "-c" ]]; then
    CLEAR_FLAG="--clear"
   elif [[ "$arg" == "--stop" || "$arg" == "-s" ]]; then
    STOP_FLAG="--stop"
  elif [[ "$arg" == "--runner" || "$arg" == "-r" ]]; then
    RUNNER_FLAG="--runner"
    # Check if next argument is a number
    if [[ "$next_arg" =~ ^[0-9]+$ ]]; then
      RUNNER_SCALE="$next_arg"
      ((i++))  # Skip next arg
    fi
  fi
done

if [[ -n "$CLEAR_FLAG" ]]; then
  echo "Cleaning up existing containers and images..."
  docker stop $(docker ps -q)
  docker rm -f $(docker ps -aq)
  docker system prune -af
  docker volume prune -af
  echo "Docker cleanup complete"
  exit 0

elif [[ -n "$STOP_FLAG" ]]; then
  echo "Cleaning up existing containers..."
  docker stop $(docker ps -q)
  docker rm -f $(docker ps -aq)
  echo "Docker containers cleanup complete"
  exit 0

fi

if [[ -n "$BUILD_FLAG" ]]; then
  echo "Building and starting Docker containers..."
  docker compose -f docker-compose.yml up --build -d
  echo "Access the application at: https://localhost"

elif [[ -n "$RUNNER_FLAG" ]]; then
  echo "Starting runner containers (scale: $RUNNER_SCALE)..."
  docker compose -f docker-compose-create-runners.yml up --scale runner-app=$RUNNER_SCALE

else
  echo "Starting Docker containers..."
  docker compose -f docker-compose.yml up -d
  echo "Access the application at: https://localhost"
fi

echo "Docker setup complete"

