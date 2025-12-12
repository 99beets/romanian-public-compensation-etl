# Infrastructure as Code (Terraform)

This directory provisions the cloud resources required for running the
Romanian Public Compensation ETL pipeline.

## Components Deployed

### Amazon S3
- **Artifacts bucket** for storing ETL assets (ZIPs, metadata)
- **Logs bucket** for S3 access logs
- Server-Side Encryption (AES256)
- Versioning enabled
- Public access fully blocked
- Lifecycle rules for tiering older logs

### AWS Lambda (ETL entrypoint scaffold)
- Deploys a packaged ZIP build
- Uses IAM role with S3 read/write permissions
- Can be extended later to orchestrate cleaning & loading

### Amazon RDS (PostgreSQL)
- Postgres instance (`db.t3.micro`)
- Dedicated DB subnet group using default VPC subnets
- Security group restricted to `db_allowed_cidrs`
- Outputs exposed:
  - endpoint
  - port
  - database name
  - username

### IAM
- Execution role for Lambda
- Custom inline policies for S3 access

### Randomized suffixes
Resources use a small random hex suffix to avoid name collisions between
development environments.

---

## Deploying the Infrastructure

```
terraform init
terraform plan
terraform apply
```

`dev.auto.tfvars` contains environment-specific values such as:
- `db_username`
- `db_password`
- `db_allowed_cidrs`

Terraform automatically loads `*.auto.tfvars` files.

---

## Destroying the Environment
```
terraform destroy
```

This tears down:
- RDS instance
- Security groups
- S3 buckets
- Lambda function
- Role + policies

NOTE: RDS deletion takes several minutes.

---

## Architecture Overview

Terraform now provides the full cloud runtime for the ETL:

Local Python ETL → S3 Artifacts → Lambda (optional automation)
->
RDS PostgreSQL ← Security Group + Subnet Group


Future enhancements:
- EventBridge scheduled ETL runs
- Secrets Manager for credential rotation
- CloudWatch metrics & alarms