import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent

PIPELINE = [
    "ingest_api.py",
]

def run(script):
    print(f"\n=== Running {script} ===")
    result = subprocess.run(
        [sys.executable, str(BASE / script)],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:\n, result.stderr")

for s in PIPELINE:
    run(s)

print("\nIngestion pipeline complete.")