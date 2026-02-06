# Runbook: AWS Infrastructure Lifecycle

This runbook describes how to safely destroy and recreate the cloud infrastructure used in this project.

All infrastructure is managed using Terraform and is intended to be fully reproducible.

---

## Scope

The infrastructure defined in this project may include:

- AWS RDS (PostgreSQL)
- S3 buckets (artifacts and ingestion boundaries)
- IAM roles and policies
- Networking components
- Lambda functions (where applicable)

Terraform configuration is located in:

infra/terraform

---

## Destroying Infrastructure

To remove all provisioned resources:

cd infra/terraform
terraform destroy

Review the execution plan carefully before confirming destruction.

---

## Pre-Destroy Checklist

Before destroying infrastructure:

1. Confirm no important data needs to be retained
2. Take database snapshots if required
3. Download any required S3 artifacts
4. Ensure no pipelines or scheduled jobs are running
5. Confirm Terraform is targeting the correct AWS account and region

---

## Verifying Destruction

After running `terraform destroy`, verify in the AWS Console:

- No EC2 instances running
- No RDS databases active
- No NAT gateways present
- No load balancers running
- No Elastic IPs allocated

Service-managed buckets (for example Elastic Beanstalk or other AWS services) may remain and can be ignored if the account is being closed.

---

## Recreating Infrastructure

To rebuild infrastructure from scratch:

cd infra/terraform
terraform init
terraform plan
terraform apply

Ensure the following are configured before applying:

- AWS credentials
- Environment variables (.env or shell environment)
- Correct AWS region

---

## Handling Terraform State Issues

If Terraform reports a state lock or initialization problem:

1. Ensure no other Terraform processes are running
2. Reinitialize the working directory:

rm -rf .terraform
terraform init

3. Retry the operation

---

## Design Principle

This project follows the principle:

Infrastructure should be disposable and reproducible at any time.

Benefits:

- Safe experimentation
- Clean environment resets
- Repeatable deployments
- Easier debugging and recovery

---

## Closing an AWS Account (Optional)

If the infrastructure was created in a dedicated AWS account:

1. Run terraform destroy where possible
2. Verify no billable resources remain
3. Close the account from AWS Account Settings

AWS may automatically clean up some service-managed resources after account closure.
