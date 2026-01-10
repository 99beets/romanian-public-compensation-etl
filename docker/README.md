# Local Docker Environment

This folder contains Docker configuration for running the project locally in a containerized environment.

## Services

### PostgreSQL
- Image: postgres:15
- Port: 5432
- Used as the local data 

## Usage

Start services:

```bash
docker-compose up -d
```
Stop services:

```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

Reset data (!!deletes database!!)
```bash
docker compose down -v
```