CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE IF NOT EXISTS audit.anomaly_candidates (
    candidate_id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_table TEXT NOT NULL,
    record_pk TEXT NOT NULL,
    year INT,
    company_id TEXT,
    person_id TEXT,
    total_ron NUMERIC,
    anomaly_score NUMERIC NOT NULL,
    anomaly_reasons TEXT[] NOT NULL -- store multiple anomaly reasons
);

CREATE TABLE IF NOT EXISTS audit.anomaly_reviews (
    review_id BIGSERIAL PRIMARY KEY,
    candidate_id BIGINT NOT NULL REFERENCES audit.anomaly_candidates(candidate_id) ON DELETE CASCADE,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewer_type TEXT NOT NULL,
    model TEXT,
    prompt_sha256 TEXT NULL,
    label TEXT NOT NULL,
    confidence NUMERIC,
    rationale TEXT NOT NULL,
    raw_response_json jsonb
);

