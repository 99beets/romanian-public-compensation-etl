import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

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


def get_git_sha() -> str:
    """Return short git SHA if available, otherwise 'n/a'."""
    try:
        p = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(base),
            capture_output=True,
            text=True,
        )
        return p.stdout.strip() if p.returncode == 0 else "n/a"
    except Exception:
        return "n/a"

def write_run_summary(
    *,
    status: str,
    duration_s: float,
    steps: list[str],
    failed_step: str | None = None,
) -> Path:
    """Write a human-readable summary of the pipeline run."""
    REPO_ROOT = Path(__file__).resolve().parents[2]
    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sha = get_git_sha()

    host = os.getenv("PGHOST") or os.getenv("DB_HOST") or "localhost"
    port = os.getenv("PGPORT") or os.getenv("DB_PORT") or "5432"
    dbname = os.getenv("PGDATABASE") or os.getenv("DB_NAME") or "not set"
    user = os.getenv("PGUSER") or os.getenv("DB_USER") or "not set"

    failed_line = failed_step if failed_step else "n/a"

    content = f"""# Pipeline Run Summary

- Date (UTC): {ts}
- Status: {status}
- Duration: {duration_s:.1f}s
- Git SHA: {sha}

## Database (resolved)
- Host: {host}
- Port: {port}
- Database: {dbname}
- User: {user}

## Steps executed
{chr(10).join([f"- {s}" for s in steps])}

## Failure
- Failed step: {failed_line}
"""

    path = logs_dir / "run_summary.md"
    path.write_text(content, encoding="utf-8")
    return path


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
    return True, elapsed


def main():
    print_environment_once()

    steps_executed: list[str] = []
    failed_step: str | None = None
    overall_start = time.time()
    status = "Success"

    for s in SCRIPTS:
        steps_executed.append(s)
        ok, _ = run(s)
        if not ok:
            status = "Failed"
            failed_step = S
            break

    duration = time.time() - overall_start
    summary_path = write_run_summary(
        status=status,
        duration_s=duration,
        steps=steps_executed,
        failed_step=failed_step,
    )
    print(f"\nRun summary written to: {summary_path}")

    if status == "Failed":
        sys.exit(1)

    print("\nAll stages complete.")

if __name__ == "__main__":
    main()
