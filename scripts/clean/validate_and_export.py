# Validate cleaned CSV output and re-export it in a safe, database-friendly format.
# Ensures structural consistency and prevents issues during PostgreSQL COPY ingestion.

import csv
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone


# Resolve repo root (scripts/clean/... -> project root)
BASE_DIR = Path(__file__).resolve().parents[2]

input_path = BASE_DIR / "data" / "indemnizatii_clean.csv"
output_path = BASE_DIR / "data" / "indemnizatii_clean_validated.csv"

# Load CSV with a forgiving parser to avoid breaking on minor formatting issues
df = pd.read_csv(input_path, dtype=str, on_bad_lines="skip", encoding="utf-8").fillna("")

print(f"Loaded {len(df)} rows and {len(df.columns)} columns.\n")

# Validate raw file structure using csv.reader to detect inconsistent row lengths
# that pandas may silently tolerate or skip
print("Checking for inconsistent row lengths in raw CSV")
expected_cols = len(df.columns)
bad_line_count = 0

with open(input_path, encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, start=1):
        if len(row) != expected_cols:
            bad_line_count += 1
            print(f"Line {i} has {len(row)} columns instead of {expected_cols}: {row}")

print(f"\nRaw CSV rows with inconsistent column counts: {bad_line_count}")

# Emit a small data quality summary before exporting the validated CSV
print("\n=== Data Quality Summary ===")
print(f"Total rows: {len(df)}")

critical_cols = ["autoritate_tutelara", "intreprindere", "cui", "personal", "calitate_membru"]
missing_critical_cols = [col for col in critical_cols if col not in df.columns]

if missing_critical_cols:
    print(f"Missing critical columns: {missing_critical_cols}")
    sys.exit(1)

rows_with_missing_fields = df[df[critical_cols].apply(lambda x: x.str.strip().eq("").any(), axis=1)]
print(f"Rows with missing critical fields: {len(rows_with_missing_fields)}")

names_with_multiple_cui = 0

if {"personal", "cui"}.issubset(df.columns):
    person_cui_counts = (
        df.assign(
            personal_clean=df["personal"].str.strip().str.lower(),
            cui_clean=df["cui"].str.strip()
        )
        .query("personal_clean != '' and cui_clean != ''")
        .groupby("personal_clean")["cui_clean"]
        .nunique()
    )

    names_with_multiple_cui = int((person_cui_counts > 1).sum())
    print(f"Names appearing under multiple CUI values: {names_with_multiple_cui}")

blank_nr_crt = 0
if "nr_crt" in df.columns:
    blank_nr_crt = int((df["nr_crt"].str.strip() == "").sum())
    print(f"Blank nr_crt values: {blank_nr_crt}")

# Re-export CSV with strict quoting and normalized line endings
# to ensure compatibility with PostgreSQL COPY ingestion
df.to_csv(
    output_path,
    index=False,
    encoding="utf-8",
    quoting=csv.QUOTE_ALL,
    lineterminator="\n"
)

quality_dir = BASE_DIR / "logs" / "quality"
quality_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

quality_report = {
    "run_timestamp_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    "input_file": str(input_path.relative_to(BASE_DIR)),
    "output_file": str(output_path.relative_to(BASE_DIR)),
    "row_count": int(len(df)),
    "column_count": int(len(df.columns)),
    "bad_line_count": int(bad_line_count),
    "missing_critical_columns": missing_critical_cols,
    "rows_with_missing_fields": int(len(rows_with_missing_fields)),
    "names_with_multiple_cui_review_count": int(names_with_multiple_cui),
    "blank_nr_crt": int(blank_nr_crt),
    "status": "success",    
}

report_path = quality_dir / f"quality_report_{timestamp}.json"

with report_path.open("w", encoding="utf-8") as f:
    json.dump(quality_report, f, indent=2, ensure_ascii=False)

print(f"Quality report written to: {report_path}")

print("\nCSV exported safely with full quoting and normalized line endings.")
print(f"Validated file written to: {output_path}")
print("Ready for PostgreSQL import using the \\copy command.\n")
