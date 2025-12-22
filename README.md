# Romanian Public Compensation Data (ETL Pipeline)

This project demonstrates an **end-to-end ETL (Extract, Transform, Load)** workflow using **Python (pandas)** and **PostgreSQL**.

The dataset represents nominal compensation payments for Romanian public institutions, extracted from an official PDF source and transformed for structured storage and analysis.

## Running the pipeline locally

This project is designed to be runnable end-to-end in a local development environment using PostgreSQL and Python.

### Prerequisites

- Python 3.10+
- PostgreSQL (local instance)
- Git
- Virtual environment tool (venv, conda, etc.)

### Environment variables

Set the following environment variables before running the pipeline:

- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

(Example for Git Bash / Linux/macOS:)

```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=your_database
export PGUSER=you_user
export PGPASSWORD=your_password
```
## Pipeline Execution Flow

The clean ETL pipeline executes in a deterministic, linear order to ensure data quality and reproducibility.

Execution steps:

1. Validate raw CSV structure  
   Ensures column presence, ordering, and detects structural anomalies from PDF export.

2. Clean and normalize compensation data  
   Applies text cleanup, salary normalization, numeric inference, and missing key resolution.

3. Export cleaned dataset  
   Persists a stable, versionable artifact (`indemnizatii_clean.csv`) for downstream use.

4. Load cleaned data into PostgreSQL  
   Performs a full reload using TRUNCATE + COPY to guarantee idempotent runs.

Primary orchestration entrypoint:

```bash
python scripts/clean/run_pipeline_clean.py
```

Optional database reload only:
```bash
python scripts/clean/reload_indemnizatii_clean.py
```

Pipeline outputs:
- `data/indemnizatii_clean.csv` (cleaned dataset)
- PostgreSQL table `raw.indemnizatii_clean` (loaded data)

Design notes:
- The pipeline is intentionally modular to support future orchestration via AWS Lambda or scheduled jobs.
- S3 acts as the ingestion boundary between Python ETL and downstream consumers.
- dbt models are built on top of the cleaned relational layer.

---

## Project Structure

```
data/
│   indemnizatii.csv                   # Raw input data from PDF export
│   indemnizatii_clean.csv             # Cleaned output generated from ETL

scripts/
└── clean/
    data_clean.py                      # Core cleaning and normalization logic
    validate_and_export.py             # Structural validation of raw CSV
    reload_indemnizatii_clean.py       # Bulk load into PostgreSQL
    upload_to_s3.py                    # Upload cleaned dataset to S3 (ingestion boundary)
    run_pipeline_clean.py              # Orchestrates cleaning + loading process

tools/
    debug_nrcrt_inference.py           # NR_CRT inference utility
    find_missing_fields.py             # Identifies undocumented column gaps
    find_null_rows.py                  # Surface unexpected null patterns

sql/
├── schema/
│     create_table_indemnizatii_clean.sql   # DDL for PostgreSQL loading table
└── queries/
      clean/
        avg_compensation_by_role.sql
        personnel_total_comp.sql
        top_10_directors_by_total_compensation.sql
        top_companies_by_total_compensation.sql

dbt_project/
└── models/
    staging/
      stg_indemnizatii_clean.sql              # Source standardization model
      stg_indemnizatii_clean.yml              # Source-level tests

    intermediate/
      int_indemnizatii_base.sql               # Normalized salary data
      int_persoane_clean.sql                  # Deduplicated identities
      int_companii_clean.sql                  # Company mapping layer
      schema.yml                              # Tests for base/intermediate layer

    marts/
      fact_indemnizatii.sql                   # Annual compensation fact table
      dim_persoane.sql                        # Person dimension
      dim_companii.sql                        # Company dimension
      schema.yml                              
      analytics/
        distribution_companii.sql
        organization_pay_spread.sql
        top_companii_by_spend.sql
        top_earners.sql
        yearly_salary_evolution.sql
      quality/
        duplicate_person_contracts.sql

README.md
.gitignore
```

## Pipeline Overview

### 1. Extract
Data is exported manually from the official AMEPIP PDF into indemnizatii.csv.

### 2. Transform (Python)
The cleaning pipeline performs:

Column normalization
- remove diacritics
- lowercases
- replaces spaces with underscores
- collapses repeated underscores

Text cleanup
- remove PDF-artifact line breaks
- strips whitespace
- replaces placeholders (-, null, N/A) with empty string

Salary normalization
    Handles all irregular compensation formats:
    - 31 530 -> 31530
    - 23316/46632 -> 46632 (take max)
    - 71000+71000 -> 142000 (sum)
    - 5000 - 2000 -> splits into base + variable
    - preserves readable text fields (suma, indemnizatie_variabila)
    - generates safe integer columns:
        - suma_num
        - indemnizatie_variabila_num

