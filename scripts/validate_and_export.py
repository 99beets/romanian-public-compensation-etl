import pandas as pd
import csv

path = r'C:/data-eng-practice/postgresql/sql-indemnizatii-nominale/data/ind-nom-table-clean.csv'
df = pd.read_csv(path, on_bad_lines='skip', encoding='utf-8')

print(f"Loaded {len(df)} rows and {len(df.columns)} columns.\n")

# Validate with csv.reader (raw file check)
print("Checking for inconsistent row lengths in raw CSV")
with open(path, encoding='utf=-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, start=1):
        if len(row) != len(df.columns):
            print(f"Line {i} has {len(row)} columns instead of {len(df.columns)}: {row}")

# Validate inside pandas
expected_cols = len(df.columns)
invalid_rows = df[df.apply(lambda x: len(x) != expected_cols, axis=1)]
print(f"\n Invalid rows found in DataFrame: {len(invalid_rows)}")

# Export safely with quoting and normalized newlines
output_path = r'C:/data-eng-practice/postgresql/sql-indemnizatii-nominale/data/ind-nom-table-clean.csv'

df.to_csv(
    output_path,
    index=False,
    encoding='utf-8',
    quoting=csv.QUOTE_ALL, # csv.QUOTE_ALL -> ensures all fields are quoted properly
    lineterminator='\n'   # ensures consistent newlines
)

print("\n CSV exported safely with full quoting and normalized line endings.")
print("Ready for PostgreSQL impot using the \\copy command.\n")