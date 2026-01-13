from dotenv import load_dotenv
from pathlib import Path
import os
import psycopg2

load_dotenv()

# Connection configuration (libpq standard variables)
conn_params = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD")
}

missing = [k for k, v in conn_params.items() if v is None]
if missing:
    raise RuntimeError(f"Missing required DB env vars: {missing}")

# File path (portable, repo-relative)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
csv_path = PROJECT_ROOT / "data" / "indemnizatii_clean.csv"


# SQL commands
truncate_sql = "TRUNCATE TABLE raw.indemnizatii_clean RESTART IDENTITY;"

copy_sql = f"""
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

def truncate_table(cur):
    # Truncate the indemnizatii_clean table and reset its ID sequence
    cur.execute(truncate_sql)
    print("Table truncated successfully.")

def load_csv_to_table(cur, path):
    # Load data from local CSV into the indemnizatii_clean table
    with open(path, "r", encoding="utf-8") as f:
        cur.copy_expert(copy_sql, f)
    print("Data reloaded successfully from CSV.")

def main():
    # Pipeline entrypoint
    try:
        conn = get_connection()
        conn.autocommit = True
        cur = conn.cursor()

        truncate_table(cur)
        load_csv_to_table(cur, csv_path)
    
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()