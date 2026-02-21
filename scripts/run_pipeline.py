import os
import platform
import subprocess
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Repo paths
REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
LOGS_DIR = REPO_ROOT / "logs"

# Environment checks
def has_db_config() -> bool:
    host = os.getenv("PGHOST") or os.getenv("DB_HOST")
    dbname = os.getenv("PGDATABASE") or os.getenv("DB_NAME")
    user = os.getenv("PGUSER") or os.getenv("DB_USER")
    return bool(host and dbname and user)


def has_aws_creds() -> bool:
    return bool(
        (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
        or os.getenv("AWS_PROFILE")
    )

# Pipeline stage selection
def build_scripts() -> list[Path]:
    # Note: adjust these paths if stage scripts are moved.
    stages = [
        SCRIPTS_DIR / "clean" / "data_clean.py",
        SCRIPTS_DIR / "clean" / "validate_and_export.py",
        SCRIPTS_DIR / "clean" / "load_indemnizatii_clean_to_pg.py",
    ]

    upload_enabled = os.getenv("PIPELINE_UPLOAD") == "1"
    upload_stage = SCRIPTS_DIR / "clean" / "upload_to_s3.py"

    if upload_enabled and has_aws_creds():
        stages.append(upload_stage)
    elif upload_enabled and not has_aws_creds():
        print(
            "!!! PIPELINE_UPLOAD=1 but AWS credentials not found. Skipping upload.",
            file=sys.stderr,
        )

    return stages

# Logging / summary helpers
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
    try:
        p = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_ROOT),
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
    steps: list[Path],
    failed_step: Path | None = None,
) -> Path:
    LOGS_DIR.mkdir(exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sha = get_git_sha()

    host = os.getenv("PGHOST") or os.getenv("DB_HOST") or "localhost"
    port = os.getenv("PGPORT") or os.getenv("DB_PORT") or "5432"
    dbname = os.getenv("PGDATABASE") or os.getenv("DB_NAME") or "not set"
    user = os.getenv("PGUSER") or os.getenv("DB_USER") or "not set"

    def pretty(p: Path) -> str:
        try:
            return str(p.relative_to(REPO_ROOT))
        except Exception:
            return str(p)

    failed_line = pretty(failed_step) if failed_step else "n/a"
    steps_lines = "\n".join([f"- {pretty(s)}" for s in steps])

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
{steps_lines}

## Failure
- Failed step: {failed_line}
"""

    path = LOGS_DIR / "run_summary.md"
    path.write_text(content, encoding="utf-8")
    return path

# Runner
def run(script_path: Path) -> tuple[bool, float]:
    print(f"\n=== Running {script_path.relative_to(REPO_ROOT)} ===")
    start = time.time()

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    elapsed = time.time() - start

    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")

    if result.stderr:
        print("! stderr:\n", result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(
            f"!!! Stage failed: {script_path.name} (after {elapsed:.1f}s)",
            file=sys.stderr,
        )
        return False, elapsed

    print(f"=== Finished {script_path.name} ({elapsed:.1f}s) ===")
    return True, elapsed


def main():
    parser = argparse.ArgumentParser(description="Run ETL pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which stages would run without executing them",
    )
    args = parser.parse_args()

    print_environment_once()

    scripts_to_run = build_scripts()

    # Fail fast if loading to PG without DB config
    load_stage = SCRIPTS_DIR / "clean" / "load_indemnizatii_clean_to_pg.py"
    needs_db = load_stage in scripts_to_run
    if needs_db and not has_db_config():
        print(
            "!!! DB config missing (PGHOST/PGDATABASE/PGUSER or DB_HOST/DB_NAME/DB_USER). Aborting.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Dry-run mode
    if args.dry_run:
        print("\nDRY RUN MODE - No stages will be executed.\n")
        for s in scripts_to_run:
            print(f"Would run: {s.relative_to(REPO_ROOT)}")
        return

    steps_executed: list[Path] = []
    failed_step: Path | None = None
    status = "Success"
    overall_start = time.time()

    for s in scripts_to_run:
        steps_executed.append(s)
        ok, _ = run(s)
        if not ok:
            status = "Failed"
            failed_step = s
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
