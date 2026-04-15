# Validate cleaned CSV output and re-export it in a safe, database-friendly format.
# Ensures structural consistency and prevents issues during PostgreSQL COPY ingestion.

import pandas as pd
import csv
from pathlib import Path

# Resolve repo root (scripts/clean/... -> project root)
BASE_DIR = Path(__file__).resolve().parents[2]

path = BASE_DIR / "data" / "indemnizatii_clean.csv"

# Load CSV with a forgiving parser to avoid breaking on minor formatting issues
df = pd.read_csv(path, dtype=str, on_bad_lines='skip', encoding='utf-8')

print(f"Loaded {len(df)} rows and {len(df.columns)} columns.\n")

# Validate raw file structure using csv.reader to detect inconsistent row lengths
# that pandas may silently tolerate or skip
print("Checking for inconsistent row lengths in raw CSV")
with open(path, encoding='utf-8', newline="") as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, start=1):
        if len(row) != len(df.columns):
            print(f"Line {i} has {len(row)} columns instead of {len(df.columns)}: {row}")

# Secondary validation inside pandas (defensive check; main structural validation is done on raw CSV)
expected_cols = len(df.columns)
invalid_rows = df[df.apply(lambda x: len(x) != expected_cols, axis=1)]
print(f"\nInvalid rows found in DataFrame: {len(invalid_rows)}")

# Re-export CSV with strict quoting and normalized line endings
# to ensure compatibility with PostgreSQL COPY ingestion
output_path = BASE_DIR / "data" / "indemnizatii_clean.csv"

df.to_csv(
    output_path,
    index=False,
    encoding='utf-8',
    quoting=csv.QUOTE_ALL,  # quote all fields to avoid delimiter/formatting issues
    lineterminator='\n'     # enforce consistent newline format across environments
)

print("\n CSV exported safely with full quoting and normalized line endings.")
print("Ready for PostgreSQL import using the \\copy command.\n")