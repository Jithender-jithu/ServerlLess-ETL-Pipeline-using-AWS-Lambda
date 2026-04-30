-- Performance indexes
CREATE INDEX idx_event_date    ON api_records (event_date);
CREATE INDEX idx_category      ON api_records (category);
CREATE INDEX idx_source_api    ON api_records (source_api);
CREATE INDEX idx_ingested_at   ON api_records (ingested_at DESC);
