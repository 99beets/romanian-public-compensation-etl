# ADR-004: Local-First Development Strategy (with Cloud Parity)

- **Status:** Accepted
- **Date:** 2026-02-28
- **Decision owner:** Project maintainer
- **Context:** Romanian Public Compensation ETL

## Context

This project must be easy to run end-to-end for contributors and reviewers without requiring AWS access or incurring cloud costs.

The repository supports both:
- **Local execution** using Docker Compose for PostgreSQL + Python ETL + dbt.
- **Cloud execution** against a managed PostgreSQL instance (e.g., RDS) using environment variables.

The README already documents that local runs should work without manual DB environment variables, while cloud runs require `PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD`. :contentReference[oaicite:1]{index=1}

## Decision

We adopt a **Local-First Development Strategy**:

1. **Default workflow is local**
   - Docker Compose provides local PostgreSQL.
   - Python ingestion/cleaning runs locally.
   - dbt transformations run locally against the Docker DB.

2. **Cloud is optional and used for parity checks**
   - Cloud execution is used for integration validation, infrastructure testing, and deployment readiness.
   - Cloud connectivity is enabled via environment variables and example env files.

3. **Environment separation is explicit**
   - Local development uses Docker defaults and local `.env` examples (no hard dependency on secrets).
   - Cloud uses `.env.cloud.example` style configuration and explicit `PG*` variables.

## Alternatives Considered

### A) Cloud-first development (always use RDS)
**Rejected** because:
- Adds cost and slows iteration.
- Requires AWS credentials and networking setup for every contributor/reviewer.
- Increases friction for quick testing and CI.

### B) Dual-first (no default; equal emphasis)
**Rejected** because:
- Creates ambiguity in the “golden path”.
- Increases maintenance burden and documentation complexity.

## Consequences

### Positive
- **Fast iteration loop** (local runs are quick and deterministic).
- **Low contributor friction** (no AWS required to run the pipeline end-to-end).
- **Clear reproducibility** (Docker + Makefile style commands provide consistent local setup).
- **Cloud readiness remains** (parity path exists via explicit env vars).

### Negative / Trade-offs
- Local PostgreSQL behavior may differ slightly from managed Postgres defaults (extensions, parameter groups).
- Requires discipline to periodically validate cloud parity.
- Two execution modes increase documentation surface area.

## Implementation Notes

- Maintain a single “golden path” in README for local execution.
- Keep cloud configuration isolated to:
  - `.env.cloud.example`
  - Terraform under `infra/terraform`
  - `PG*` variables documented for cloud-only runs
- Prefer automation (Makefile targets) to reduce drift between local and cloud workflows.

## Follow-ups

- Add/maintain a short checklist for parity validation (e.g., “run pipeline against cloud DB once per milestone”).
- Consider adding a CI job that runs dbt tests against a containerized Postgres service to enforce local reproducibility.