# Quick diagnostic script to inspect nr_crt inference inputs and mappings.
# Helps verify whether missing identifiers can be recovered from existing CUI -> nr_crt pairs.
import pandas as pd

# Load the same enriched file used in the identifier inference workflow
path = "data/ind-nom-table-enriched.csv"
df = pd.read_csv(path, dtype=str, keep_default_na=False)

print("=== Step 1: Basic info ===")
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
print("Columns:", list(df.columns))
print()

# Check whether nr_crt exists and how many values are blank
if "nr_crt" in df.columns:
    blanks = (df["nr_crt"].astype(str).str.strip() == "").sum()
    print(f"Blank nr_crt count: {blanks}")
else:
    print(" No column named 'nr_crt' found.")
print()

# Check whether CUI exists and how many values are blank
if "cui" in df.columns:
    blanks_cui = (df["cui"].astype(str).str.strip() == "").sum()
    print(f"Blank CUI count: {blanks_cui}")
else:
    print(" No column named 'cui' found.")
print()

# Rebuild the CUI -> nr_crt mapping to inspect how many usable lookup pairs exist
if "nr_crt" in df.columns and "cui" in df.columns:
    df["cui"] = df["cui"].astype(str).str.strip()
    cui_to_nrcrt = (
        df.loc[df["nr_crt"].str.strip() != "", ["cui", "nr_crt"]]
        .drop_duplicates(subset="cui")
        .set_index("cui")["nr_crt"]
        .to_dict()
    )
    print(f"CUI -> nr_crt mapping size: {len(cui_to_nrcrt)} entries")
    print()

    # Show a few sample mappings for quick inspection
    sample = list(cui_to_nrcrt.items())[:5]
    print("Sample mappings:", sample)
else:
    print("Skipping mapping — missing one or both columns.")
print()

print(" Debug completed.")