import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str

def load_db_config_from_env() -> DbConfig:
    """
    Pulls Postgres connection details from env vars.
    Reuses existing set_pg_env.sh / .env workflow.
    """
    return DbConfig(
        host=os.environ.get("PHGOST", "localhost"),
        port=int(os.environ.get("PGPORT", "5432")),
        dbname=os.environ.get("PGDATABASE", "postgres"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGUSER", "postgres"),
    )

def safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None

def compute_anomaly_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds an anomaly score and reasons per row.
    Assumptions:
    - df has: record_pk, year, company_id, person_id, total_ron
    """
    out = df.copy()

    # Normalize numeric
    out["total_ron_num"] = out["total_ron"].apply(safe_float)

    # Score + reasons
    scores: List[float] = []
    reasons_list: List[List[str]] = []

    # Peer-group stats (z-score) by (year, company_id), fallback to year only
    # This catches "way higher than peers in same org/year"
    grp_cols = ["year", "company_id"]
    peer = out.groupby(grp_cols)["total_ron_num"].agg(["mean", "std"]).reset_index()
    out = out.merge(peer, on=grp_cols, how="left", suffixes=("", "_peer"))

    # Fallback stats by year if std is null/0
    peer_y = out.groupby(["year"])["total_ron_num"].agg(["mean", "std"]).rename(
        columns={"mean": "mean_y", "std": "std_y"}
    ).reset_index()
    out = out.merge(peer_y, on=["year"], how="left")

    def row_score(row: pd.Series) -> Tuple[float, List[str]]:
        score = 0.0
        reasons: List[str] = []

        total = row.get("total_ron_num", None)

        suma = safe_float(row.get("suma_clean"))
        variabila = safe_float(row.get("variabila_clean"))

        if suma is not None and suma < 0:
            score += 2.5
            reasons.append("suma_negative")

        if variabila is not None and variabila < 0:
            score += 2.0
            reasons.append("variabila_negative")

        if total is None:
            score += 3.0
            reasons.append("total_missing")
        else:
            if total < 0:
                score += 5.0
                reasons.append("total_negative")
            if total == 0:
                score += 1.5
                reasons.append("total_zero")
            if total > 2_000_000:
                score += 4.0
                reasons.append("total_implausibly_high")
        
        if not row.get("person_id"):
            score += 1.0
            reasons.append("person_id_missing")
        
        if not row.get("company_id"):
            score += 1.0
            reasons.append("company_id_missing")
        
        if total is not None:
            mean = row.get("mean", None)
            std = row.get("std", None)
            if mean is not None and std not in (None, 0.0) and pd.notna(std):
                z = abs((total - float(mean)) / float(std))
                if z >= 4:
                    score += 3.5
                    reasons.append(f"zscore_company_year_{z:.1f}")
                elif z >= 3:
                    score += 2.0
                    reasons.append(f"zscore_company_year_{z:.1f}")
            else:
                mean_y = row.get("mean_y", None)
                std_y = row.get("std_y", None)
                if mean_y is not None and std_y not in (None, 0.0) and pd.notna(std_y):
                    z = abs((total - float(mean_y)) / float(std_y))
                    if z >= 4:
                        score += 2.5
                        reasons.append(f"zscore_year_{z:.1f}")
                    elif z >= 3:
                        score += 1.5
                        reasons.append(f"zscore_year_{z:.1f}")
            
            return score, reasons
        
    for _, r in out.iterrows():
        s, rs = row_score(r)
        scores.append(s)
        reasons_list.append(rs)
    
    out["anomaly_score"] = scores
    out["anomaly_reasons"] = reasons_list

    return out

# -----------------------------
# “LLM-assisted” classifier (online or offline)
# -----------------------------

def build_llm_prompt(record: Dict[str, Any]) -> str:
    """
    Prompt that produces a consistent JSON output.
    """
    return f"""
You are a data quality reviewer for public compensation data.

Classify this flagged record into one label:
- LIKELY_ERROR
- NEEDS_REVIEW
- OK

Return STRICT JSON with keys:
label (string), confidence (number 0..1), rationale (string)

Record:
{json.dumps(record, ensure_ascii=False)}

Consider:
- negative/zero/implausible totals
- missing identifiers
- unusually high compared to peers (z-score reason may exist)
""".strip()

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def classify_with_llm_or_offline(record: Dict[str, Any]) -> Tuple[Dict[str, Any], str, str]:
    """
    Offline mode outputs a deterministic "good enough" classification.
    Returns: (result_json, reviewer_type, model_name)
    """
    prompt = build_llm_prompt(record)
    prompt_hash = sha256_text(prompt)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Offline heuristic: still "LLM-assisted workflow" structure,
        # but without external dependency.
        score = float(record.get("anomaly_score", 0.0))
        reasons = record.get("anomaly_reasons", [])

        if score >= 6 or any ("negative" in str(x) for x in reasons):
            result = {"label": "LIKELY_ERROR", "condifdence:": 0.75, "rationale": "High anomaly score / strong rule trigger"}
        elif score >= 3:
            result = {"label": "NEEDS_REVIEW", "confidence": 0.6, "rationale": "Moderate anomaly"}
        else:
            result = {"label": "OK", "confidence": 0.55, "rationale": "Weak signal; probably legitimate variation."}

        return {**result, "prompt_sha256": promp_hash, "raw_response_json": None}, "offline", "offline-heuristic"

    raise RuntimeError("OPENAI_API_KEY is set but online LLM call is not implemented yet.")

# -----------------------------
# DB I/O (read candidates, write queue + reviews)
# -----------------------------

def connect(db: DbConfig):
    return psycopg2.connect(
        host=db.host, port=db.port, dbname=db.dbname, user=db.user, password=db.password
    )

def read_source_table(conn, source_table: str, year: Optional[int], limit: int) -> pd.DataFrame:
    """
      - pk
      - person_id
      - company_id
      - total_plata
      - suma_clean
      - variabila_clean
      - an_raportare
    """
    where = "where 1=1"
    params: List[Any] = []

    if year is not None:
        where += " and an_raportare = %s"
        params.append(year)
    
    sql = f"""
      select
        cast(pk as text) as record_pk,
        cast(person_id as text) as person_id,
        cast(company_id as text) as company_id,

        -- totals
        total_plata as total_ron,
        suma_clean,
        variabila_clean,

        an_raportare as year
      from {source_table}
      {where}
      order by an_raportare desc, pk
      limit %s
    """
    params.append(limit)

    return pd.read_sql(sql, conn, params=params)

def write_candidates(conn, run_id: str, source_table: str, df: pd.DataFrame) -> List[int]:
    """
    Writes to audit.anomaly_candidates and returns candidate_id list.
    """
    rows = []
    for _, r in df.iterrows():
        rows.append((
            run_id,
            source_table,
            r["record_pk"],
            int(r["year"]) if pd.notna(r["year"]) else None,
            r.get("company_id"),
            r.get("person_id"),
            r.get("total_ron_num"),
            float(r["anomaly_score"]),
            r["anomaly_reasons"],
        ))

    insert_sql = """
      insert into audit.anomaly_candidates
        (run_id, source_table, record_pk, year, company_id, person_id, total_ron, anomaly_score, anomaly_reasons)
      values %s
      returning candidate_id
    """

    with conn.cursor() as cur:
        execute_values(cur, insert_sql, rows)
        ids = [x[0] for x in cur.fetchall()]
    conn.commit()
    return ids

def write_reviews(conn, candidate_ids: List[int], results: List[Dict[str, Any]], reviewer_type: str, model: str) -> None:
    """
    Writes LLM/offline decision with audit data.
    """
    rows = []
    for cid, res in zip(candidate_ids, results):
        rows.append((
            cid,
            reviewer_type,
            model,
            res["prompt_sha256"],
            float(res.get("confidence", 0.0)) if res.get("confidence") is not None else None,
            res["rationale"],
            json.dumps(res.get("raw_response_json")) if res.get("raw_response_json") is not None else None,
        ))
    
    sql = """
      insert into audit.anomaly_reviews
        (candidate_ids, reviewer_type, model, prompt_sha256, label, confidence, rationale, raw_response_json)
      values %s
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows)
    conn.commit()

