provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket         = "tf-state-rds-234554"
    key            = "default/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
