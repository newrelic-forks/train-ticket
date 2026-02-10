# Terraform Backend Configuration
# Uncomment and configure if you want to use remote state storage

# terraform {
#   backend "s3" {
#     bucket = "your-terraform-state-bucket"
#     key    = "train-ticket/config/terraform.tfstate"
#     region = "us-east-1"
#   }
# }

# For local state storage (default), no backend configuration is needed
# State will be stored in terraform.tfstate file in this directory
