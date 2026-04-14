# Lightweight ingestion orchestrator that runs multiple pipeline stages
# (API + PDF/clean pipeline) as subprocesses. Each stage is executed
# sequentially and must succeed before the next one runs.

import subprocess
import sys
from pathlib import Path

# Resolve repository root to ensure all subprocesses run from a consistent working directory.
REPO_ROOT = Path(__file__).resolve().parents[2]

# Ordered list of ingestion stages.
# Each stage is executed via `python -m` and must succeed before the next runs.
STAGES = [
    ("API ingest", "scripts.ingest.ingest_api"),
    ("PDF/clean pipeline", "scripts.clean.run_pipeline_clean"),
]

# Execute a single ingestion stage as a subprocess.
# Captures stdout/stderr and raises an exception on failure to stop the pipeline.

def run_stage(name: str, module: str) -> None:
    print(f"\n=== Stage: {name} ===")
    print(f"Running: {module}")

    # Run module as a subprocess to isolate execution and capture output cleanly.
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

    # Fail fast if any stage exits with a non-zero status.
    if result.returncode != 0:
        raise RuntimeError(f"Stage '{name}' failed with exit code {result.returncode}")

    print(f"=== Completed: {name} ===")

# Execute all ingestion stages sequentially.
# Stops immediately if any stage fails.
def main():
    for name, script in STAGES:
        run_stage(name, script)
    
    # Final success message after all stages complete.
    print("\nAll ingestion stages complete.")

if __name__ == "__main__":
    main()