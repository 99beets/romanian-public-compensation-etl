# Quick diagnostic script to detect malformed rows in a CSV file
# by checking for inconsistent column counts.

import csv

# NOTE: Hardcoded path for ad-hoc debugging — update as needed
path = r'C:/data-eng-practice/postgresql/sql-indemnizatii-nominale/data/ind-nom-table-clean.csv'

with open(path, encoding='utf-8') as f:
    reader = csv.reader(f)
    
    # Expected number of columns in a valid row
    EXPECTED_COLS = 10
    
    # Print rows that deviate from expected structure
    for i, row in enumerate(reader, start=1):
        if len(row) != EXPECTED_COLS:
            print(f"Line {i} has {len(row)} columns: {row}")