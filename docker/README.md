# Local Docker Environment

This folder contains Docker Compose configuration for running local development services used by the project.

It provides a reproducible local PostgreSQL environment for running the ETL pipeline and dbt transformations.

---

## Prerequisites

- Docker + Docker Compose
- Make
- Python 3.10+
- dbt Core

> All commands below are executed from the repository root using the project Makefile.

---

## Services

### PostgreSQL
- Image: `postgres:15`
- Port: `5432`
- Purpose: Local development database

---

## Quick Start

Start the database:
```bash
make up
```

Run the Python ETL to load source data:
```bash
make etl
```

Run dbt transformations:
```bash
make dbt-run
```

Run tests:
```bash
make dbt-test
```

Run the full pipeline end-to-end:
```bash
make run
```

---

## Service Management

Stop services:
```bash
make down
```

View logs:
```bash
make logs
```

Reset database (!!! deletes all local data):
```bash
make reset
```