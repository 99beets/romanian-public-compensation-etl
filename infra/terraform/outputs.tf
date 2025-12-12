output "rds_endpoint" {
  description = "PostgreSQL endpoint for the ETL/dbt pipeline"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_port" {
  description = "PostgreSQL port"
  value       = aws_db_instance.postgres.port
}

output "rds_db_name" {
  description = "Database name"
  value       = aws_db_instance.postgres.db_name
}

output "rds_username" {
  description = "Master username (for reference)"
  value       = aws_db_instance.postgres.username
}