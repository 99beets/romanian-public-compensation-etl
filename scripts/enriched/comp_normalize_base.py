import re
import pandas as pd
from pathlib import Path

INPUT = Path("data/ind-nom-table-clean.csv")
OUTPUT = Path("data/ind-nom-table-enriched.csv")

def extract_monthly_base(value: str):
    """Extract the numeric monthly base salary from text like '4,455' or '31 530'."""
    if not value or str(value).strip() == "":
        return None

    text = str(value).strip()
    if text.lower() in {"-", "n/a", "nu a fost stabilită"}:
        return None

    # Normalize separators
    text = text.replace("\xa0", " ").replace("\u202f", " ")
    text = re.sub(r"[^\d,./+\-]", "", text)

    # Case: x/y pattern
    if "/" in text:
        left = text.split("/")[0].strip()
        left_digits = re.sub(r"[^\d]", "", left)
        return int(left_digits) if left_digits.isdigit() else None

    # Otherwise: first number
    match = re.search(r"\d[\d\s,\.]*", text)
    if match:
        digits = re.sub(r"[^\d]", "", match.group(0))
        return int(digits) if digits.isdigit() else None

    return None


def compute_extra_and_total(raw: str, base: int | None):
    """Compute (extra, total) from 'suma' text."""
    if base is None or not isinstance(raw, str):
        return 0, None

    text = raw.strip()

    # Handle patterns like 'x - y'
    if "-" in text and "+" not in text:
        nums = [int(re.sub(r"[^\d]", "", m.group(0))) for m in re.finditer(r"\d[\d\s,\.]*", text)]
        if len(nums) == 2 and nums[1] > nums[0]:
            extra = nums[1] - nums[0]
            return extra, nums[1]
        return 0, None

    # Handle 'x + y' patterns
    if "+" in text:
        nums = [int(re.sub(r"[^\d]", "", m.group(0))) for m in re.finditer(r"\d[\d\s,\.]*", text)]
        if len(nums) >= 2:
            extra = sum(nums[1:])
            total = base + extra
            return extra, total

    return 0, None


def main():
    df = pd.read_csv(INPUT, dtype=str, keep_default_na=False)

    # Create numeric columns if missing
    for col in ["suma_base_num", "suma_extra_num", "suma_total_num"]:
        if col not in df.columns:
            df[col] = ""

    for idx, raw in df["suma"].items():
        base = extract_monthly_base(raw)
        extra, total = compute_extra_and_total(raw, base)

        # fallback: use suma_num if base missing
        if (base is None or base == 0) and "suma_num" in df.columns:
            try:
                base_val = int(df.at[idx, "suma_num"])
                base = base or base_val
                total = total or base_val
            except Exception:
                pass

        # ensure total at least equals base
        if total is None and base:
            total = base

        # ✅ simple addition fix — add indemnizatie_variabila_num if it exists
        if "indemnizatie_variabila_num" in df.columns:
            try:
                var_val = int(df.at[idx, "indemnizatie_variabila_num"])
                if var_val and var_val > 0:
                    total = (total or 0) + var_val
            except Exception:
                pass

        # update final values
        df.at[idx, "suma_base_num"] = str(base or 0)
        df.at[idx, "suma_extra_num"] = str(extra or 0)
        df.at[idx, "suma_total_num"] = str(total or 0)

    if "unnamed:_0" in df.columns:
        df = df.rename(columns={"unnamed:_0": "nr_crt"})

    df = df[
        [
        "nr_crt",
        "autoritate_tutelara",
        "intreprindere",
        "cui",
        "personal",
        "calitate_membru",
        "suma",
        "indemnizatie_variabila",
        "suma_base_num",
        "suma_extra_num",
        "suma_total_num",
        ]
    ]

    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"Enriched file written: {OUTPUT}")

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

if __name__ == "__main__":
    main()
