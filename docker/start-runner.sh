#!/bin/bash

set -e

echo "Starting GitHub Actions Runner..."
echo "Runner Name: ${RUNNER_NAME}"
echo "Runner Labels: ${RUNNER_LABELS}"

# Check if required environment variables are set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set"
    exit 1
fi

# Validate token format (should start with ghp_, gho_, ghs_, or github_pat_)
if [[ ! "$GITHUB_TOKEN" =~ ^(ghp_|gho_|ghs_|github_pat_) ]]; then
    echo "Warning: GITHUB_TOKEN does not appear to be a valid GitHub token format"
    echo "Expected to start with ghp_, gho_, ghs_, or github_pat_"
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
RESPONSE=$(curl -s -X POST \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "${TOKEN_URL}")

REGISTRATION_TOKEN=$(echo "$RESPONSE" | jq -r .token)

if [ -z "$REGISTRATION_TOKEN" ] || [ "$REGISTRATION_TOKEN" == "null" ]; then
    echo "Error: Failed to get registration token from GitHub"
    echo "API Response: $RESPONSE"
    echo "Please ensure GITHUB_TOKEN has the correct permissions"
    exit 1
fi

echo "Successfully obtained registration token"

# Configure the runner
echo "Configuring runner..."
if ./config.sh \
    --url "${RUNNER_URL}" \
    --token "${REGISTRATION_TOKEN}" \
    --name "${RUNNER_NAME}" \
    --work "${RUNNER_WORKDIR}" \
    --labels "${RUNNER_LABELS}" \
    --unattended \
    --replace \
    --disableupdate; then
    echo "Runner configured successfully"
else
    echo "Error: Failed to configure runner"
    exit 1
fi

#Cleanup function to remove runner on exit
cleanup() {
    echo "Removing runner..."

    # Get removal token
    REMOVE_RESPONSE=$(curl -s -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Accept: application/vnd.github.v3+json" \
        "${TOKEN_URL/registration/remove}")

    REMOVE_TOKEN=$(echo "$REMOVE_RESPONSE" | jq -r .token)

    if [ -z "$REMOVE_TOKEN" ] || [ "$REMOVE_TOKEN" == "null" ]; then
        echo "Warning: Failed to get removal token"
        echo "Runner may need to be manually removed from GitHub"
    else
        if ./config.sh remove --token "${REMOVE_TOKEN}"; then
            echo "Runner successfully removed"
        else
            echo "Warning: Failed to remove runner configuration"
        fi
    fi
}

trap cleanup EXIT

# Start the runner
echo "Starting runner process..."
set +e  # Disable exit on error to capture detailed exit info
./run.sh &
RUNNER_PID=$!

if [ -z "$RUNNER_PID" ]; then
    echo "Error: Failed to start runner process"
    exit 1
fi

echo "Runner started with PID: $RUNNER_PID"
echo "Runner is now active and waiting for jobs..."

# Wait for the runner process
wait $RUNNER_PID
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "Error: Runner process exited with code: $EXIT_CODE"
else
    echo "Runner process completed normally"
fi

exit $EXIT_CODE
