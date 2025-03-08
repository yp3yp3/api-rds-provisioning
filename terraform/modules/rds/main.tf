terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "aws_db_instance" "this" {
  identifier              = var.db_identifier
  allocated_storage       = var.environment == "prod" ? 25 : 20
  instance_class          = var.environment == "prod" ? "db.t4g.micro" : "db.t3.micro"
  engine                  = var.engine
  username                = var.db_username
  password                = random_password.db_password.result
  skip_final_snapshot     = true
}
