-- Briefings executivos gerados pelo Briefing Agent
CREATE TABLE IF NOT EXISTS startup_briefings (
    id              SERIAL PRIMARY KEY,
    startup_id      INT NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    briefing_text   TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_briefings_startup_id ON startup_briefings (startup_id);

-- Validação de evidências (última validação por startup)
CREATE TABLE IF NOT EXISTS startup_validations (
    id              SERIAL PRIMARY KEY,
    startup_id      INT NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    is_valid        BOOLEAN NOT NULL DEFAULT FALSE,
    issues          TEXT[],
    source_count    INT DEFAULT 0,
    validated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_validations_startup_id ON startup_validations (startup_id);
