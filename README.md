# Romanian Public Compensation Data (ETL Pipeline)

This project demonstrates an **end-to-end ETL (Extract, Transform, Load)** workflow using **Python (pandas)** and **PostgreSQL**.

The dataset represents nominal compensation payments for Romanian public institutions, extracted from an official PDF source and transformed for structured storage and analysis.

---

## Project Structure

```
scripts/
│
├── clean/                             # Stage 1 — Data Cleaning & Validation
│   ├── data_clean.py                  # Normalizes, de-duplicates, fixes column names
│   ├── data_enrich.py                 # Infers missing 'nr_crt' values from 'cui'
│   ├── validate_and_export.py         # Checks consistency, prepares CSV for PostgreSQL
│   ├── reload_indemnizatii_clean.py   # Reloads clean data into Postgres (TRUNCATE + COPY)
│   └── run_pipeline_clean.py          # Orchestrates entire cleaning workflow
│
├── enriched/                          # Stage 2 — Enrichment and inferring
│   ├── comp_normalize_base.py         # Extracts base/extra/total compensation fields
│   ├── reload_indemnizatii_enriched.py# Loads enriched dataset into Postgres
│   └── run_pipeline_enriched.py       # Full pipeline
│
└── tools/
    └── column_count_script.py         # (Legacy helper, kept for debugging)

sql/
│
├── schema/                            # Database structure definitions
│   ├── create_table_indemnizatii_clean.sql
│   └── create_table_indemnizatii_enriched.sql
│
└── queries/                           # Analytical & reporting SQL scripts
    ├── clean/
    │   ├── avg_compensation_by_role.sql
    │   ├── personnel_total_comp.sql
    │   ├── top_10_directors_by_total_compensation.sql
    │   └── top_companies_by_total_compensation.sql
    │
    └── enriched/
        ├── avg_compensation_by_role_enriched.sql
        ├── personnel_total_comp_enriched.sql
        ├── top_10_directors_by_total_compensation.sql
        └── top_companies_by_total_compensation.sql

README.md
.gitignore
```

## Pipeline Overview

### 1. Extract
Raw data exported from a government PDF (indemnizații nominale).
The ETL workflow is now split into **two modular pipelines** for flexibility:
```
| **Clean** | `scripts/clean/` | Standardizes raw data, normalizes text, validates structure, and produces `ind-nom-table-clean.csv`. |
| **Enriched** | `scripts/enriched/` | Builds on the clean output, deriving new columns like `suma_base_num`, `suma_extra_num`, and `suma_total_num`, producing `ind-nom-table-enriched.csv`. |
```
Each pipeline can run independently

### 2. Transform (Python)
- Removed malformed rows using `pandas.read_csv(..., on_bad_lines='skip')`
- Normalized column names (lowercase, underscores)
- Replaced invalid placeholders (`-`, `N/A`, `null`) with `NaN`
- Converted numeric fields to `NUMERIC`
- Saved UTF-8 cleaned CSV ready for PostgreSQL

### 3. Load (PostgreSQL)
Created a normalized table:

```
CREATE TABLE indemnizatii (
    id SERIAL PRIMARY KEY,
    nr_crt TEXT,
    autoritate_tutelara TEXT,
    intreprindere TEXT,
    cui TEXT,
    personal TEXT,
    calitate_membru TEXT,
    suma NUMERIC,
    indemnizatie_variabila NUMERIC
);
```

Loaded data using:
```
\copy indemnizatii(nr_crt, autoritate_tutelar, intreprindere, cui, personal, calitate_membru, suma, indemnizatie_variabila)
FROM 'data/ind-nom-table-clean.csv'
DELIMITER ',' CSV HEADER ENCODING 'UTF8';
```

## Data Cleaning Pipeline Update

This update refactors the **data_clean.py** script to improve consistency and safety in data ingestion:

- All columns are now loaded as **strings (`dtype=str`)**, ensuring blank cells are preserved.
Using `dtype=str` ensures that Pandas does not automatically infer numeric types, which previously converted missing integers (e.g., `1 → 1.0`).  
This preserves original formatting and avoids downstream COPY errors in PostgreSQL.
- Removed the need for `.astype(str)` conversions and `.0` cleanup.
- Added defensive normalization for column names and empty placeholders.
- Introduced `run_pipeline.py` to execute all ETL steps sequentially.
- Added `reload_indemnizatii.py` for automated reloading into PostgreSQL.
- Cleaned formatting in compensation fields to remove spacing artifacts from PDF extraction
- Kept commas in the display columns ('suma', 'indemnizatie_variabila') for readability.
- Converted numeric fields ('suma_num', 'indemnizatie_variabila_num') to integers.
Both `reload_indemnizatii_clean.py` and `reload_indemnizatii_enriched.py` now include:
- A **safe reload mechanism** that uses `TRUNCATE TABLE ... RESTART IDENTITY;` to reset the auto-incrementing primary key each time the table is refreshed.
- Clean exception handling and automatic connection closure.
- A consistent `copy_expert()` pattern for high-volume CSV imports.

    ## How to run
    ```bash
    python scripts/run_pipeline.py
    python scripts/reload_indemnizatii.py
    ```
    or
    ```bash
    python scripts/run_pipeline_enriched.py
    python scripts/reload_indemnizatii_enriched.py
    ```

### 4. Data Enrichment

Added a new script data_enrich.py for data consistency.

- Identifies rows with missing nr_crt values.

- Uses the cui (unique company identifier) to infer and fill missing sequence numbers.

- Keeps both nr_crt (original) and nr_crt_inferred (filled) columns side-by-side for transparency.

File: scripts/data_clean.py

    Run:
    ```bash
    python scripts/data_enrich.py
    ```
### 4.1 Monthly Base Salary Extraction (`suma_base_num`)

Some salary entries contain multiple numbers, such as `23316/46632` or '71000+71000 62,560'.  
In these cases, the **first number** represents the base monthly compensation.

A new script ('comp_normalize_base.py') has been added to extract this information and create a new column:

This script creates a new column:

| Column             | Meaning                                        |
|--------------------|------------------------------------------------|
| `suma_base_num`    | Monthly base salary interpreted from `suma`    |

    Run:
    ```bash
    python scripts/comp_normalize_base.py
    ```

### 5. Analysis (PostgreSQL SQL Queries)

A new 'sql/queries/' directory has been created, to provide several analytical views on the dataset.
These SQL scripts calculate totals, rankings, and averages across insitutions, personnel, and companies.

### Data Source and Use Disclaimer

This project uses publicly available data published by the Autoritatea pentru Monitorizarea și Evaluarea Performanțelor Întreprinderilor Publice (AMEPIP), Romania.

Original dataset:
https://amepip.gov.ro/wp-content/uploads/2025/08/Situatia-indemnizatiilor-nominale-IP-centrale-august-2025.pdf

The data is used strictly for educational and non-commercial purposes as part of a personal data engineering portfolio.
All personal information appearing in the dataset originates from official public disclosures made in accordance with Romanian transparency laws (Law no. 544/2001).

No attempt is made to alter, interpret, or republish personal data beyond its original context.