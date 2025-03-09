variable "db_identifier" {
  type = string
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev/prod)"
}

variable "engine" {
  type        = string
  validation {
    condition     = contains(["mysql", "postgres"], var.engine)
    error_message = "Engine must be either 'mysql' or 'postgres'."
  }
}

variable "db_username" {
  type        = string
  default     = "rds_admin"
  description = "DB username (default: admin)"
}
