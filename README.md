# Romanian Public Compensation Data (ETL Pipeline)

This project demonstrates an **end-to-end ETL (Extract, Transform, Load)** workflow using **Python (pandas)** and **PostgreSQL**.

The dataset represents nominal compensation payments for Romanian public institutions, extracted from an official PDF source and transformed for structured storage and analysis.

---

## Project Structure

```
data/
│   indemnizatii.csv               # Raw input data
│   indemnizatii_clean.csv         # Cleaned output (generated)

scripts/
└── clean/
    ├── data_clean.py              # Core cleaning and normalization logic
    ├── validate_and_export.py     # CSV structure validation
    ├── reload_indemnizatii_clean.py   # Load cleaned data into PostgreSQL
    └── run_pipeline_clean.py      # Orchestrates the pipeline

tools/
    debug_nrcrt_inference.py
    find_missing_fields.py
    find_null_rows.py

sql/
├── schema/
│     create_table_indemnizatii_clean.sql
│
└── queries/
      clean/
        avg_compensation_by_role.sql
        personnel_total_comp.sql
        top_10_directors_by_total_compensation.sql
        top_companies_by_total_compensation.sql

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

## Pipeline Architecture
Raw CSV → Python ETL → Postgres (indemnizatii_clean) → DBT staging → Analytics layer

### Data Source and Use Disclaimer

This project uses publicly available data published by the Autoritatea pentru Monitorizarea și Evaluarea Performanțelor Întreprinderilor Publice (AMEPIP), Romania.

Original dataset:
https://amepip.gov.ro/wp-content/uploads/2025/08/Situatia-indemnizatiilor-nominale-IP-centrale-august-2025.pdf

The data is used strictly for educational and non-commercial purposes as part of a personal data engineering portfolio.
All personal information appearing in the dataset originates from official public disclosures made in accordance with Romanian transparency laws (Law no. 544/2001).

No attempt is made to alter, interpret, or republish personal data beyond its original context.