SHELL := /bin/bash

# Load env vars from .env if present
ifneq (,$(wildcard .env))
include .env
export
endif

COMPOSE := docker compose -f docker/docker-compose.yml

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

up:
	$(COMPOSE) up -d
	@$(MAKE) wait-db

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f postgres

status:
	$(COMPOSE) ps

wait-db:
	@echo "Waiting for Postgres to be ready..."
	@for i in {1..30}; do \
		if $(COMPOSE) exec -T postgres pg_isready -U $${PGUSER:-postgres} -d $${PGDATABASE:-indemnizatii} >/dev/null 2>&1; then \
			echo "Postgres is ready."; exit 0; \
		fi; \
		sleep 2; \
	done; \
	echo "Postgres did not become ready in time."; exit 1

psql:
	$(COMPOSE) exec postgres psql -U $${PGUSER:-postgres} -d $${PGDATABASE:-indemnizatii}

# ---- Project-specific commands ----

etl:
	@echo "Running ETL (local)..."
	@bash -lc 'source .venv/bin/activate && source tools/set_pg_env.sh local && python3 scripts/clean/run_pipeline_clean.py'

etl-cloud:
	@echo "Running ETL (cloud)..."
	@bash -lc 'source .venv/bin/activate && source tools/set_pg_env.sh cloud && python3 scripts/clean/run_pipeline_clean.py'

dbt-deps:
	cd dbt_project && dbt deps

dbt-run:
	cd dbt_project && dbt run

dbt-test:
	cd dbt_project && dbt test

run: up etl dbt-run dbt-test
	@echo "Local quickstart complete."

reset:
	@echo "!!! This will destroy the database volume. Continue? (Ctrl+C to cancel) !!!"
	@sleep 2
	$(COMPOSE) down -v