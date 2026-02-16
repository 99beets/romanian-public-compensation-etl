from pathlib import Path
import os
import psycopg2
import sys

# File path (portable, repo-relative)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

csv_path = PROJECT_ROOT / "data" / "indemnizatii_clean.csv"
ddl_path = PROJECT_ROOT / "sql" / "schema" / "create_table_indemnizatii_clean.sql"

if not ddl_path.exists():
    raise FileNotFoundError(f"DDL file not found: {ddl_path}")

if not csv_path.exists():
    raise FileNotFoundError(
        f"CSV not found: {csv_path}. Did you run the cleaning/export step first?"
    )

# Connection configuration (libpq standard variables)
conn_params = {
    "host": os.getenv("PGHOST") or os.getenv("DB_HOST") or "localhost",
    "port": os.getenv("PGPORT") or os.getenv("DB_PORT") or os.getenv("port") or "5432",
    "dbname": os.getenv("PGDATABASE") or os.getenv("DB_NAME"),
    "user": os.getenv("PGUSER") or os.getenv("DB_USER"),
    "password": os.getenv("PGPASSWORD") or os.getenv("DB_PASSWORD")
}

required = ["host", "port", "dbname", "user"]
missing = [k for k in required if not conn_params.get(k)]
if missing:
    raise RuntimeError(f"Missing required DB connection params: {missing}")

LOCAL_HOSTS = {"localhost", "127.0.0.1", "postgres", "host.docker.internal"}
host = (conn_params["host"] or "").strip()
allow_cloud = (os.getenv("ALLOW_CLOUD_TRUNCATE") or "").strip().lower() == "true"

if host not in LOCAL_HOSTS and not allow_cloud:
    raise RuntimeError(f"Refusing destructive operations. host={host!r}")

if host not in LOCAL_HOSTS and allow_cloud:
    print("WARNING: cloud truncate enabled via ALLOW_CLOUD_TRUNCATE=true", file=sys.stderr)

truncate_sql = "TRUNCATE TABLE raw.indemnizatii_clean RESTART IDENTITY;"

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

def get_connection():
    # Establish and return a PostgreSQL connection
    return psycopg2.connect(**conn_params)

def ensure_schema(cur):
    sql = ddl_path.read_text(encoding="utf-8")
    cur.execute(sql)
    print("Schema/table ensured (DDL executed).")

def truncate_table(cur):
    # Truncate the indemnizatii_clean table and reset its ID sequence
    cur.execute(truncate_sql)
    print("Table truncated successfully.")

def load_csv_to_table(cur, path: Path):
    with open(path, "r", encoding="utf-8") as f:
        cur.copy_expert(copy_sql, f)
    print("Data reloaded successfully from CSV.")

def main():
    # Pipeline entrypoint
    try:
        conn = get_connection()
        conn.autocommit = True
        cur = conn.cursor()

        ensure_schema(cur)
        truncate_table(cur)
        load_csv_to_table(cur, csv_path)
    
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

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