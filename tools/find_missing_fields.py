# Compare raw vs cleaned datasets to identify records lost during processing.
# Specifically checks for CUIs present in raw data but missing after cleaning.

import pandas as pd

raw_path = "data/indemnizatii.csv"
clean_path = "data/indemnizatii_clean.csv"

# Load raw and cleaned datasets using consistent parsing settings
raw = pd.read_csv(raw_path, dtype=str, keep_default_na=False, encoding="utf-8", engine="python")
clean = pd.read_csv(clean_path, dtype=str, keep_default_na=False, encoding="utf-8", engine="python")

# Extract unique identifiers from both datasets
# Note: raw uses 'CUI' while cleaned dataset uses normalized 'cui'
raw_ids = set(raw["CUI"].tolist())
clean_ids = set(clean["cui"].tolist())

# Identify CUIs that were present in raw data but did not make it into the cleaned dataset
missing = raw_ids - clean_ids

print(f"Missing CUIs ({len(missing)}):")
print(missing)