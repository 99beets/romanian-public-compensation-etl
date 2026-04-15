# Data cleaning pipeline for messy PDF-extracted public salary data.
# Handles inconsistent formatting, text artifacts, and irregular numeric patterns
# to produce a normalized dataset suitable for loading into PostgreSQL and dbt.

import pandas as pd
import re
from pathlib import Path

# Resolve repository root to ensure consistent file paths across environments
BASE_DIR = Path(__file__).resolve().parents[2]  # repo root
RAW_PATH = BASE_DIR / "data" / "indemnizatii.csv"
CLEAN_PATH = BASE_DIR / "data" / "indemnizatii_clean.csv"

# Use a forgiving CSV parser to handle inconsistent PDF-exported structure
# (irregular delimiters, malformed rows, unexpected line breaks).
df = pd.read_csv(
    RAW_PATH,
    dtype=str,
    keep_default_na=False,
    na_values=[],
    engine='python',
    on_bad_lines='warn'
)

print("After read_csv:", len(df))

# Normalize column names to ASCII-safe, snake_case format for downstream systems
# (PostgreSQL/dbt compatibility and easier querying).
df.columns = [
    re.sub(
        r'_+', '_',  # collapse repeated underscores
        c.encode('ascii', 'ignore') # remove diacritics
        .decode()
        .lower()
        .replace(' ', '_')
        .replace('\n', '_')
        .replace('\r', '_')
        .strip('_')  # remove heading/trailing underscore
    )   
    for c in df.columns
]

print("Columns after cleaning:", df.columns)

# Drop fully empty rows introduced by malformed PDF extraction
df = df.dropna(how='all')

df = df.rename(columns={
    'nr.crt': 'nr_crt',
    'autoritate_public_tutelar_(apt)': 'autoritate_tutelara',
    'nume_ntreprindere_public':'intreprindere',
    'cui': 'cui',
    'nume_personal_conducere': 'personal',
    'calitate_(membru_ca/cs_director/membru_directorat)': 'calitate_membru',
    'valoare_indemnizaie_fix_lunar_conform_contract_(brut-lei)*': 'suma',
    'valoare_indemnizaie_variabila_anual_conform_contract_(brut-lei)*': 'indemnizatie_variabila'
})

# Remove embedded line breaks and whitespace artifacts from PDF extraction
# to ensure consistent text fields.
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(r"[\r\n]+", " ", regex=True)
        .str.strip()
    )

# Replace common placeholder values with empty strings for consistent downstream handling
df = df.replace(['-', 'N/A', 'n/a', 'null', 'NULL'], '')

# Handles multiple irregular salary formats from source data:
# - sums ("5000+2000")
# - ranges ("2000/4000")
# - mixed formatting with spaces and symbols
def clean_numeric_text(value: str):
    """Extract the numeric monthly base salary from text like '4,455' or '31 530'."""
    if not value or str(value).strip() == '':
        return ''

    text = str(value).strip()

    if text.lower() in {'-', 'n/a', 'nu a fost stabilită'}:
        return ''

    # Normalize Unicode spacing
    text = text.replace('\xa0', '').replace('\u202f', ' ')

    # Remove unwanted character but keep + - . , /
    cleaned = re.sub(r'[^\d,./+\-]', '', text)

    # Case 1: '+' pattern -> sum all numeric components
    if '+' in cleaned:
        parts = cleaned.split("+")
        nums =[]

        for p in parts:
            d = re.sub(r'[^\d]', '', p)
            if d.isdigit():
                nums.append(int(d))

        if len(nums) >= 2:
            return str(sum(nums))
        
        return cleaned
        
    # Case 2: '/' pattern -> choose the larger value (assumed max compensation)
    if '/' in cleaned:
        parts = cleaned.split("/")
        nums = []

        for p in parts:
            d = re.sub(r'[^\d]', '', p)
            if d.isdigit():
                nums.append(int(d))

        if len(nums) >= 2:
            return str(max(nums))

    return cleaned

# Split combined "base - variable" salary fields into separate columns.
# Overwrites indemnizatie_variabila when this pattern is detected.
def split_dash_into_variable(row):
    """If 'suma' looks like 'base - variable', put the part after '-'
    into 'indemnizatie_variabila' and keep the left part in 'suma'.
    Whatever was in indemnizatie_variabila is overwritten."""

    suma = row.get('suma', '')

    if isinstance(suma, str) and '-' in suma:
        parts = suma.split('-', 1) # split into left and right only once
        left_raw = parts[0].strip()
        right_raw = parts[1].strip()

        # Extract digits to make sure both sides are number-like
        left_digits = re.sub(r'[^\d]', '', left_raw)
        right_digits = re.sub(r'[^\d]', '', right_raw)

        if left_digits.isdigit() and right_digits.isdigit():
            row['suma'] = left_raw
            row['indemnizatie_variabila'] = right_raw

    return row

df = df.apply(split_dash_into_variable, axis=1)

numeric_cols = ['suma', 'indemnizatie_variabila']

for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].apply(clean_numeric_text)

# Convert cleaned salary text into integer-safe numeric columns for downstream analysis
df["suma_num"] = (
    df["suma"]
    .apply(lambda x: re.sub(r"[^\d]", "", x) if isinstance(x, str) else "")
    .replace("", "0")
    .astype(int)
)

# Create indemnizatie_variabila_num column
if "indemnizatie_variabila" in df.columns:
    df["indemnizatie_variabila_num"] = (
        df["indemnizatie_variabila"]
        .apply(lambda x: re.sub(r"[^\d]", "", x) if isinstance(x, str) else "")
        .replace("", "0")
        .astype(int)
    )

df = df.dropna(how='all')

# Ensure identifier column is consistently formatted as a string
# and remove Excel-style ".0" artifacts.
if 'nr_crt' in df.columns:
    df['nr_crt'] = (
        df['nr_crt']
        .astype(str)
        .str.replace(r'\.0$', '', regex=True)
        .str.strip()
        .replace({'nan': '', 'None': ''})
    )

# Infer missing nr_crt values using stable CUI -> nr_crt mapping
# based on rows where the identifier is already present.
if 'nr_crt' in df.columns and 'cui' in df.columns:
    # build mapping of cui -> nr_crt from rows that already have nr_crt
    cui_to_nrcrt = (
        df.loc[df['nr_crt'].str.strip() != '', ['cui', 'nr_crt']]
        .drop_duplicates(subset='cui')
        .set_index('cui')['nr_crt']
        .to_dict()
    )

    # fill missing nr_crt directly in place
    df['nr_crt'] = df.apply(
        lambda row: row['nr_crt'] if row['nr_crt'].strip() != '' else cui_to_nrcrt.get(row['cui'], ''),
        axis=1
    )
else:
    print("Warning: Missing 'nr_crt' or 'cui' column — skipping identifier inference.")

print(f"Final cleaned row count: {len(df)}")
print(f"Final columns: {list(df.columns)}")

# Persist cleaned dataset as a stable, versionable artifact for downstream processing
df.to_csv(CLEAN_PATH, index=False, encoding='utf-8')
print(f"Cleaned CSV saved to {CLEAN_PATH}")
