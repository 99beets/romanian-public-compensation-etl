# Local Docker Environment

This folder contains Docker Compose configuration for running local development services.

## Services

### PostgreSQL
- Image: postgres:15
- Port: 5432
- Used as the local development database

## Usage

The recommended way to manage local services is via the project Makefile (from repo root).

Start services:
```bash
make up
```

Stop services:
```bash
make down
```

View logs:
```bash
make logs
```
Reset database (deletes all local data):
```bash
make reset
```