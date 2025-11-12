locals {
  # keep names short
  name_prefix = replace(var.project_name, "/[^a-z0-9-]/", "")
}