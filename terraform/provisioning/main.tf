variable "AWS_ACCOUNT_ID" {}
variable "AWS_REGION" {}
variable "AWS_ACCESS_KEY_ID" {}
variable "AWS_SECRET_ACCESS_KEY" {}
variable "AWS_OWNING_TEAM" {}
variable "AWS_INSTANCE_PREFIX" {}
variable "AWS_KEY_PAIR" {}
variable "NEW_RELIC_LICENSE_KEY" {}
variable "NEW_RELIC_API_KEY" {}
variable "NEW_RELIC_ACCOUNT_ID" {}
variable "NEW_RELIC_REGION" {}
variable "NEW_RELIC_BROWSER_KEY" {}
variable "GITHUB_USERNAME" {}
variable "GITHUB_PAT" {}

locals {
  aws_account_id = var.AWS_ACCOUNT_ID
  tags = {
    environment = "production"
    owning_team = var.AWS_OWNING_TEAM
    product     = "TrainTicket"
  }
}

provider "aws" {
  region     = var.AWS_REGION
  access_key = var.AWS_ACCESS_KEY_ID
  secret_key = var.AWS_SECRET_ACCESS_KEY

  default_tags {
    tags = local.tags
  }
  assume_role {
    role_arn = "arn:aws:iam::${local.aws_account_id}:role/resource-provisioner"
  }
}
