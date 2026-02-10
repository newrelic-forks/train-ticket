#!/usr/bin/env bash

echo "=========================================="
echo "Train-Ticket Infrastructure Teardown"
echo "=========================================="
echo ""
echo "This will destroy all AWS infrastructure provisioned by Terraform."
echo "This includes:"
echo "  - 4 EC2 instances (Master + 3 Workers)"
echo "  - S3 bucket and contents"
echo "  - IAM roles and policies"
echo "  - Security groups"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
  echo "Teardown cancelled."
  exit 0
fi

echo ""
echo "Starting infrastructure teardown..."
echo ""

# Change to provisioning directory and run terraform destroy
cd "$(dirname "$0")/terraform/provisioning" || exit 1

./terraform.sh destroy -auto-approve

if [ $? -eq 0 ]; then
  echo ""
  echo "=========================================="
  echo "Infrastructure teardown completed successfully!"
  echo "=========================================="
else
  echo ""
  echo "=========================================="
  echo "ERROR: Infrastructure teardown failed!"
  echo "=========================================="
  echo "Please check the error messages above and try again."
  exit 1
fi
