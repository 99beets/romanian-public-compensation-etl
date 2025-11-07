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

def compute_extra_and_total(raw: str, base: int | None):
    """
    Return (extr, total) from 'suma' text.
    Rules (minimal & safe):

    """

    if base is None or not isinstance(raw, str):
        return 0, None

    text = raw.strip()
    if "/" in text:
        return 0, None
    if "+" not in text:
        return 0, None
    
    tokens = [(m.group(0), m.span()) for m in re.finditer(r"\d[\d\s,\.]*", text)]

    def to_int(num_str: str):
        digits = re.sub(r"[^\d]", "", num_str)
        return int(digits) if digits.isdigit() else None
    
    def is_percent(span):
        # look right for a '%'
        start, end = span
        return "%" in text[start:end+1] or (end < len(text) and text[end] == "%")
    
    def is_range(span):
        start, end = span
        left = text[max(0, start-1):start+1]
        right = text[end-1:min(len(text), end+2)]
        return "-" in left or "-" in right
    
    nums = []
    for tok, span in tokens:
        if is_percent(span) or is_range(span):
            continue
        val = to_int(tok)
        if val is not None:
            nums.append(val)

    if not nums:
        return 0, None
    
    extra = sum(nums[1:]) if len(nums) > 1 else 0
    total = (base + extra) if extra > 0 else None
    return extra, total



def main():
    df = pd.read_csv(INPUT, dtype=str, keep_default_na=False)

    # Create text output columns

    for col in ["suma_base_nume", "suma_extra_num", "suma_total_numa"]:
        if col not in df.columns:
            df[col] = ""

    # Fill new column row-by-row
    for idx, raw in df["suma"].items():
        base = extract_monthly_base(raw)
        extra, total = compute_extra_and_total(raw, base)

        df.at[idx, "suma_base_num"] = "" if base is None else str(base)
        df.at[idx, "suma_extra_num"] = "" if extra == 0 else str(extra)
        df.at[idx, "suma_total_num"] = "" if total is None else str(total)

    # Save enriched file
    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"Enriched file written: {OUTPUT}")


if __name__ == "__main__":
    main()