#!/usr/bin/env bash

# Set default PostgreSQL environment variables for local Docker development.
# Intended to be sourced, but also supports direct execution.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -euo pipefail
fi

# Local Docker Postgres defaults (can be overridden if already set)
export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGDATABASE="${PGDATABASE:-indemnizatii}"
export PGUSER="${PGUSER:-postgres}"
export PGPASSWORD="${PGPASSWORD:-postgres}"

echo "Local PostgreSQL environment variables set."
