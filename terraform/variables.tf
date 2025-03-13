variable "environments" {
  description = "A map of environments to deploy"
  type        = map(object({
    environment = string
    engine        = string
  }))
  validation {
    condition     = alltrue([for e in values(var.environments) : contains(["mysql", "postgres"], e.engine)])
    error_message = "Engine must be either 'mysql' or 'postgres'."
  }  
}
