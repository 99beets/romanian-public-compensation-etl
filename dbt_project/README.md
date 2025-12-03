DBT Project: indemnizatii

This folder contains the dbt transformation layer for the Romanian Public Compensation ETL.

Models

   - stg_indemnizatii_clean
     Staging layer that standardizes all fields and exposes cleaned numeric columns.

Sources

   - public.indemnizatii_clean
     Clean table loaded by the Python ETL pipeline.

Running
```
dbt build
```