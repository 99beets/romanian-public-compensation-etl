#!/usr/bin/env bash
# If the script is executed (not sourced), enable strict mode
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    set -euo pipefail
fi

# Usage:
#   source tools/set_pg_env.sh            # loads .env if present
#   source tools/set_pg_env.sh cloud      # loads .env.cloud if present

MODE="${1:-local}"

ENV_FILE=".env"
if [[ "$MODE" == "cloud" ]]; then
    ENV_FILE=".env.cloud"
fi

if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
    echo "Loaded environment from $ENV_FILE"
else
    echo "Warning: $ENV_FILE not found. Using existing environment variables only."
fi

if [[ "$MODE" == "cloud" ]]; then
    echo "CLOUD MODE ENABLED — destructive operations will affect production DB"
fi

# Ensure libpq-style vars exist (defaults are LOCAL-friendly)
export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGDATABASE="${PGDATABASE:-indemnizatii}"
export PGUSER="${PGUSER:-postgres}"
export PGPASSWORD="${PGPASSWORD:-postgres}"

echo "PostgreSQL environment variables set for mode: $MODE."