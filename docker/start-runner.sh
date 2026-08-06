#!/bin/bash

set -e

# Use hostname as runner name only if not already set by entrypoint
# This ensures each container in a scaled deployment gets a unique name
if [ -z "$RUNNER_NAME" ] || [ "$RUNNER_NAME" == "runner" ]; then
    RUNNER_NAME=$(hostname)
    echo "Using hostname as runner name: ${RUNNER_NAME}"
fi

echo "Starting GitHub Actions Runner..."
echo "Runner Name: ${RUNNER_NAME}"
echo "Runner Labels: ${RUNNER_LABELS}"

# Check if required environment variables are set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set"
    exit 1
fi

# Determine if we're registering for an organization or a repository
if [ -n "$GITHUB_OWNER" ] && [ -n "$GITHUB_REPOSITORY" ]; then
    # Repository runner
    RUNNER_URL="https://github.com/${GITHUB_OWNER}/${GITHUB_REPOSITORY}"
    TOKEN_URL="https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPOSITORY}/actions/runners/registration-token"

elif [ -n "$GITHUB_OWNER" ]; then
    # Organization runner
    RUNNER_URL="https://github.com/${GITHUB_OWNER}"
    TOKEN_URL="https://api.github.com/orgs/${GITHUB_OWNER}/actions/runners/registration-token"
else
    echo "Error: Either GITHUB_OWNER or both GITHUB_OWNER and GITHUB_REPOSITORY must be set"
    exit 1
fi

echo "Registering runner for: ${RUNNER_URL}"

# Get a registration token from GitHub API
REGISTRATION_TOKEN=$(curl -s -X POST \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "${TOKEN_URL}" | jq -r .token)

if [ -z "$REGISTRATION_TOKEN" ] || [ "$REGISTRATION_TOKEN" == "null" ]; then
    echo "Error: Failed to get registration token from GitHub"
    echo "Please ensure GITHUB_TOKEN has the correct permissions"
    exit 1
fi

# Configure the runner
./config.sh \
    --url "${RUNNER_URL}" \
    --token "${REGISTRATION_TOKEN}" \
    --name "${RUNNER_NAME}" \
    --work "${RUNNER_WORKDIR}" \
    --labels "${RUNNER_LABELS}" \
    --unattended \
    --replace

#Cleanup function to remove runner on exit
cleanup() {
    echo "Removing runner..."
    REMOVE_TOKEN=$(curl -s -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github.v3+json" \
        "${TOKEN_URL/registration/remove}" | jq -r .token)

    ./config.sh remove --token "${REMOVE_TOKEN}"
}

trap cleanup EXIT

# Start the runner
./run.sh