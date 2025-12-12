data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_db_subnet_group" "this" {
  name       = "${local.name_prefix}-${random_id.suffix.hex}-db-subnets"
  subnet_ids = data.aws_subnets.default.ids

  tags = merge(
    var.tags,
    {
      Name = "${local.name_prefix}-db-dubnet-group"
    }
  )
}

# Security group allowing Postgres access from IP(s)
resource "aws_security_group" "rds" {
  name        = "${local.name_prefix}-${random_id.suffix.hex}-rds-sg"
  description = "Security group for RDS Postgres"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Postgres from allowed CIDRs"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.db_allowed_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_db_instance" "postgres" {
  identifier            = "${local.name_prefix}-${random_id.suffix.hex}-pg"
  engine                = "postgres"
  engine_version        = "15" # or most recent supported version in EU-West-1
  instance_class        = "db.t3.micro"
  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  port = 5432

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible     = true # dev only, locked by SG
  multi_az                = false
  storage_encrypted       = true
  backup_retention_period = 1    # keep 1 day of backup in dev
  skip_final_snapshot     = true # dev only

  deletion_protection = false # terraform destruction permition

  tags = merge(
    var.tags,
    {
      Name = "${local.name_prefix}-postgres"
    }
  )
}