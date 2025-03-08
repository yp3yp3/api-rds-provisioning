variable "db_identifier" {
  type = string
}

variable "engine" {
  type        = string
  validation {
    condition     = contains(["mysql", "postgres"], var.engine)
    error_message = "Engine must be either 'mysql' or 'postgres'."
  }
}

variable "environment" {
  type = string
}
