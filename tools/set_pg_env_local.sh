#!/usr/bin/env bash
set -euo pipefail

# Local Docker Postgres defaults
export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGDATABASE="${PGDATABASE:-indemnizatii}"
export PGUSER="${PGUSER:-postgres}"
export PGPASSWORD="${PGPASSWORD:-postgres}"

echo "Local PostgreSQL environment variables set."