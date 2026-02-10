#!/bin/bash

# Load environment variables from the .env file in the root of the repository
ENV_FILE="$(dirname "$0")/../../.env" # Adjust path to locate .env relative to this script

if [ -f "$ENV_FILE" ]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
else
  echo "Error: .env file not found at $ENV_FILE"
  exit 1
fi

# Change directory to the Terraform provisioning directory
cd "$(dirname "$0")" || exit 1

# Pass all arguments to the Terraform command
terraform "$@"
