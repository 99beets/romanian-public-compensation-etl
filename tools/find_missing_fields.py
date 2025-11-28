import pandas as pd

raw_path = "data/indemnizatii.csv"
clean_path = "data/indemnizatii_clean.csv"

raw = pd.read_csv(raw_path, dtype=str, keep_default_na=False, encoding="utf-8", engine="python")
clean = pd.read_csv(clean_path, dtype=str, keep_default_na=False, encoding="utf-8", engine="python")

raw_ids = set(raw["CUI"].tolist())
clean_ids = set(clean["cui"].tolist())

missing = raw_ids - clean_ids

print(f"Missing CUIs ({len(missing)}):")
print(missing)