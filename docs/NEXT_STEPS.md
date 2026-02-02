# Next Steps and Future Enhancements

This document outlines potential next steps for the project as the data source,
scope, or automation requirements evolve.

## Data source evolution
- Support ingestion of additional AMEPIP publications if new reporting periods are released.
- Introduce explicit `reporting_period` metadata at the ingestion layer.
- Preserve historical cleaned artifacts (e.g., S3 partitioned by period).

## Pipeline execution
- Add scheduled execution (e.g., EventBridge-triggered Lambda).
- Introduce a lightweight orchestration layer for cloud runs.
- Improve retry semantics and failure classification.

## Data modeling
- Add dbt snapshots for selected dimensions (e.g., persons, organizations).
- Extend fact tables to support multi-period comparisons.
- Enrich models with derived metrics (e.g., compensation growth, volatility).

## Data quality and observability
- Promote selected SQL sanity checks into dbt tests.
- Add row-count and checksum validation between stages.
- Emit structured pipeline metrics for monitoring.

## NLP / OCR enhancements
- Improve OCR confidence scoring and fallback rules.
- Expand NLP entity normalization for inconsistent role and organization names.
- Evaluate LLM-assisted review for anomalous compensation records.

These items are intentionally deferred to keep the current project focused,
iterative, and easy to reason about.
