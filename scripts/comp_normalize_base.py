import re
import pandas as pd
from pathlib import Path

INPUT = Path("data/ind-nom-table-clean.csv")
OUTPUT = Path("data/ind-nom-table-enriched.csv")

def extract_monthly_base(value: str):
    """
    Extract the monthly base salary from the 'suma' text.

    Logic:
        1) If there's 'x/y' (e.g., '23316/46632'), return x.
        2) Otherwise return the first numeric sequence in the string.
        3) If no numeric content, return None.
    """

    if value is None:
        return None
    
    text = str(value).strip()
    if text == "" or text.lower() in {"-", "n/a", "nu a fost stabilită"}:
        return None
    
    # Helper: remove formatting and convert to int
    def to_int(num_str: str):
        num = re.sub(r"[^\d]", "", num_str)  # keep digits only
        return int(num) if num.isdigit() else None
    
    # Case 1: handle x/y structure
    if "/" in text:
        left = text.split("/")[0].strip()
        left_num = to_int(left)
        if left_num is not None:
            return left_num
    
    # Case 2: get first numeric substring (supports spaces, commas, periods)
    match = re.search(r"\d[\d\s,\.]*", text)
    if match:
        return to_int(match.group(0))
    
    return None


def main():
    df = pd.read_csv(INPUT, dtype=str, keep_default_na=False)

    # Create empty output column
    df["suma_base_num"] = ""

    # Fill new column row-by-row
    for idx, raw in df["suma"].items():
        base = extract_monthly_base(raw)
        df.at[idx, "suma_base_num"] = "" if base is None else str(base)

    # Save enriched file
    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"Enriched file written: {OUTPUT}")


if __name__ == "__main__":
    main()