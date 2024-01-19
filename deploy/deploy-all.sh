#!/bin/bash

# Directory containing the .yml files
DIR="docker-swarm"

# Iterate over each .yml file in the specified directory
for file in "$DIR"/*.yml; do
    # Extract the base name without the .yml extension
    base_name=$(basename "$file" .yml)

    # Deploy using the base name
    python3 deploy.py "$base_name" --key ~/.ssh/docker-swarm-acct2.pem
done

