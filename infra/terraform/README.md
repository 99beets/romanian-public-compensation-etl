This directory provisions:
- Lambda compute scaffold for ETL
- S3 artifacts/logs buckets with encryption + versioning
- IAM execution roles
- Randomized suffixes for env separation

Deploy:
```
    terraform init
    terraform plan
    terraform apply
```
Destroy:
```
    terraform destroy
```

NOTE: DB layer and ECS scheduled execution will be added later.