# Identify rows with missing values in critical business fields.
# Used to surface data quality issues after cleaning.

import pandas as pd
import sys

# Ensure UTF-8 output (useful for non-ASCII characters in dataset)
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv("data/ind-nom-table-clean.csv", dtype=str, keep_default_na=False)

# Columns considered essential for a valid record
critical_cols = ["autoritate_tutelara", "intreprindere", "cui", "personal", "calitate_membru"]

# Select rows where at least one critical field is empty
rows_with_missing_fields = df[df[critical_cols].apply(lambda x: x.eq("").any(), axis=1)]

print(f"Found {len(rows_with_missing_fields)} rows with at least one empty key field.")

# Display a sample of problematic rows for inspection
print(rows_with_missing_fields.head(15).to_string(index=False))