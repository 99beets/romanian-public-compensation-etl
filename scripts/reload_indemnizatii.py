import psycopg2
import os

conn_params = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", "5432"),
    "dbname": os.getenv("PG_DB"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PWD")
}

# Path to clean CSV
csv_path = r"C:/data-eng-practice/postgresql/sql-indemnizatii-nominale/data/ind-nom-table-clean.csv"

# SQL commands

truncate_sql = "TRUNCATE TABLE indemnizatii;"

copy_sql = f"""
COPY indemnizatii (
nr_crt, 
autoritate_tutelar, 
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

try:
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(truncate_sql)
    print("Table truncated successfully.")

    with open(csv_path, 'r', encoding='utf-8') as f:
        cur.copy_expert(copy_sql, f)
    print("Data reloaded succsessfully from CSV.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()