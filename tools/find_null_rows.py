import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv("data/ind-nom-table-clean.csv", dtype=str, keep_default_na=False)

critical_cols = ["autoritate_tutelara", "intreprindere", "cui", "personal", "calitate_membru"]
missing = df[df[critical_cols].apply(lambda x: x.eq("").any(), axis=1)]

print(f"Found {len(missing)} rows with at least one empty key field.")
print(missing.head(15).to_string(index=False))