# -----------------------------
# CLI entrypoint
# -----------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="e.g. analytics.fact_indemnizatii")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--min-score", type=float, default=3.0)
    parser.add_argument("--out", default="artifacts/anomaly_candidates.csv")
    parser.add_argument("--write-db", action="store_true", help="write candidates + reviews to Postgres audit schema")
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    db = load_db_config_from_env()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    with connect(db) as conn:
        df = read_source_table(conn, args.source, args.year, args.limit)
        print("[anomaly_review] read rows:", len(df))
        print("[anomaly_review] columns:", list(df.columns))

        if len(df) == 0:
            raise RuntimeError("Query returned 0 rows. Year filter or source table/schema likely wrong.")

        scored = compute_anomaly_score(df)
        flagged = scored[scored["anomaly_score"] >= args.min_score].copy()
        flagged = flagged.sort_values("anomaly_score", ascending=False)

        # Save CSV artifact for quick human review
        flagged.to_csv(args.out, index=False)
        print(f"[anomaly_review] run_id={run_id} flagged={len(flagged)} saved={args.out}")

        # Optional DB persistance + LLM/offline classification
        if args.write_db and len(flagged) > 0:
            candidate_ids = write_candidates(conn, run_id, args.source, flagged)

            results: List[Dict[str, Any]] = []
            reviewer_type = "offline"
            model = "offline-heuristic"

            for _, row in flagged.iterrows():
                record = {
                    "record_pk": row["record_pk"],
                    "year": row.get("year"),
                    "company_id": row.get("company_id"),
                    "person_id": row.get("person_id"),

                    "total_plata": row.get("total_ron_num"),
                    "suma_clean": safe_float(row.get("suma_clean")),
                    "variabila_clean": safe_float(row.get("variabila_clean")),

                    "anomaly_score": float(row["anomaly_score"]),
                    "anomaly_reasons": row["anomaly_reasons"],
                }
                res, reviewer_type, model = classify_with_llm_or_offline(record)
                results.append(res)
            
            write_reviews(conn, candidate_ids, results, reviewer_type, model)
            print(f"[anomaly_review] wrote {len(candidate_ids)} candidates + reviews to audit.* tables")


if __name__ == "__main__":
    main()
