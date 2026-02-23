import os
import platform
import subprocess
import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

# Repo paths
REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
LOGS_DIR = REPO_ROOT / "logs"
PIPELINE_LOGS_DIR = LOGS_DIR / "pipeline"

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

# Logging
def setup_logging() -> tuple[logging.Logger, Path]:
    PIPELINE_LOGS_DIR.mkdir(exist_ok=True)

    prune_logs(keep_last=20)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_path = PIPELINE_LOGS_DIR / f"pipeline_{run_id}.log"

    logger = logging.getLogger("pipeline")
    logger.setLevel(logging.INFO)
    logger.propagate = False # avoid duplicate logs if root handlers exist

    if logger.handlers:
        logger.handlers.clear()
    
    formatter = logging.Formatter("%(asctime)sZ [%(levelname)s] %(message)s")
    formatter.converter = time.gmtime # force UTC timestamps

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)

    return logger, log_path

def pretty_path(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except Exception:
        return str(p)

def log_environment_once(logger: logging.Logger) -> None:
    host = os.getenv("PGHOST") or os.getenv("DB_HOST") or "localhost"
    port = os.getenv("PGPORT") or os.getenv("DB_PORT") or "5432"
    dbname = os.getenv("PGDATABASE") or os.getenv("DB_NAME") or "not set"
    user = os.getenv("PGUSER") or os.getenv("DB_USER") or "not set"

    logger.info("=== Runtime Environment ===")
    logger.info("Python version: %s", platform.python_version())
    logger.info("Executable    : %s", sys.executable)
    logger.info("OS            : %s %s", platform.system(), platform.release())
    logger.info("Database (resolved) host=%s port=%s db=%s user=%s", host, port, dbname, user)
    logger.info("===========================")

def prune_logs(*, keep_last: int = 20, pattern: str = "pipeline_*.log") -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    logs = sorted(PIPELINE_LOGS_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in logs[keep_last:]:
        try:
            old.unlink()
        except Exception:
            pass

def get_git_sha(logger: logging.Logger) -> str:
    try:
        p = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        return p.stdout.strip() if p.returncode == 0 else "n/a"
    except Exception as e:
        logger.warning("Could not resolve git SHA: %s", e)
        return "n/a"

# Summary report
def write_run_summary(
    *,
    status: str,
    duration_s: float,
    steps: list[Path],
    failed_step: Path | None,
    log_path: Path,
    sha: str,
) -> Path:
    LOGS_DIR.mkdir(exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    host = os.getenv("PGHOST") or os.getenv("DB_HOST") or "localhost"
    port = os.getenv("PGPORT") or os.getenv("DB_PORT") or "5432"
    dbname = os.getenv("PGDATABASE") or os.getenv("DB_NAME") or "not set"
    user = os.getenv("PGUSER") or os.getenv("DB_USER") or "not set"

    failed_line = pretty_path(failed_step) if failed_step else "n/a"
    steps_lines = "\n".join([f"- {pretty_path(s)}" for s in steps])

    content = f"""# Pipeline Run Summary

- Date (UTC): {ts}
- Status: {status}
- Duration: {duration_s:.1f}s
- Git SHA: {sha}
- Log file: {pretty_path(log_path)}

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

    path = PIPELINE_LOGS_DIR / "run_summary.md"
    path.write_text(content, encoding="utf-8")
    return path

# Runner
def run_stage(logger: logging.Logger, script_path: Path) -> tuple[bool, float]:
    stage_name = pretty_path(script_path)
    logger.info("=== Stage start: %s ===", stage_name)
    start = time.time()

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    elapsed = time.time() - start

    if result.stdout:
        logger.info("[stdout] %s\n%s", stage_name, result.stdout.rstrip())

    if result.stderr:
        logger.warning("[stderr] %s\n%s", stage_name, result.stderr.rstrip())

    if result.returncode != 0:
        logger.error("Stage failed: %s (exit=%s, elapsed=%.1fs)", stage_name, result.returncode, elapsed)
        return False, elapsed

    logger.info("=== Stage success: %s (elapsed=%.1fs) ===", stage_name, elapsed)
    return True, elapsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ETL pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which stages would run without executing them",
    )
    args = parser.parse_args()

    logger, log_path = setup_logging()
    sha = get_git_sha(logger)

    logger.info("Pipeline run start (git=%s)", sha)
    log_environment_once(logger)

    scripts_to_run = build_scripts()

    if sys.prefix == sys.base_prefix:
        logger.error("You are not running inside a virtualenv. Activate .venv first.")
        sys.exit(2)

    # Warn (don't print) if upload requested but missing creds
    upload_enabled = os.getenv("PIPELINE_UPLOAD") == "1"
    if upload_enabled and not has_aws_creds():
        logger.warning("PIPELINE_UPLOAD=1 but AWS credentials not found. Skipping upload stage.")

    # Fail fast if loading to PG without DB config
    load_stage = SCRIPTS_DIR / "clean" / "load_indemnizatii_clean_to_pg.py"
    needs_db = load_stage in scripts_to_run
    if needs_db and not has_db_config():
        logger.error(
            "!!! DB config missing (PGHOST/PGDATABASE/PGUSER or DB_HOST/DB_NAME/DB_USER). Aborting."
        )
        sys.exit(2)

    # Dry-run mode
    if args.dry_run:
        logger.info("DRY RUN MODE - No stages will be executed.")
        for s in scripts_to_run:
            logger.info("Would run: %s", pretty_path(s))
        logger.info("Pipeline run end (dry-run). Log: %s", pretty_path(log_path))

    steps_executed: list[Path] = []
    failed_step: Path | None = None
    status = "Success"
    overall_start = time.time()

    for s in scripts_to_run:
        steps_executed.append(s)
        ok, _ = run_stage(logger, s)
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
        log_path=log_path,
        sha=sha,
    )
    
    logger.info("Run summary written to: %s", pretty_path(summary_path))
    logger.info("Pipeline run end (status=%s, duration=%.1fs). Log: %s", status, duration, pretty_path(log_path))

    if status == "Failed":
        sys.exit(1)

    logger.info("\nAll stages complete.")

if __name__ == "__main__":
    main()
