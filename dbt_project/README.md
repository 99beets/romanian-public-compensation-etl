# dbt Integration — Romanian Public Compensation ETL

This directory contains the **dbt (Data Build Tool)** transformation layer for the
Romanian Public Compensation ETL project.

---

## Overview

The dbt project connects to the local **PostgreSQL** database `indemnizatii`
and builds analytical models and views used for data exploration, validation,
and future cloud deployment (AWS Lambda + S3 + Terraform).

---

## Structure

models/
├── source/
│   └── sources.yml
└── warehouse/
    ├── mean_compensation_by_institution.yml
    ├── mean_compensation_by_institution.sql
    ├── avg_compensation_by_institution.sql
    └── schema/avg_compensation_by_institution.yml

DBT Enhancements (Data Validation & Utility Macros)

The dbt project has been extended with two key open-source packages that bring powerful testing and transformation utilities:

1. dbt-labs/dbt_utils

A core companion package created by the dbt Labs team.
It adds helper macros for:

Common SQL transformations (e.g., safe unions, pivoting, surrogate keys)

Easier joins and column operations

Generic testing (e.g., unique combinations, relationships, equal row counts)

Reusable logic for cross-database portability

Example usage:

{{ dbt_utils.surrogate_key(['cui', 'nr_crt']) }}


Creates a deterministic hash-based key from multiple columns.

2. metaplane/dbt_expectations (formerly calogica/dbt_expectations)

Inspired by Great Expectations, this package provides declarative data quality tests — directly in YAML.

You can express assertions like:

tests:
  - dbt_expectations.expect_column_values_to_be_between:
      min_value: 0
      max_value: 999999