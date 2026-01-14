import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "data_clean.py",
    "validate_and_export.py",
    # "upload_to_s3.py",
    "load_indemnizatii_clean_to_pg.py"
]

base = Path(__file__).parent

def run(script: str):
    print(f"\n=== Running {script} ===")

    result = subprocess.run(
        [sys.executable, str(base / script)],
        cwd=str(base),          # makes relative paths consistent
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("! stderr:\n", result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"!!! Stage failed: {script}", file=sys.stderr)
        sys.exit(result.returncode)

    print(f"=== Finished {script} ===")


def main():
    for s in SCRIPTS:
        run(s)

    print("\nAll stages complete.")


if __name__ == "__main__":
    main()