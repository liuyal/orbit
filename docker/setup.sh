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

  if [[ "$arg" == "--clean" || "$arg" == "-c" ]]; then
    CLEAN_FLAG="--clean"

  elif [[ "$arg" == "--stop" || "$arg" == "-s" ]]; then
    STOP_FLAG="--stop"

  elif [[ "$arg" == "--build" || "$arg" == "-b" ]]; then
    BUILD_FLAG="--build"

  elif [[ "$arg" == "--start" ]]; then
    START_FLAG="--start"

  elif [[ "$arg" == "--start-runner" || "$arg" == "-r" ]]; then
    RUNNER_FLAG="--start-runner"
    # Check if next argument is a number
    if [[ "$next_arg" =~ ^[0-9]+$ ]]; then
      RUNNER_SCALE="$next_arg"
      ((i++))  # Skip next arg
    fi
  fi
done

if [[ -n "$CLEAN_FLAG" ]]; then
  echo "Cleaning up Docker containers and images..."
  docker stop $(docker ps -q)
  docker rm -f $(docker ps -aq)
  docker system prune -af
  docker volume prune -af
  echo "Docker cleanup complete"

elif [[ -n "$STOP_FLAG" ]]; then
  echo "Cleaning up existing Docker containers..."
  docker stop $(docker ps -q)
  docker rm -f $(docker ps -aq)
  echo "Docker containers cleanup complete"

fi

if [[ -n "$BUILD_FLAG" ]]; then
  echo "Building docker images..."
  docker compose -f docker-compose.yml build
  docker compose -f docker-compose-create-runners.yml build

fi

if [[ -n "$START_FLAG" ]]; then
  echo "Starting Docker containers..."
  docker compose -f docker-compose.yml up -d
  echo "Access the application at: https://localhost"

elif [[ -n "$RUNNER_FLAG" ]]; then
  echo "Starting runner containers (scale: $RUNNER_SCALE)..."
  docker compose -f docker-compose-create-runners.yml up -d --scale runner-app=$RUNNER_SCALE

fi

echo "Docker setup complete"
