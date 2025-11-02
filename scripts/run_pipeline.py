# run_pipeline.py
import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "data_clean.py",
    "column_count_script.py",
    "validate_and_export.py"
]

base = Path(__file__).parent

def run(script):
    print(f"\n=== Running {script} ===")
    result = subprocess.run(
        [sys.executable, str(base/script)],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print("! sderr:\n", result.stderr)
    print(f"=== Finished {script} ===")

for s in SCRIPTS:
    run(s)

print("\n All stages complete.")