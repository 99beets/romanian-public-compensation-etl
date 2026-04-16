SHELL := /bin/bash

# Load environment variables from .env if present (local development)
ifneq (,$(wildcard .env))
include .env
export
endif

# Docker Compose wrapper for local Postgres service
COMPOSE := docker compose -f docker/docker-compose.yml

# Declare phony targets (not file-based)
.PHONY: help up down logs psql wait-db dbt-deps dbt-run dbt-test etl etl-cloud run reset status

help:
	@echo "Targets:"
	@echo "  make up        - Start Postgres (Docker)"
	@echo "  make down      - Stop services"
	@echo "  make logs      - Tail Postgres logs"
	@echo "  make psql      - Open psql into Postgres"
	@echo "  make etl       - Run Python ETL to load data"
	@echo "	 make etl-cloud - Run Python ETL against cloud Postgres (uses .env.cloud)"
	@echo "  make dbt-run   - Run dbt models"
	@echo "  make dbt-test  - Run dbt tests"
	@echo "  make run       - End-to-end: up -> etl -> dbt-run -> dbt-test"
	@echo "  make reset     - Reset DB volume (DESTROYS DATA)"
	@echo "  make status    - Show docker compose status"

# Start local Postgres and wait until it's ready to accept connections
up:
	$(COMPOSE) up -d
	@$(MAKE) wait-db

# Stop all services
down:
	$(COMPOSE) down

# Tail Postgres container logs
logs:
	$(COMPOSE) logs -f postgres

# Show container status
status:
	$(COMPOSE) ps

# Wait for Postgres readiness using pg_isready (retry loop with timeout)
wait-db:
	@echo "Waiting for Postgres to be ready..."
	@for i in {1..30}; do \
		if $(COMPOSE) exec -T postgres pg_isready -U $${PGUSER:-postgres} -d $${PGDATABASE:-indemnizatii} >/dev/null 2>&1; then \
			echo "Postgres is ready."; exit 0; \
		fi; \
		sleep 2; \
	done; \
	echo "Postgres did not become ready in time."; exit 1

# Open interactive psql session inside container
psql:
	$(COMPOSE) exec postgres psql -U $${PGUSER:-postgres} -d $${PGDATABASE:-indemnizatii}

# ---- Project-specific commands ----

# Run ETL pipeline locally (uses local Postgres env config)
etl:
	@echo "Running ETL (local)..."
	@bash -lc 'source .venv/bin/activate && source tools/set_pg_env.sh local && python3 scripts/clean/run_pipeline_clean.py'

# Run ETL pipeline against cloud Postgres (requires .env.cloud)
etl-cloud:
	@echo "Running ETL (cloud)..."
	@bash -lc 'source .venv/bin/activate && source tools/set_pg_env.sh cloud && python3 scripts/clean/run_pipeline_clean.py'

# Install dbt dependencies
dbt-deps:
	cd dbt_project && dbt deps

# Execute dbt models (transform layer)
dbt-run:
	cd dbt_project && dbt run

# Run dbt tests for data validation
dbt-test:
	cd dbt_project && dbt test

# Full local pipeline: infra + ETL + transformations + tests
run: up etl dbt-run dbt-test
	@echo "Local quickstart complete."

# WARNING: Destroys Docker volume (data loss)
reset:
	@echo "!!! This will destroy the database volume. Continue? (Ctrl+C to cancel) !!!"
	@sleep 2
	$(COMPOSE) down -v

# Bootstrap local Python environment
bootstrap:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

# Remove generated artifacts
clean:
	rm -f data/*_clean.csv
	rm -rf __pychache__