# Romanian Public Compensation Data (ETL Pipeline)

This project demonstrates an **end-to-end ETL (Extract, Transform, Load)** workflow using **Python (pandas)** and **PostgreSQL**.

The dataset represents nominal compensation payments for Romanian public institutions, extracted from an official PDF source and transformed for structured storage and analysis.

---

## Project Structure

```
│
├── data/
│ ├── ind-nom-table.csv
│ ├── ind-nom-table-clean.csv 
│
├── scripts/
│ ├── data_clean.py
│ ├── column_count_script.py
│ ├── validate_and_export.py
│ ├── reload_indemnizatii.py
│ ├── run_pipeline.py
│ ├── comp_normalize_base.py
│ └── data_enrich.py 
│ 
├── sql/queries/
│ ├── avg_compensation_by_role.sql
│ ├── missing_nr_crt_review.sql
│ ├── personnel_total_comp.sql
│ ├── top_10_directors_by_total_compensation.sql
│ └── top_companies_by_total_compensation.sql
│
└── README.md
```

## Process Overview

### 1. Extract
Raw data exported from a government PDF (indemnizații nominale).

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
    autoritate_tutelar TEXT,
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
- Removed the need for `.astype(str)` conversions and `.0` cleanup.
- Added defensive normalization for column names and empty placeholders.
- Introduced `run_pipeline.py` to execute all ETL steps sequentially.
- Added `reload_indemnizatii.py` for automated reloading into PostgreSQL.
- Cleaned formatting in compensation fields to remove spacing artifacts from PDF extraction
- Kept commas in the display columns ('suma', 'indemnizatie_variabila') for readability.
- Converted numeric fields ('suma_num', 'indemnizatie_variabila_num') to integers.

## Why this matters
Using `dtype=str` ensures that Pandas does not automatically infer numeric types, which previously converted missing integers (e.g., `1 → 1.0`).  
This preserves original formatting and avoids downstream COPY errors in PostgreSQL.

    ## How to run
    ```bash
    python scripts/run_pipeline.py
    python scripts/reload_indemnizatii.py
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

Some salary entries contain multiple numbers, such as `23316/46632`.  
In these cases, the first value represents the base monthly compensation.

A new script has been added to extract this value:

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