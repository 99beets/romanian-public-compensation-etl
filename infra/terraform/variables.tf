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
      project   = "romanian-public-comp-etl"
      owner     = "paul.b"
      env       = "dev"
    }
}