# DBT Project: indemnizatii

This dbt project represents the analytical transformation layer of the Romanian Public Compensation ETL pipeline. It refines cleaned PostgreSQL records into business-ready models.

## Model Layers

### Staging
- stg_indemnizatii  
  Standardizes naming and exposes numeric salary fields.

### Intermediate
- int_indemnizatii_base  
  Computes total remuneration and handles null-safe numeric fields.
- int_persoane_clean  
  Produces normalized person identifiers using deterministic hashing.
- int_companii_clean  
  Normalizes company names and exposes CUI as company_id.

### Marts (Fact & Dimensions)
- fact_indemnizatii  
  Annual compensation fact table. One record = person × company × year.
- dim_persoane  
  Canonical list of persons.
- dim_companii  
  Canonical list of companies.

## Configuration
Reporting year is configured in dbt_project.yml:

vars:
  indemnizatii_year: 2025

## Running Transformations
```
dbt build
```

## Documentation
To generate documentation and lineage:
```
dbt docs generate
dbt docs serve
```