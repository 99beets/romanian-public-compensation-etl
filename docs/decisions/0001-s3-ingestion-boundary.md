# ADR 0001 — Use S3 as an optional ingestion boundary for cloud runs

## Status
Accepted

## Context
This project supports two execution modes:

- **Local mode**: Dockerized Postgres via `make up`, then `make etl`, then dbt models/tests.
- **Cloud mode**: Run the same ETL against a managed Postgres instance (RDS) using `make etl-cloud`.

In cloud workflows, we want a clean separation between:
1) **data preparation** (PDF/CSV validation + cleaning + normalization in Python)
2) **downstream consumption** (Postgres load + dbt transformations + analytics)

We also want the pipeline to be reproducible and debuggable: if a downstream step breaks, we should be able to re-run from a stable artifact, not re-scrape/re-clean everything.

## Decision
When running in cloud mode, the pipeline may persist the cleaned dataset artifact to S3:

- Artifact: `data/indemnizatii_clean.csv`
- S3 location convention: `s3://<artifacts-bucket>/indemnizatii/indemnizatii_clean.csv`

S3 acts as an **ingestion boundary** between the Python cleaning layer and the database/dbt layer.

Local mode can skip S3 entirely and load directly into Postgres for speed and simplicity.

## Consequences
### Benefits
- **Reproducibility**: a versionable artifact exists independently of Postgres.
- **Decoupling**: Python ETL and database/dbt steps can evolve independently.
- **Debugging**: failures in load/dbt can be retried without repeating cleaning.
- **Future orchestration**: enables scheduled/automated runs (e.g., Lambda/EventBridge) where S3 is the handoff point.

### Trade-offs / Costs
- **Extra moving part** in cloud mode (AWS credentials, bucket policies).
- **Two-step flow** for cloud (upload then load) can add complexity if not well documented.
- Requires careful handling of naming/versioning conventions to avoid overwriting artifacts unintentionally.

## Alternatives considered
1) **Load directly into RDS without S3**
   - Simpler, fewer components
   - Harder to reproduce/debug and less flexible for future orchestration

2) **Store artifacts locally only**
   - Works for local runs
   - Doesn’t support cloud orchestration patterns or team sharing
