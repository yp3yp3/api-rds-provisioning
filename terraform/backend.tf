terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
