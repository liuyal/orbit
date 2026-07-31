#!/bin/bash

# ================================================================
# Script Name: setup-runner.sh
# Description: Setup script for runner Docker environment
# Author: Jerry
# License: MIT
# ================================================================

show_help() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  -h, --help            Show this help message and exit"
  echo "  -br, --build-runner   Build runner Docker images"
  echo "  -sr, --start-runner N  Start N runner containers (default: 10)"
  echo
}

# Load environment variables from .env file if it exists
if [ -f ../env/.env ]; then
  echo "Loading environment variables from .env file..."
  set -a
  source ../env/.env
  set +a
fi

RUNNER_SCALE=10  # Default value

# Parse arguments
ARGS=("$@")
for ((i=0; i<$#; i++)); do
  arg="${ARGS[$i]}"
  next_arg="${ARGS[$((i+1))]:-}"

  if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
    show_help
    exit 0

  elif [[ "$arg" == "--build-runner" || "$arg" == "-br" ]]; then
    BUILD_RUNNER_FLAG="--build-runner"

  elif [[ "$arg" == "--start-runner" || "$arg" == "-sr" ]]; then
    START_RUNNER_FLAG="--start-runner"
    # Check if next argument is a number
    if [[ "$next_arg" =~ ^[0-9]+$ ]]; then
      RUNNER_SCALE="$next_arg"
      ((i++))  # Skip next arg
    fi
  fi
done

if [[ -n "$BUILD_RUNNER_FLAG" ]]; then
  echo "Building runner docker images..."
  docker compose -f docker-compose-runners.yml build
fi

if [[ -n "$START_RUNNER_FLAG" ]]; then
  echo "Starting $RUNNER_SCALE runner container(s)..."

  # Create tmp directory if it doesn't exist
  mkdir -p tmp
  cp ../env/.env tmp/.env

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

echo "Runner setup complete"

