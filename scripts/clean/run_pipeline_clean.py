import os
import platform
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = [
    "data_clean.py",
    "validate_and_export.py",
    # "upload_to_s3.py",
    "load_indemnizatii_clean_to_pg.py",
]

base = Path(__file__).parent


def print_environment_once():
    host = os.getenv("PGHOST") or os.getenv("DB_HOST") or "localhost"
    port = os.getenv("PGPORT") or os.getenv("DB_PORT") or "5432"
    dbname = os.getenv("PGDATABASE") or os.getenv("DB_NAME") or "not set"
    user = os.getenv("PGUSER") or os.getenv("DB_USER") or "not set"

    print("\n=== Runtime Environment ===")
    print(f"Python version : {platform.python_version()}")
    print(f"Executable     : {sys.executable}")
    print(f"OS             : {platform.system()} {platform.release()}")
    print("\nDatabase configuration (resolved):")
    print(f"  Host     : {host}")
    print(f"  Port     : {port}")
    print(f"  Database : {dbname}")
    print(f"  User     : {user}")
    print("============================\n")


def run(script: str):
    print(f"\n=== Running {script} ===")
    start = time.time()

    result = subprocess.run(
        [sys.executable, str(base / script)],
        cwd=str(base),
        capture_output=True,
        text=True,
    )

    elapsed = time.time() - start

    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")

    if result.stderr:
        print("! stderr:\n", result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"!!! Stage failed: {script} (after {elapsed:.1f}s)", file=sys.stderr)
        sys.exit(result.returncode)

    print(f"=== Finished {script} ({elapsed:.1f}s) ===")


def main():
    print_environment_once()

    for s in SCRIPTS:
        run(s)

    print("\nAll stages complete.")


if __name__ == "__main__":
    main()
