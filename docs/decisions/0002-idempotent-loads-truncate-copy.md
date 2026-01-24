# ADR 0002 — Use TRUNCATE + COPY for idempotent loads during iterative development

## Status
Accepted

## Context
This project ingests compensation data extracted from an official AMEPIP PDF (currently, the August 2025 publication).

The ETL and normalization logic is actively evolving:
- PDF-to-CSV artifacts require cleanup and structural validation
- salary fields contain irregular formats that require iterative parsing rules
- missing identifiers (e.g., `nr_crt`) may require inference and backfills
- dbt models/tests are refined as the raw layer improves

During this phase, the pipeline must be easy to re-run many times while producing deterministic outputs.

## Decision
For the raw load step, the pipeline uses a full replace strategy:

1) `TRUNCATE TABLE ... RESTART IDENTITY`
2) bulk load with PostgreSQL `COPY`

This makes each ETL run idempotent: the database state after a successful run depends only on the current cleaned artifact, not on any previous runs.

## Consequences
### Benefits
- **Idempotent reruns**: repeated executions do not create duplicates
- **Deterministic state**: simplifies debugging and validation (clean slate each run)
- **Fast loads** using `COPY` (better than row inserts for bulk data)
- **dbt consistency**: downstream models/tests run against a single coherent raw snapshot

### Trade-offs / Costs
- **No automatic history** stored in the raw table across runs
- **Not ideal at large scale** if the dataset grows substantially
- Requires deliberate design later if/when multiple reporting periods need to be retained

## Alternatives considered
1) **Append-only loads**
   - Simple, but duplicates accumulate across iterative reruns

2) **Incremental/upsert loads**
   - Requires stable natural keys and a defined “what changed” signal
   - Adds complexity that is not needed for the current single-publication / iterative-cleaning phase

3) **Snapshot tables partitioned by run_id/reporting_period**
   - Preserves history
   - Better introduced once reporting cadence and identifiers are clearer

## Notes / Future evolution
If AMEPIP publishes additional datasets (new months/years), future approaches may include:
- storing cleaned artifacts in S3 by `reporting_period`
- raw tables partitioned by `reporting_period` or `run_id`
- dbt snapshots for change tracking at the dimension/fact layer
