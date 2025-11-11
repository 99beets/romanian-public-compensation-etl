import pandas as pd

# Load clean CSV
path = r"data/ind-nom-table-clean.csv"
df = pd.read_csv(path, dtype=str, keep_default_na=False)

# Ensure 'nr_crt' is stored as text and remove .0
if 'nr_crt' in df.columns:
    df['nr_crt'] = (
        df['nr_crt']
        .astype(str)
        .str.replace(r'\.0$', '', regex=True)
        .replace({'nan': '', 'None': ''})
        .str.strip()
    )

# Identify missing nr_crt and fill based on matching CUI
if 'nr_crt' in df.columns and 'cui' in df.columns:
    cui_to_nrcrt = (
        df.loc[df['nr_crt'].str.strip() != '', ['cui', 'nr_crt']]
        .drop_duplicates(subset='cui')
        .set_index('cui')['nr_crt']
        .to_dict()
    )

    df['nr_crt_inferred'] = df.apply(
        lambda row: row['nr_crt'] if row['nr_crt'].strip() != '' else cui_to_nrcrt.get(row['cui'], ''),
        axis=1
    )
else:
    print("Warning: Missing 'nr_crt' or 'cui' column - cannot infer values.")

# Make sure both are treated as text (even if empty)
df['nr_crt_inferred'] = df['nr_crt_inferred'].astype(str).replace({'nan': '', 'None': ''}).str.strip()

# Move inferred column right after nr_crt
cols = df.columns.tolist()
if 'nr_crt' in cols and 'nr_crt_inferred' in cols:
    nr_index = cols.index('nr_crt')
    # Remove and reinsert in the desire position
    cols.insert(nr_index + 1, cols.pop(cols.index('nr_crt_inferred')))
    df = df[cols]

# Compare before/after to verify changes
changed = df[(df['nr_crt'] != df['nr_crt_inferred']) & (df['nr_crt_inferred'].str.strip() != '')]
print(f"\nRows where nr_crt was inferred: {len(changed)}")
if len(changed) > 0:
    print(changed[['cui', 'nr_crt', 'nr_crt_inferred']].head(10))

# Export visualization-only version
df.to_csv("data/ind-nom-table-enriched.csv", index=False, encoding='utf-8')
print("\nEnriched file saved as data/ind-nom-enriched.csv (for visualization only).")