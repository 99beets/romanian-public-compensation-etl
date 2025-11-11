import pandas as pd
import re

# 1. Read CSV with forgiving parser
df = pd.read_csv(
    'data/ind-nom-table.csv',
    dtype=str,
    keep_default_na=False,
    na_values=[],
    engine='python',
    on_bad_lines='skip'
)

# 2. Clean column names: remove diacritics, lowercase, replace spaces and line breaks
df.columns = [
    re.sub(r'_+', '_',  # collapse repeated underscores
        c.encode('ascii', 'ignore').decode() # remove diacritics
        .lower()
        .replace(' ', '_')
        .replace('\n', '_')
        .replace('\r', '_')
        .strip('_'))    # remove /headingtrailing underscore
        for c in df.columns]

print("Columns after cleaning:", df.columns)

# 3. Drop empty rows and duplicates
df = df.dropna(how='all').drop_duplicates()

# 4. Rename columns to shorter names
df = df.rename(columns={
    'unnamed_0': 'nr_crt',
    'autoritate_public_tutelar_(apt)': 'autoritate_tutelara',
    'nume_ntreprindere_public':'intreprindere',
    'cui': 'cui',
    'nume_personal_conducere': 'personal',
    'calitate_(membru_ca/cs_director/membru_directorat)': 'calitate_membru',
    'valoare_indemnizaie_fix_lunar_conform_contract_(brut-lei)*': 'suma',
    'valoare_indemnizaie_variabila_anual_conform_contract_(brut-lei)*': 'indemnizatie_variabila'
})

if 'nr_crt' in df.columns:
    df['nr_crt'] = df['nr_crt'].astype(str)

# 5. Clean text cells from embedded line breaks
for col in df.select_dtypes(include=['object']).columns:
    df[col] = df[col].astype(str).apply(lambda x: re.sub(r'[\r\n]+', ' ', x.strip()))

# 6. Replace placeholders with empty strings
df = df.replace(['-', 'N/A', 'n/a', 'null', 'NULL'], '')

# 7. Clean numeric columns (suma and indemnizatie_variabila)
for col in ['suma', 'indemnizatie_variabila']:
    # Keep the original column text (for traceability) and remove spaces inside numbers
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(r'(?<=\d)\s+(?=\d)', '', regex=True)
        .str.strip()
               
    )

    # Create a parallel numeric-safe column
    safe_col = f"{col}_num"
    df[safe_col] = (
        df[col]
        .str.replace(r'[\s.,]', '', regex=True)     # remove thousand separators
        .str.replace(r'[^\d\-]', '', regex=True)    # remove any leftover symbols
        .replace(['', '-', 'nan', 'NaN'], '0')
    )
    df[safe_col] = pd.to_numeric(df[safe_col], errors='coerce').fillna(0).astype(int)

# 8. Drop completely empty rows or duplcates
df = df.dropna(how='all').drop_duplicates()

# 9. Ensure nr_crt is string-safe
if 'nr_crt' in df.columns:
    df['nr_crt'] = (
        df['nr_crt']
        .astype(str)
        .str.replace(r'\.0$', '', regex=True)
        .str.strip()
        .replace({'nan': '', 'None': ''})
    )

# 10. Preview cleaned data
print(df.head())

# 11. Save cleaned file
df.to_csv('data/ind-nom-table-clean.csv', index=False, encoding='utf-8')