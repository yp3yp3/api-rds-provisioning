output "db_secret_arn" {
  value       = aws_secretsmanager_secret.db_secret.arn
  description = "ARN of the stored RDS secret"
}
output "creation_date" {
  value       = aws_db_instance.this.tags["CreationDate"]
  description = "The creation date of the RDS instance"
}