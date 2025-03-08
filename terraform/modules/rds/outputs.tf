output "db_instance_endpoint" {
  value       = aws_db_instance.this.endpoint
  description = "RDS Endpoint"
}

output "db_generated_password" {
  value       = random_password.db_password.result
  description = "Auto-generated DB password"
  sensitive   = true
}
