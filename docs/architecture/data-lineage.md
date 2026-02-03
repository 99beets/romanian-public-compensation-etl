# Data Lineage & Flow

This diagram illustrates the end-to-end data flow for the Romanian Public Compensation ETL pipeline.

```
AMEPIP PDFs
    │
    ▼
Python Ingestion
(raw file validation, retries)
    │
    ▼
Cleaning & Normalisation
(schema alignment, type coercion)
    │
    ▼
PostgreSQL (raw schema)
    │
    ▼
dbt Staging Models
    │
    ▼
dbt Intermediate Models
    │
    ▼
dbt Mart Models
(analytics-ready tables)
    │
    ▼
Anomaly Detection
(rule-based + LLM-assisted review)
```

## Notes
- OCR is used as a fallback for non-extractable PDFs.
- All pipeline runs are logged with audit metadata.
- Anomaly detection is explainable and auditable by design.
