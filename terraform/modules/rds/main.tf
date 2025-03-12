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
resource "time_static" "creation_time" {}

resource "random_password" "db_password" {
  length  = 16
  special = true
  override_special = "!#$%^&*()-_=+[]{}|:,.<>?"
}

resource "aws_db_instance" "this" {
  identifier              = var.db_identifier
  allocated_storage       = var.environment == "prod" ? 25 : 20
  instance_class          = var.environment == "prod" ? "db.t4g.micro" : "db.t3.micro"
  engine                  = var.engine
  username                = var.db_username
  password                = random_password.db_password.result
  skip_final_snapshot     = true
  tags = {
    Name          = var.db_identifier
    Environment   = var.environment
    CreationDate  = time_static.creation_time.rfc3339  # add creation date
  }
}

resource "aws_secretsmanager_secret" "db_secret" {
  name = "rds/${var.db_identifier}"
  depends_on = [aws_db_instance.this]  # Secret will be created only after RDS is ready
}

resource "aws_secretsmanager_secret_version" "db_secret_version" {
  secret_id     = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db_password.result
    endpoint = aws_db_instance.this.endpoint
  })
}

