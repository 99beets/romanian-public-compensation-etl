import pandas as pd

# 1. Read CSV with forgiving parser
df = pd.read_csv('data/ind-nom-table.csv', engine='python', on_bad_lines='skip')

# 2. Clean column names: remove diacritics, lowercase, replace spaces and line breaks
df.columns = [c.encode('ascii', 'ignore').decode().lower().replace(' ', '_').replace('\r', '_') for c in df.columns]
print("Columns after cleaning:", df.columns)

# 3. Drop empty rows and duplicates
df = df.dropna(how='all').drop_duplicates()

# 4. Rename columns to shorter names
df = df.rename(columns={
    'unnamed_0': 'nr_crt',
    'autoritate_public_tutelar_(apt)': 'autoritate_tutelar',
    'nume_ntreprindere_public':'intreprindere',
    'cui': 'cui',
    'nume_personal_conducere': 'personal',
    'calitate_(membru_ca/cs_director/membru_directorat)': 'calitate',
    'valoare_indemnizaie_fix_lunar_conform_contract_(brut-lei)*': 'suma',
    'valoare_indemnizaie_variabila_anual_conform_contract_(brut-lei)*': 'indemnizatie_variabila'
})

# 5. Replace placeholders with empty strings
df = df.replace(['-', 'N/A', 'n/a', 'null', 'NULL'], '')

# 6. Convert to numeric (invalid = NaN)
df['suma'] = pd.to_numeric(df['suma'], errors='coerce')
df['indemnizatie_variabila'] = pd.to_numeric(df['indemnizatie_variabila'], errors='coerce')

# 7. Drop completely empty rows or duplcates
df = df.dropna(how='all').drop_duplicates()

# 8. Preview cleaned data
print(df.head())

# 9. Save cleaned file
df.to_csv('data/ind-nom-table-clean.csv', index=False, encoding='utf-8')
