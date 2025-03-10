output "db_username" {
  description = "The master username for the RDS instance"
  value       = module.rds_instance.db_username
}

output "db_password" {
  description = "The master password for the RDS instance"
  value       = module.rds_instance.db_password
  sensitive   = true
}

output "db_endpoint" {
  description = "The connection endpoint for the RDS instance"
  value       = module.rds_instance.db_endpoint
}
