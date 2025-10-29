# Romanian Public Compensation Data (ETL Pipeline)

This project demonstrates an **end-to-end ETL (Extract, Transform, Load)** workflow using **Python (pandas)** and **PostgreSQL**.

The dataset represents nominal compensation payments for Romanian public institutions, extracted from an official PDF source and transformed for structured storage and analysis.

---

## 🧩 Project Structure

│
├── data/
│ ├── ind-nom-table.csv # raw data extracted from PDF
│ ├── ind-nom-table-clean.csv # cleaned data (UTF-8, consistent schema)
│
├── scripts/
│ ├── data_clean.py # cleaning and preprocessing script
│ ├── column_count_script.py # column validation helper
│
├── PostgreSQL/
│ ├── create_table.sql # schema definition
│ ├── load_data.sql # COPY command
│
└── README.md

## 🧠 Process Overview

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

Loaded data using:

\copy indemnizatii(nr_crt, autoritate_tutelar, intreprindere, cui, personal, calitate_membru, suma, indemnizatie_variabila)
FROM 'data/ind-nom-table-clean.csv'
DELIMITER ',' CSV HEADER ENCODING 'UTF8';
