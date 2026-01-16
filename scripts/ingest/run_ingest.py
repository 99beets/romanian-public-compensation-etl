import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

STAGES = [
    ("API ingest", "scripts.ingest.ingest_api"),
    ("PDF/clean pipeline", "scripts.clean.run_pipeline_clean"),
]

def run_stage(name: str, module: str) -> None:
    print(f"\n=== Stage: {name} ===")
    print(f"Running: {module}")

    result = subprocess.run(
        [sys.executable, "-m", module],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:", result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"Stage '{name}' failed with exit code {result.returncode}")

    print(f"=== Completed: {name} ===")

def main():
    for name, script in STAGES:
        run_stage(name, script)
    
    print("\nAll ingestion stages complete.")

if __name__ == "__main__":
    main()