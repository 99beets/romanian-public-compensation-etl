from dotenv import load_dotenv
load_dotenv()

import psycopg2
import os

# Connection configuration
conn_params = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", "5432"),
    "dbname": os.getenv("PG_DB"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PWD")
}

# File path
csv_path = r"C:/data-eng-practice/postgresql/sql-indemnizatii-nominale/data/indemnizatii_clean.csv"

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