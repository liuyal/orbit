#!/bin/bash

# ================================================================
# Script Name: docker_setup.sh
# Description: Setup script for Docker environment
# Author: Jerry
# License: MIT
# ================================================================

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  set -a
  source .env
  set +a
fi

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
  docker compose -f docker-compose-runners.yml build

fi

if [[ -n "$START_FLAG" ]]; then
  echo "Starting Docker containers..."
  docker compose -f docker-compose.yml up -d
  echo "Access the application at: https://localhost"

elif [[ -n "$RUNNER_FLAG" ]]; then
  echo "Starting $RUNNER_SCALE runner container(s)..."

  # Create tmp directory if it doesn't exist
  mkdir -p tmp
  cp .env tmp/.env

  # Generate a temporary docker-compose file with explicit runner services
  echo "Generating docker-compose configuration for $RUNNER_SCALE runners..."

  cat > tmp/docker-compose-tmp-runner.yml << EOF
services:
EOF

  # Generate service definition for each runner
  for ((i=0; i<$RUNNER_SCALE; i++)); do
    cat >> tmp/docker-compose-tmp-runner.yml << EOF
  runner-$i:
    image: runner-app:latest
    container_name: runner-$i
    restart: unless-stopped
    environment:
      - GITHUB_OWNER=${GITHUB_OWNER}
      - GITHUB_REPOSITORY=${GITHUB_REPOSITORY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - RUNNER_NAME=runner-$i
      - RUNNER_WORKDIR=_work
      - RUNNER_LABELS=linux
EOF
  done

  # Start all runners using docker compose
  echo "Starting runners with docker compose..."
  docker compose -f tmp/docker-compose-tmp-runner.yml up -d

  echo "Started $RUNNER_SCALE runner(s)"
  echo "Temporary compose file saved at: tmp/docker-compose-tmp-runner.yml"

fi

echo "Docker setup complete"