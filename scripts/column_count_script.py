import csv

path = r'C:/data-eng-practice/postgresql/sql-indemnizatii-nominale/data/ind-nom-table-clean.csv'
with open (path, encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, start=1):
        if len(row) != 7:
            print(f"Line {i} has {len(row)} columns: {row}")

df.to_csv(
    'data/ind-nom-table-clean.csv'
    index=False,
    encoding='utf-8',
    quoting=1,           # csv.QUOTE_ALL -> ensures all fields are quoted properly
    line_terminator='\n' # ensures consistent newlines
)

expected_cols = len(df.columns)
invalid_rows = df[df.apply(lambda x: len(x) != expected_cols, axis=1)]
print(f"Invalid rows: {len(invalid_rows)}")