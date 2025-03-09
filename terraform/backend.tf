terraform {
  backend "s3" {
    bucket         = "tf-state-rds-234554"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
