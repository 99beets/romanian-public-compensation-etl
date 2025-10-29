import csv

path = r'C:/data-eng-practice/postgresql/sql-indemnizatii-nominale/data/ind-nom-table-clean.csv'
with open (path, encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, start=1):
        if len(row) != 7:
            print(f"Line {i} has {len(row)} columns: {row}")