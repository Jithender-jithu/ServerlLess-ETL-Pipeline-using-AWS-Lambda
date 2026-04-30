-- sql/schema.sql
-- RDS table definitions
CREATE TABLE IF NOT EXISTS api_records (
    id            SERIAL PRIMARY KEY,
    source_api    VARCHAR(100)   NOT NULL,
    record_id     VARCHAR(255)   UNIQUE NOT NULL,
    payload       JSONB,
    amount        NUMERIC(18, 4),
    category      VARCHAR(100),
    status        VARCHAR(50),
    event_date    DATE,
    ingested_at   TIMESTAMP      DEFAULT NOW(),
    processed_at  TIMESTAMP
);

-- sql/indexes.sql
CREATE INDEX idx_event_date    ON api_records (event_date);
CREATE INDEX idx_category      ON api_records (category);
CREATE INDEX idx_source_api    ON api_records (source_api);
CREATE INDEX idx_ingested_at   ON api_records (ingested_at DESC);
