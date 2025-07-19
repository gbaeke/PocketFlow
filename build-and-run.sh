#!/bin/bash

# Build the Docker image for x64 platform
docker build --platform linux/amd64 -t docgen .

# extract env vars from .env as variables
if [[ -f .env ]]; then
    echo "Loading environment variables from .env file..."
    set -o allexport
    source .env
    set +o allexport
else
    echo ".env file not found. Please ensure it exists in the current directory."
    exit 1
fi

# Check if --run parameter is provided
if [[ "$1" == "--run" ]]; then
    echo "Running the container..."
    # Run the container with environment variable OPENAI_API_KEY from .env
    docker run -it -p 9997:9997 -e OPENAI_API_KEY="$OPENAI_API_KEY" docgen
else
    echo "Docker image built successfully for x64 platform. Use '--run' parameter to also run the container."
fi 