import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # repo root
RAW_PATH = BASE_DIR / "data" / "indemnizatii.csv"
CLEAN_PATH = BASE_DIR / "data" / "indemnizatii_clean.csv"

# 1. Read CSV with forgiving parser
df = pd.read_csv(
    RAW_PATH,
    dtype=str,
    keep_default_na=False,
    na_values=[],
    engine='python',
    on_bad_lines='warn'
)

print("After read_csv:", len(df))

# 2. Clean column names: remove diacritics, lowercase, replace spaces and line breaks
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

# 3. Drop empty rows
df = df.dropna(how='all')

# 4. Rename columns to shorter names
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

# 5. Clean text cells from embedded line breaks
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(r"[\r\n]+", " ", regex=True)
        .str.strip()
    )

# 6. Replace placeholders with empty strings
df = df.replace(['-', 'N/A', 'n/a', 'null', 'NULL'], '')

# 7. Normalize edge cases
def clean_numeric_text(value: str):
    """Extract the numeric monthly base salary from text like '4,455' or '31 530'."""
    if not value or str(value).strip() == '':
        return ''

    text = str(value).strip()

    if text.lower() in {'-', 'n/a', 'nu a fost stabilită'}:
        return ''

    # normalize Unicode spacing
    text = text.replace('\xa0', '').replace('\u202f', ' ')

    # Remove unwanted character but keep + - . , /
    cleaned = re.sub(r'[^\d,./+\-]', '', text)

    # Case 1: '+' pattern -> SUM all parts
    if '+' in cleaned:
        parts = cleaned.split("+")
        nums =[]

        for p in parts:
            d = re.sub(r'[^\d]', '', p)
            if d.isdigit():
                nums.append(int(d))

        if len(nums) >= 2:
            return str(sum(nums))
        
        # fallback
        return cleaned
        
    # Case 2: '/' pattern -> LARGER NUMBER
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

# 8. Create suma_num column
df["suma_num"] = (
    df["suma"]
    .apply(lambda x: re.sub(r"[^\d]", "", x) if isinstance(x, str) else "")
    .replace("", "0")
    .astype(int)
)

# 8. Create indemnizatie_variabila_num column
if "indemnizatie_variabila" in df.columns:
    df["indemnizatie_variabila_num"] = (
        df["indemnizatie_variabila"]
        .apply(lambda x: re.sub(r"[^\d]", "", x) if isinstance(x, str) else "")
        .replace("", "0")
        .astype(int)
    )

# 8. Drop empty rows
df = df.dropna(how='all')

# 9. Ensure nr_crt is string-safe
if 'nr_crt' in df.columns:
    df['nr_crt'] = (
        df['nr_crt']
        .astype(str)
        .str.replace(r'\.0$', '', regex=True)
        .str.strip()
        .replace({'nan': '', 'None': ''})
    )

# 10. Fill missing nr_crt using CUI mapping
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
    print("Warning: Missing 'nr_crt' or 'cui' column - cannot infer values.")

# 11. Preview cleaned data
print(f"Final cleaned row count: {len(df)}")
print(f"Final columns: {list(df.columns)}")

# 12. Save cleaned file
df.to_csv(CLEAN_PATH, index=False, encoding='utf-8')
print(f"Cleaned CSV saved to {CLEAN_PATH}")