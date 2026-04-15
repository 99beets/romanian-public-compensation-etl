# Load cleaned CSV data into PostgreSQL using a full-reload strategy.
# Ensures schema exists, truncates target table, and bulk loads data via COPY.

from pathlib import Path
import os
import psycopg2
import sys

# Resolve project root to construct portable, repo-relative file paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

csv_path = PROJECT_ROOT / "data" / "indemnizatii_clean.csv"
ddl_path = PROJECT_ROOT / "sql" / "schema" / "create_table_indemnizatii_clean.sql"

# Ensure required input artifacts exist before proceeding
if not ddl_path.exists():
    raise FileNotFoundError(f"DDL file not found: {ddl_path}")

if not csv_path.exists():
    raise FileNotFoundError(
        f"CSV not found: {csv_path}. Did you run the cleaning/export step first?"
    )

# Build connection parameters from environment variables (libpq-compatible)
conn_params = {
    "host": os.getenv("PGHOST") or os.getenv("DB_HOST") or "localhost",
    "port": os.getenv("PGPORT") or os.getenv("DB_PORT") or os.getenv("port") or "5432",
    "dbname": os.getenv("PGDATABASE") or os.getenv("DB_NAME"),
    "user": os.getenv("PGUSER") or os.getenv("DB_USER"),
    "password": os.getenv("PGPASSWORD") or os.getenv("DB_PASSWORD")
}

required = ["host", "port", "dbname", "user"]

# Validate required connection parameters before attempting connection
missing = [k for k in required if not conn_params.get(k)]
if missing:
    raise RuntimeError(f"Missing required DB connection params: {missing}")

# Treat only explicitly local hosts as safe for destructive full-reload operations
LOCAL_HOSTS = {"localhost", "127.0.0.1", "postgres", "host.docker.internal"}
host = (conn_params["host"] or "").strip()
allow_cloud = (os.getenv("ALLOW_CLOUD_TRUNCATE") or "").strip().lower() == "true"

# Prevent destructive operations (TRUNCATE) against non-local databases
# unless explicitly allowed via environment override
if host not in LOCAL_HOSTS and not allow_cloud:
    raise RuntimeError(f"Refusing destructive operations. host={host!r}")

# Explicit warning when destructive operations are enabled for non-local environments
if host not in LOCAL_HOSTS and allow_cloud:
    print("WARNING: destructive cloud reload enabled via ALLOW_CLOUD_TRUNCATE=true", file=sys.stderr)

# Full reload strategy: remove all existing rows and reset identity sequence
truncate_sql = "TRUNCATE TABLE raw.indemnizatii_clean RESTART IDENTITY;"

# Bulk load using PostgreSQL COPY for efficient ingestion from CSV
copy_sql = """
COPY raw.indemnizatii_clean (
    nr_crt,
    autoritate_tutelara,
    intreprindere,
    cui,
    personal,
    calitate_membru,
    suma,
    indemnizatie_variabila,
    suma_num,
    indemnizatie_variabila_num
)
FROM STDIN
DELIMITER ','
CSV HEADER
ENCODING 'UTF8';
"""

# Create a new PostgreSQL connection using resolved environment configuration
def get_connection():
    return psycopg2.connect(**conn_params)

# Ensure target schema and table exist by executing DDL script
def ensure_schema(cur):
    sql = ddl_path.read_text(encoding="utf-8")
    cur.execute(sql)
    print("Schema/table ensured (DDL executed).")

# Clear target table before reload to guarantee idempotent pipeline runs
def truncate_table(cur):
    cur.execute(truncate_sql)
    print("Table truncated successfully (full reload mode).")

# Load CSV data into target table using COPY for performance and consistency
def load_csv_to_table(cur, path: Path):
    with open(path, "r", encoding="utf-8") as f:
        cur.copy_expert(copy_sql, f)
    print("Data reloaded successfully from CSV.")

# Entry point for load stage: ensures schema, truncates table, and loads fresh data
def main():
    try:
        conn = get_connection()
        conn.autocommit = True
        cur = conn.cursor()

        ensure_schema(cur)
        truncate_table(cur)
        load_csv_to_table(cur, csv_path)
    
    # Fail fast on any error and propagate non-zero exit code for pipeline orchestration
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    # Always close database resources, even if an error occurred
    finally:
        try:
            if "cur" in locals():
                cur.close()
            if "conn" in locals():
                conn.close()
        finally:
            print("Connection closed.")

if __name__ == "__main__":
    main()