provider "aws" {
  region = var.aws_region
}

module "rds_instance" {
  source = "./modules/rds"

  db_identifier  = var.db_identifier
  engine         = var.engine
  environment    = var.environment
}
