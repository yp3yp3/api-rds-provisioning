output "rds_secrets_arns" {
  value       = { for env, instance in module.rds_instance : env => instance.db_secret_arn }
  description = "ARNs of Secrets Manager entries for each RDS instance"
}
output "rds_creation_dates" {
  value = { for db_name, instance in module.rds_instance : db_name => instance.creation_date }
  description = "Creation dates of all RDS instances"
}