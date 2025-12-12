variable "region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Short project name for tagging"
  type        = string
  default     = "romanian-public-comp-etl"
}

variable "tags" {
  description = "Common resource tag"
  type        = map(string)
  default = {
    project     = "romanian-public-comp-etl"
    owner       = "data-engineer"
    env         = "dev"
    cost_center = "learning"
  }
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "romanian_comp"
}

variable "db_username" {
  description = "Master username for RDS Postgres"
  type        = string
}

variable "db_password" {
  description = "Master password for RDS Postgres"
  type        = string
}

variable "db_allowed_cidrs" {
  description = "CIDR blocks allowed to connect to RDS"
  type        = list(string)
  default     = ["82.0.130.203/32"]
}