provider "aws" {
  region = var.aws_region
}

module "rds_instance" {
  source = "./modules/rds"
  
  for_each = var.environments

  db_identifier  = each.key
  engine         = each.value.engine
  environment    = each.value.environment
}