Missing nr_crt auto-inferrence
    If a row lacks nr_crt, the pipeline fills it using satble cui -> nr_crt mapping.

### 3. Load (PostgreSQL)
Schema:
    sql/schema/create_table_indemnizatii_clean.sql

Load cleaned data:
    python scripts/clean/reload_indemnizatii_clean.py

    Performs:
        - TRUNCATE TABLE ... RESTART IDENTITY to reset primary key
        - fast COPY import
        - safe connection handling

How to Run:
```
python scripts/clean/run_pipeline_clean.py
python scripts/clean/reload_indemnizatii_clean.py
```

### 3.1 Upload (S3 – Ingestion Boundary)

After local cleaning and validation, the finalized dataset
(`indemnizatii_clean.csv`) is uploaded to Amazon S3.

This establishes S3 as a clear ingestion boundary between data preparation and downstream consumers.

Script:
```
python scripts/clean/upload_to_s3.py
```

The upload step:
- persists a versioned artifact of the cleaned dataset
- decouples Python ETL from database loading
- enables future orchestration via Lambda or scheduled jobs
- aligns with cloud-native ingestion patterns

The S3 object path follows a stable convention:
s3://<artifacts-bucket>/indemnizatii/indemnizatii_clean.csv

### 4. SQL Queries Included

Inside sql/queries/clean/ you will find useful analytical test queries, such as:
    - average compensation by role
    - personnel total compensation
    - top directors by total compensation
    - top companies ranked by aggregate compensation

These scripts are intentionally kept simple and are useful for validating the cleaned dataset before moving transformations into dbt.

### 5. DBT Integration

This project now includes a dedicated dbt transformation layer located in the dbt_project/ directory.

## DBT Transformation Layer

The `/dbt_project` directory contains the transformation logic that converts raw loaded data into an analytics-ready format.

The dbt layer produces:
- fact_indemnizatii: annual compensation dataset
- dim_persoane: normalized people dimension
- dim_companii: normalized company dimension

Execution steps:
```
cd dbt_project
dbt build
```

To generate documentation and lineage view:
```
dbt docs generate
dbt docs serve
```

The transformation is parameterized using an annual reporting variable:
```
vars:
  indemnizatii_year: 2025
```

### Analytics Models

The dbt analytics layer now includes derived models designed for reporting, ranking, and quality validation:

- distribution_companii  
  Salary distribution per institution: min, median, max, and spending totals.

- top_companii_by_spend  
  Ranks institutions by total remuneration expenditure.

- top_earners  
  Top earning individuals, based on aggregated annual compensation.

- yearly_salary_evolution  
  Year-level financial summary to support multiple-year comparisons.

- duplicate_person_contracts  
  Highlights data inconsistencies where repeated records exist for the same individual within an institution.

- organization_pay_spread  
  Computes compensation spread per organization, useful for inequality analysis.

## Pipeline Architecture
Raw CSV → Python ETL → S3 (artifacts) → PostgreSQL (RDS) → dbt → Analytics layer

## Cloud Infrastructure (Terraform)

This project includes a complete AWS deployment of the ETL pipeline using Terraform.
The infrastructure layer provides:

### S3 Storage
- `artifacts` bucket for ETL packages, metadata, and intermediate assets  
- `logs` bucket for centralized access logging  
- Versioning, encryption, and lifecycle policies

### Lambda Execution Scaffold
A deployable ETL entrypoint for future automation (e.g., EventBridge scheduled runs).

### PostgreSQL (Amazon RDS)
A managed Postgres instance used as the target for the cleaned ETL data.
Terraform provisions:
- DB subnet group
- Security group with IP-restricted inbound rules  
- Parameterized DB name, username, password  
- Outputs exposing the connection endpoint

Connect using:
```
psql -h <rds_endpoint> -U <username> -d romanian_comp
```

### IAM Roles
Least-privilege role + inline policy for Lambda to interact with S3.

### Deployment Commands
```
cd infra/terraform
terraform init
terraform apply -var-file="dev.auto.tfvars"
```

This infrastructure is intentionally minimal, focusing on:
- platform readiness  
- reproducibility  
- clean separation between compute, storage, and orchestration  

### Data Source and Use Disclaimer

This project uses publicly available data published by the Autoritatea pentru Monitorizarea și Evaluarea Performanțelor Întreprinderilor Publice (AMEPIP), Romania.

Original dataset:
https://amepip.gov.ro/wp-content/uploads/2025/08/Situatia-indemnizatiilor-nominale-IP-centrale-august-2025.pdf

The data is used strictly for educational and non-commercial purposes as part of a personal data engineering portfolio.
All personal information appearing in the dataset originates from official public disclosures made in accordance with Romanian transparency laws (Law no. 544/2001).

No attempt is made to alter, interpret, or republish personal data beyond its original context.